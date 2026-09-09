#!/usr/bin/env python3
"""Optional helper for the documentation skill.

Dependency free (standard library only). It never generates prose.
It scaffolds directories, reports progress, suggests next work, detects
stale docs from Git history, and validates frontmatter, IDs, and links.

Usage:
    python3 scripts/docs.py <command> [options]

Commands:
    init    scaffold docs directories, config, and manifest
    status  show documentation progress from the manifest
    scan    summarize repository structure to aid mapping
    next    suggest the next module to work on (dependency order)
    stale   list docs whose sources changed since verified_commit
    verify  validate manifest, frontmatter, IDs, and internal links

Run `python3 scripts/docs.py <command> --help` for options.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

VALID_STATUSES = {
    "discovered",
    "researching",
    "researched",
    "documenting",
    "documented",
    "verifying",
    "verified",
    "needs-review",
}

RESTING_STATUSES = {
    "discovered",
    "researched",
    "documented",
    "verified",
    "needs-review",
}

MAP_KEY_RE = re.compile(r"^([A-Za-z0-9_.-]+)\s*:\s*(.*)$")
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _is_inline_map(content):
    m = MAP_KEY_RE.match(content)
    if not m:
        return None
    # Require either end of string, whitespace after colon, or quoted value.
    # Bare scalars containing colons without a space (URLs, key:{id}) stay scalars.
    _, _, after = content.partition(":")
    if after != "" and not after[:1].isspace() and after[:1] not in ("'", '"'):
        return None
    return m
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)#\s][^)\s]*)\)")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)


# ---------------------------------------------------------------------------
# Minimal YAML subset (read + write)
# ---------------------------------------------------------------------------
# Supports the subset used by docs.config.yml, manifest.yml, handoffs, and
# doc frontmatter: scalar keys, nested maps by indentation, lists of scalars,
# lists of maps, quoted strings, null, integers. Not a general YAML parser.


def _strip_comment(line):
    in_single = False
    in_double = False
    for i, ch in enumerate(line):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            return line[:i]
    return line


def _parse_scalar(raw):
    s = raw.strip()
    if s in ("", "~", "null", "Null", "NULL"):
        return None
    if (s.startswith('"') and s.endswith('"') and len(s) >= 2) or (
        s.startswith("'") and s.endswith("'") and len(s) >= 2
    ):
        return s[1:-1]
    if re.fullmatch(r"-?\d+", s):
        try:
            return int(s)
        except ValueError:
            return s
    if s in ("true", "True"):
        return True
    if s in ("false", "False"):
        return False
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(p) for p in inner.split(",")]
    return s


def _indent_of(line):
    return len(line) - len(line.lstrip(" "))


def _parse_block(lines, pos, indent):
    """Parse a mapping block. Returns (dict, next_pos)."""
    result = {}
    while pos < len(lines):
        raw = lines[pos]
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            pos += 1
            continue
        ind = _indent_of(raw)
        if ind < indent:
            break
        if ind > indent:
            # Unexpected deeper indent without a parent key; skip.
            pos += 1
            continue
        if stripped.startswith("- "):
            # List where a mapping was expected; let caller handle.
            break
        if ":" not in stripped:
            pos += 1
            continue
        key, _, rest = stripped.partition(":")
        key = key.strip()
        rest = _strip_comment(rest).strip() if rest is not None else ""
        # Rest may contain trailing comment already stripped.
        rest = rest.strip()
        nxt = pos + 1
        # Look ahead for nested content.
        while nxt < len(lines) and (
            not lines[nxt].strip() or lines[nxt].strip().startswith("#")
        ):
            nxt += 1
        if rest == "":
            if nxt < len(lines) and _indent_of(lines[nxt]) > indent:
                if lines[nxt].strip().startswith("- "):
                    lst, nxt2 = _parse_list(lines, nxt, _indent_of(lines[nxt]))
                    result[key] = lst
                    pos = nxt2
                else:
                    sub, nxt2 = _parse_block(lines, nxt, _indent_of(lines[nxt]))
                    result[key] = sub
                    pos = nxt2
            else:
                result[key] = None
                pos = nxt
        else:
            result[key] = _parse_scalar(rest)
            pos = nxt
    return result, pos


def _parse_list(lines, pos, indent):
    items = []
    while pos < len(lines):
        raw = lines[pos]
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            pos += 1
            continue
        ind = _indent_of(raw)
        if ind < indent:
            break
        if ind > indent:
            pos += 1
            continue
        if not stripped.startswith("- "):
            break
        content = stripped[2:].strip()
        content = _strip_comment(content).strip()
        if content == "":
            # Nested block under the dash.
            nxt = pos + 1
            while nxt < len(lines) and (
                not lines[nxt].strip() or lines[nxt].strip().startswith("#")
            ):
                nxt += 1
            if nxt < len(lines) and _indent_of(lines[nxt]) > indent:
                if lines[nxt].strip().startswith("- "):
                    lst, nxt2 = _parse_list(lines, nxt, _indent_of(lines[nxt]))
                    items.append(lst)
                    pos = nxt2
                else:
                    sub, nxt2 = _parse_block(lines, nxt, _indent_of(lines[nxt]))
                    items.append(sub)
                    pos = nxt2
            else:
                items.append(None)
                pos = nxt
        elif _is_inline_map(content) is not None and not content.startswith(("[", '"', "'")):
            # Inline map start: "- id: accounts" followed by more keys.
            m_inline = _is_inline_map(content)
            item = {m_inline.group(1).strip(): _parse_scalar(m_inline.group(2).strip())}
            pos += 1
            while pos < len(lines):
                r2 = lines[pos]
                s2 = r2.strip()
                if not s2 or s2.startswith("#"):
                    pos += 1
                    continue
                if _indent_of(r2) <= indent:
                    break
                if s2.startswith("- "):
                    break
                if ":" not in s2:
                    pos += 1
                    continue
                k2, _, v2 = s2.partition(":")
                v2 = _strip_comment(v2).strip()
                if v2 == "":
                    nxt = pos + 1
                    while nxt < len(lines) and (
                        not lines[nxt].strip() or lines[nxt].strip().startswith("#")
                    ):
                        nxt += 1
                    if nxt < len(lines) and _indent_of(lines[nxt]) > _indent_of(r2):
                        if lines[nxt].strip().startswith("- "):
                            lst, nxt2 = _parse_list(
                                lines, nxt, _indent_of(lines[nxt])
                            )
                            item[k2.strip()] = lst
                            pos = nxt2
                        else:
                            sub, nxt2 = _parse_block(
                                lines, nxt, _indent_of(lines[nxt])
                            )
                            item[k2.strip()] = sub
                            pos = nxt2
                    else:
                        item[k2.strip()] = None
                        pos = nxt
                else:
                    item[k2.strip()] = _parse_scalar(v2)
                    nxt = pos + 1
                    while nxt < len(lines) and (
                        not lines[nxt].strip() or lines[nxt].strip().startswith("#")
                    ):
                        nxt += 1
                    pos = nxt if nxt > pos + 1 else pos + 1
                    # Simpler: pos already advanced; fix double counting below.
                    # Recompute: we consumed lines[pos]; move one step.
                    # (Blank skipping already handled.)
                    continue
            items.append(item)
        else:
            items.append(_parse_scalar(content))
            pos += 1
    return items, pos


def parse_simple_yaml(text):
    lines = text.splitlines()
    # Skip leading --- markers if present.
    if lines and lines[0].strip() == "---":
        lines = lines[1:]
    data, _ = _parse_block(lines, 0, 0)
    return data


def _fmt_scalar(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    s = str(value)
    if s == "":
        return '""'
    if re.fullmatch(r"[A-Za-z0-9_./-]+", s):
        return s
    escaped = s.replace('"', '\\"')
    return '"%s"' % escaped


def dump_manifest(modules, path):
    lines = [
        "# Module manifest. Statuses: discovered, researching, researched,",
        "# documenting, documented, verifying, verified, needs-review.",
        "modules:",
    ]
    if not modules:
        lines.append("  []")
    for m in modules:
        lines.append("  - id: %s" % _fmt_scalar(m.get("id", "")))
        lines.append("    title: %s" % _fmt_scalar(m.get("title", "")))
        lines.append("    status: %s" % _fmt_scalar(m.get("status", "discovered")))
        lines.append("    paths:")
        for p in m.get("paths", []) or []:
            lines.append("      - %s" % _fmt_scalar(p))
        lines.append("    depends_on:")
        for d in m.get("depends_on", []) or []:
            lines.append("      - %s" % _fmt_scalar(d))
        lines.append("    doc: %s" % _fmt_scalar(m.get("doc", "")))
        lines.append("    research: %s" % _fmt_scalar(m.get("research", "")))
        lines.append(
            "    verified_commit: %s" % _fmt_scalar(m.get("verified_commit"))
        )
        notes = m.get("notes", "")
        lines.append("    notes: %s" % _fmt_scalar(notes if notes else ""))
        lines.append("")
    path.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Config and manifest loading
# ---------------------------------------------------------------------------


def find_config(explicit):
    if explicit:
        return Path(explicit)
    default = Path("docs.config.yml")
    if default.exists():
        return default
    return default


def load_config(path):
    data = {}
    if path and Path(path).exists():
        try:
            data = parse_simple_yaml(Path(path).read_text(encoding="utf-8")) or {}
        except Exception as exc:
            print("warning: could not parse config %s: %s" % (path, exc))
            data = {}
    docs_dir = data.get("docs_dir", "docs/internal")
    research_dir = data.get("research_dir", os.path.join(str(docs_dir), "research"))
    ignore = data.get("ignore", []) or []
    entrypoints = data.get("entrypoints", []) or []
    return {
        "docs_dir": Path(docs_dir),
        "research_dir": Path(research_dir),
        "ignore": [str(x) for x in ignore],
        "entrypoints": [str(x) for x in entrypoints],
        "raw": data,
        "path": Path(path) if path else Path("docs.config.yml"),
    }


def manifest_path_for(cfg):
    return cfg["docs_dir"] / "manifest.yml"


def load_manifest(mpath):
    if not mpath.exists():
        return []
    try:
        data = parse_simple_yaml(mpath.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        print("warning: could not parse manifest %s: %s" % (mpath, exc))
        return []
    modules = data.get("modules", []) or []
    if isinstance(modules, dict):
        return []
    return [m for m in modules if isinstance(m, dict)]


def read_frontmatter(md_path):
    try:
        text = Path(md_path).read_text(encoding="utf-8")
    except OSError:
        return None, "unreadable"
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, "missing"
    try:
        data = parse_simple_yaml(m.group(1)) or {}
        return data, "ok"
    except Exception as exc:
        return None, "parse-error: %s" % exc


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_init(args):
    cfg = load_config(find_config(config_arg(args)))
    if args.docs_dir:
        cfg["docs_dir"] = Path(args.docs_dir)
        cfg["research_dir"] = cfg["docs_dir"] / "research"
    docs_dir = cfg["docs_dir"]
    subdirs = ["modules", "research", "handoffs", "workflows", "qa"]
    created = []
    for sub in subdirs:
        d = docs_dir / sub
        d.mkdir(parents=True, exist_ok=True)
        created.append(str(d))
    mpath = manifest_path_for(cfg)
    if not mpath.exists() or args.force:
        mpath.parent.mkdir(parents=True, exist_ok=True)
        dump_manifest([], mpath)
        created.append(str(mpath))
    cpath = cfg["path"]
    if (not cpath.exists() or args.force) and args.write_config:
        skill_config = find_skill_config_template()
        if skill_config:
            cpath.write_text(skill_config, encoding="utf-8")
            created.append(str(cpath))
    # Minimal index so the doc set has an entry point.
    index = docs_dir / "index.md"
    if not index.exists() or args.force:
        index.write_text(
            "# Documentation index\n\n"
            "Doc set entry point. List each module, its audience, "
            "and its verification state here as modules are verified.\n",
            encoding="utf-8",
        )
        created.append(str(index))
    print("initialized documentation directories under %s" % docs_dir)
    for c in created:
        print("  %s" % c)
    return 0


def find_skill_config_template():
    here = Path(__file__).resolve()
    candidates = [
        here.parent.parent / "templates" / "docs.config.yml",
        here.parent / "docs.config.yml",
    ]
    for c in candidates:
        if c.exists():
            return c.read_text(encoding="utf-8")
    return None


def _doc_exists(repo_root, docs_dir, rel):
    if not rel:
        return False
    p = Path(rel)
    if not p.is_absolute():
        # Try relative to docs dir, then repo root.
        if (docs_dir / p).exists():
            return True
        if (repo_root / p).exists():
            return True
        return False
    return p.exists()


def cmd_status(args):
    cfg = load_config(find_config(config_arg(args)))
    mpath = manifest_path_for(cfg)
    modules = load_manifest(mpath)
    repo_root = Path(".")
    counts = {}
    for m in modules:
        counts[m.get("status", "?")] = counts.get(m.get("status", "?"), 0) + 1
    payload = {
        "config": str(cfg["path"]) if cfg["path"].exists() else None,
        "docs_dir": str(cfg["docs_dir"]),
        "manifest": str(mpath) if mpath.exists() else None,
        "total": len(modules),
        "by_status": counts,
        "modules": [],
    }
    for m in modules:
        entry = {
            "id": m.get("id"),
            "status": m.get("status"),
            "depends_on": m.get("depends_on", []) or [],
            "doc": m.get("doc"),
            "doc_exists": _doc_exists(repo_root, cfg["docs_dir"], m.get("doc")),
            "research_exists": _doc_exists(
                repo_root, cfg["docs_dir"], m.get("research")
            ),
            "verified_commit": m.get("verified_commit"),
        }
        payload["modules"].append(entry)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print("docs_dir: %s" % cfg["docs_dir"])
        print("manifest: %s" % (mpath if mpath.exists() else "(missing)"))
        print("total modules: %d" % len(modules))
        if counts:
            for s in sorted(counts):
                print("  %-12s %d" % (s, counts[s]))
        else:
            print("  (no modules recorded)")
        for e in payload["modules"]:
            flag = "doc:yes" if e["doc_exists"] else "doc:no"
            print("  - %-24s %-12s %s" % (e["id"], e["status"], flag))
        transient = [e for e in payload["modules"] if e["status"] not in RESTING_STATUSES]
        if transient:
            print("warning: transient states present (resume or reset them):")
            for e in transient:
                print("  - %s is %s" % (e["id"], e["status"]))
    return 0


def _ignored(path_str, ignore_list):
    for pat in ignore_list:
        pat = pat.strip().strip("/")
        if not pat:
            continue
        if path_str == pat or path_str.startswith(pat + "/"):
            return True
        # Simple glob support for patterns with *.
        if "*" in pat:
            import fnmatch

            if fnmatch.fnmatch(path_str, pat) or fnmatch.fnmatch(
                os.path.basename(path_str), pat
            ):
                return True
    return False


def cmd_scan(args):
    cfg = load_config(find_config(config_arg(args)))
    root = Path(args.root or ".")
    ignore = list(cfg["ignore"]) + (args.ignore or [])
    total_files = 0
    by_ext = {}
    top_dirs = {}
    candidates = []
    ENTRY_HINTS = {
        "main.py", "app.py", "server.py", "manage.py", "cli.py",
        "package.json", "go.mod", "Cargo.toml", "pyproject.toml",
        "Dockerfile", "docker-compose.yml", "compose.yaml",
    }
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir == ".":
            rel_dir = ""
        # Prune ignored dirs.
        dirnames[:] = [
            d
            for d in dirnames
            if not _ignored(
                os.path.join(rel_dir, d) if rel_dir else d, ignore
            )
            and not d.startswith(".git")
        ]
        if _ignored(rel_dir, ignore) and rel_dir:
            dirnames[:] = []
            continue
        for fn in filenames:
            rel = os.path.join(rel_dir, fn) if rel_dir else fn
            if _ignored(rel, ignore):
                continue
            total_files += 1
            ext = os.path.splitext(fn)[1].lower() or "(none)"
            by_ext[ext] = by_ext.get(ext, 0) + 1
            top = rel.split(os.sep)[0] if os.sep in rel else "(root)"
            top_dirs[top] = top_dirs.get(top, 0) + 1
            if fn in ENTRY_HINTS:
                candidates.append(rel)
    payload = {
        "root": str(root),
        "total_files": total_files,
        "by_extension": dict(sorted(by_ext.items(), key=lambda kv: -kv[1])[:20]),
        "top_dirs": dict(sorted(top_dirs.items(), key=lambda kv: -kv[1])[:20]),
        "entrypoint_hints": sorted(candidates)[:30],
        "configured_entrypoints": cfg["entrypoints"],
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print("root: %s  files: %d" % (root, total_files))
        print("top directories:")
        for k, v in payload["top_dirs"].items():
            print("  %-28s %d" % (k, v))
        print("top extensions:")
        for k, v in payload["by_extension"].items():
            print("  %-12s %d" % (k, v))
        print("entrypoint hints:")
        for c in payload["entrypoint_hints"] or ["(none found)"]:
            print("  %s" % c)
    return 0


def cmd_next(args):
    cfg = load_config(find_config(config_arg(args)))
    modules = load_manifest(manifest_path_for(cfg))
    by_id = {m.get("id"): m for m in modules}
    verified = {
        m.get("id") for m in modules if m.get("status") == "verified"
    }
    researched = {
        m.get("id") for m in modules if m.get("status") in ("researched", "documented", "verifying", "verified")
    }
    # Priority: needs-review first, then discovered/researching in dep order.
    def ready(m, done):
        deps = m.get("depends_on", []) or []
        return all(d in done for d in deps)

    needs_review = [m for m in modules if m.get("status") == "needs-review"]
    for m in needs_review:
        if ready(m, verified | (set(by_id) - {m.get("id")})):
            return _emit_next(m, "needs-review with defects to recheck", args)

    # Investigation order: discovered/researching whose deps are researched.
    for status in ("discovered", "researching", "researched"):
        for m in modules:
            if m.get("status") == status and ready(m, researched | verified):
                # Skip modules blocked on unverified deps only for later phases;
                # for investigation, researched deps suffice.
                return _emit_next(m, "ready for investigation (deps researched)", args)
    # Writing order: researched -> documenting.
    for m in modules:
        if m.get("status") == "researched":
            return _emit_next(m, "ready to document", args)
    for m in modules:
        if m.get("status") in ("documented", "documenting"):
            return _emit_next(m, "ready to verify", args)
    for m in modules:
        if m.get("status") == "verifying":
            return _emit_next(m, "finish verification pass", args)
    # Fallback: anything not verified whose deps are verified.
    for m in modules:
        if m.get("status") != "verified" and ready(m, verified):
            return _emit_next(m, "unblocks dependents", args)
    # Last resort: first non-verified.
    for m in modules:
        if m.get("status") != "verified":
            missing = [
                d
                for d in (m.get("depends_on", []) or [])
                if d not in verified
            ]
            return _emit_next(
                m, "blocked on: %s" % (", ".join(missing) or "none"), args
            )
    if args.json:
        print(json.dumps({"next": None, "reason": "all modules verified"}))
    else:
        print("all modules verified; consider architecture, workflows, and QA passes")
    return 0


def _emit_next(m, reason, args):
    if args.json:
        print(
            json.dumps(
                {
                    "next": m.get("id"),
                    "status": m.get("status"),
                    "paths": m.get("paths", []) or [],
                    "depends_on": m.get("depends_on", []) or [],
                    "doc": m.get("doc"),
                    "research": m.get("research"),
                    "reason": reason,
                },
                indent=2,
            )
        )
    else:
        print("next: %s (%s)" % (m.get("id"), m.get("status")))
        print("  reason: %s" % reason)
        print("  paths: %s" % ", ".join(m.get("paths", []) or []))
        print("  depends_on: %s" % ", ".join(m.get("depends_on", []) or []))
    return 0


def _git(args_list, cwd):
    try:
        out = subprocess.run(
            ["git"] + args_list,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return None, str(exc)
    if out.returncode != 0:
        return None, out.stderr.strip()
    return out.stdout.strip(), None


def cmd_stale(args):
    cfg = load_config(find_config(config_arg(args)))
    repo = Path(args.repo or ".")
    modules = load_manifest(manifest_path_for(cfg))
    if not (repo / ".git").exists():
        print("warning: no .git directory at %s; cannot compute staleness" % repo)
        return 1
    head, err = _git(["rev-parse", "HEAD"], repo)
    if head is None:
        print("error: cannot read HEAD: %s" % err)
        return 1
    results = []
    for m in modules:
        sha = m.get("verified_commit")
        if m.get("status") != "verified" or not sha:
            continue
        valid, verr = _git(["cat-file", "-e", str(sha)], repo)
        _ = valid
        paths = m.get("paths", []) or []
        if not paths:
            continue
        out, err = _git(["log", "--oneline", "%s..HEAD" % sha, "--"] + paths, repo)
        if out is None:
            results.append(
                {"id": m.get("id"), "error": err, "changed": None, "commits": []}
            )
        elif out.strip():
            commits = out.strip().splitlines()
            results.append(
                {
                    "id": m.get("id"),
                    "verified_commit": sha,
                    "changed": True,
                    "commits": commits[:10],
                    "count": len(commits),
                }
            )
        else:
            results.append(
                {
                    "id": m.get("id"),
                    "verified_commit": sha,
                    "changed": False,
                    "commits": [],
                    "count": 0,
                }
            )
    stale_list = [r for r in results if r.get("changed")]
    if args.json:
        print(json.dumps({"head": head, "stale": stale_list, "checked": results}, indent=2))
    else:
        print("HEAD: %s" % head)
        if not results:
            print("(no verified modules with commits to check)")
        for r in results:
            if r.get("changed"):
                print("  STALE %-22s %d commit(s) since %s" % (r["id"], r["count"], r["verified_commit"]))
                for c in r["commits"]:
                    print("      %s" % c)
            elif r.get("changed") is False:
                print("  fresh %-22s (since %s)" % (r["id"], r["verified_commit"]))
            else:
                print("  error %-22s %s" % (r.get("id"), r.get("error")))
    return 0


def cmd_verify(args):
    cfg = load_config(find_config(config_arg(args)))
    repo = Path(args.repo or ".")
    docs_dir = cfg["docs_dir"]
    mpath = manifest_path_for(cfg)
    modules = load_manifest(mpath)
    errors = []
    warnings = []

    # Manifest checks.
    seen = set()
    for m in modules:
        mid = m.get("id")
        if not mid:
            errors.append("manifest: module missing id")
            continue
        if not ID_RE.match(str(mid)):
            errors.append("manifest: bad id '%s' (use lowercase slugs)" % mid)
        if mid in seen:
            errors.append("manifest: duplicate id '%s'" % mid)
        seen.add(mid)
        if m.get("status") not in VALID_STATUSES:
            errors.append(
                "manifest: module '%s' has unknown status '%s'" % (mid, m.get("status"))
            )
        for dep in m.get("depends_on", []) or []:
            if dep not in seen and dep not in [x.get("id") for x in modules]:
                errors.append("manifest: module '%s' depends on unknown '%s'" % (mid, dep))
            if dep == mid:
                errors.append("manifest: module '%s' depends on itself" % mid)

    # Frontmatter checks for existing canonical docs.
    doc_files = []
    for m in modules:
        for key in ("doc", "research"):
            _ = key
        rel = m.get("doc")
        if not rel:
            continue
        p = docs_dir / rel if not os.path.isabs(str(rel)) else Path(rel)
        alt = repo / rel if not p.exists() else None
        target = p if p.exists() else (alt if alt is not None and alt.exists() else p)
        doc_files.append((m.get("id"), target))
    # Also check architecture, index, workflows, qa files present on disk.
    extra_dirs = [docs_dir / "workflows", docs_dir / "qa"]
    extra_files = []
    for d in extra_dirs + [docs_dir]:
        if d.exists():
            for f in sorted(d.glob("*.md")):
                if (f.name == "index.md" and d == docs_dir) or d.name in (
                    "workflows",
                    "qa",
                ):
                    extra_files.append((None, f))
    if (docs_dir / "architecture.md").exists():
        extra_files.append((None, docs_dir / "architecture.md"))

    checked = []
    for mid, path in doc_files + extra_files:
        if not path.exists():
            if mid:
                warnings.append("manifest: doc for '%s' missing at %s" % (mid, path))
            continue
        is_index = path.name == "index.md" and path.parent.resolve() == docs_dir.resolve() if docs_dir.exists() else path.name == "index.md"
        data, state = read_frontmatter(path)
        checked.append(str(path))
        if is_index and (state == "missing" or data is None):
            # Entry point may omit frontmatter; links are still checked below.
            continue
        if is_index:
            # Entry point with frontmatter is allowed but not validated strictly.
            continue
        if state == "missing":
            errors.append("frontmatter: %s has no frontmatter block" % path)
            continue
        if state.startswith("parse-error"):
            errors.append("frontmatter: %s %s" % (path, state))
            continue
        for field in ("title", "area", "audience", "status", "source"):
            if field not in data or data[field] in (None, ""):
                errors.append("frontmatter: %s missing '%s'" % (path, field))
        audience = data.get("audience")
        if audience is not None and not isinstance(audience, list):
            errors.append("frontmatter: %s audience must be a list" % path)
        fstatus = data.get("status")
        if fstatus is not None and fstatus not in VALID_STATUSES | {"draft"}:
            warnings.append("frontmatter: %s unusual status '%s'" % (path, fstatus))
        area = data.get("area")
        if mid and area != mid and str(path).endswith(".md"):
            # Module docs must match; workflow/qa/architecture checked loosely.
            if str(docs_dir / "modules") in str(path) or "/modules/" in str(path):
                errors.append(
                    "frontmatter: %s area '%s' does not match module id '%s'"
                    % (path, area, mid)
                )
        if area and area not in seen and area not in ("architecture", "workflows"):
            # QA files use module ids; flag unknown areas.
            warnings.append("frontmatter: %s area '%s' not in manifest" % (path, area))
        vc = data.get("verified_commit")
        if fstatus == "verified" and not vc:
            errors.append("frontmatter: %s marked verified without verified_commit" % path)
        if vc:
            out, err = _git(["cat-file", "-e", str(vc)], repo)
            if out is None and (repo / ".git").exists():
                warnings.append(
                    "frontmatter: %s verified_commit '%s' not found: %s" % (path, vc, err)
                )

    # Link checks.
    link_errors = []
    md_files = [Path(c) for c in checked]
    for md in md_files:
        try:
            text = md.read_text(encoding="utf-8")
        except OSError:
            continue
        # Strip frontmatter so it is not scanned.
        text = FRONTMATTER_RE.sub("", text, count=1)
        for match in LINK_RE.finditer(text):
            target = match.group(1).strip()
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue  # external URL or mailto
            if target.startswith("#"):
                continue  # anchor
            if target.startswith("http"):
                continue
            resolved = (md.parent / target.split("#")[0]).resolve()
            # Allow links outside docs dir only if they point at repo files.
            try:
                base = (repo.resolve(), docs_dir.resolve())
            except OSError:
                base = None
            _ = base
            if not resolved.exists():
                # Also try relative to repo root.
                alt = (repo / target.split("#")[0])
                if not alt.exists():
                    link_errors.append("%s: broken link to '%s'" % (md, target))
    for le in link_errors:
        errors.append("links: %s" % le)

    # Manifest/doc status agreement.
    for m in modules:
        rel = m.get("doc")
        if not rel:
            continue
        p = docs_dir / rel if not os.path.isabs(str(rel)) else Path(rel)
        if not p.exists() and not (repo / rel).exists():
            continue
        target = p if p.exists() else (repo / rel)
        data, state = read_frontmatter(target)
        if state != "ok" or not data:
            continue
        if data.get("status") != m.get("status") and not args.lenient_status:
            warnings.append(
                "status: module '%s' manifest says '%s' but doc says '%s'"
                % (m.get("id"), m.get("status"), data.get("status"))
            )

    payload = {
        "manifest": str(mpath) if mpath.exists() else None,
        "modules": len(modules),
        "files_checked": checked,
        "errors": errors,
        "warnings": warnings,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print("checked %d file(s), %d module(s)" % (len(checked), len(modules)))
        for w in warnings:
            print("warning: %s" % w)
        for e in errors:
            print("error: %s" % e)
        if not errors and not warnings:
            print("ok: manifest, frontmatter, and links look consistent")
    if args.strict and warnings:
        return 1
    return 1 if errors else 0


def build_parser():
    p = argparse.ArgumentParser(
        prog="docs.py",
        description="Optional helper for the documentation skill (stdlib only).",
    )
    p.add_argument(
        "--config", dest="config_global", default=None,
        help="path to docs.config.yml (may also be given after the command)",
    )
    sub = p.add_subparsers(dest="command", required=True)

    a = sub.add_parser("init", help="scaffold docs directories and manifest")
    a.add_argument("--config", default=None, help="path to docs.config.yml")
    a.add_argument("--docs-dir", default=None)
    a.add_argument("--force", action="store_true")
    a.add_argument(
        "--write-config",
        action="store_true",
        help="also write docs.config.yml from the skill template when missing",
    )
    a.set_defaults(func=cmd_init)

    a = sub.add_parser("status", help="show progress from the manifest")
    a.add_argument("--config", default=None, help="path to docs.config.yml")
    a.add_argument("--json", action="store_true")
    a.set_defaults(func=cmd_status)

    a = sub.add_parser("scan", help="summarize repo structure for mapping")
    a.add_argument("--config", default=None, help="path to docs.config.yml")
    a.add_argument("--root", default=".")
    a.add_argument("--ignore", action="append", default=[])
    a.add_argument("--json", action="store_true")
    a.set_defaults(func=cmd_scan)

    a = sub.add_parser("next", help="suggest next module in dependency order")
    a.add_argument("--config", default=None, help="path to docs.config.yml")
    a.add_argument("--json", action="store_true")
    a.set_defaults(func=cmd_next)

    a = sub.add_parser("stale", help="list docs changed since verified_commit")
    a.add_argument("--config", default=None, help="path to docs.config.yml")
    a.add_argument("--repo", default=".")
    a.add_argument("--json", action="store_true")
    a.set_defaults(func=cmd_stale)

    a = sub.add_parser(
        "verify", help="validate manifest, frontmatter, IDs, and links"
    )
    a.add_argument("--config", default=None, help="path to docs.config.yml")
    a.add_argument("--repo", default=".")
    a.add_argument("--strict", action="store_true")
    a.add_argument(
        "--lenient-status",
        action="store_true",
        help="do not warn when manifest and doc statuses differ",
    )
    a.add_argument("--json", action="store_true")
    a.set_defaults(func=cmd_verify)

    return p


def config_arg(args):
    return getattr(args, "config", None) or getattr(args, "config_global", None)


def resolve_config_arg(args):
    return config_arg(args)


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    # --config is global; subparser defaults keep it.
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
