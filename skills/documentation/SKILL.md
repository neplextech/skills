---
name: documentation
description: Study a software repository in bounded chunks and produce verified Markdown documentation for engineering onboarding, QA, architecture, and troubleshooting. Use when asked to document a codebase, explain how a system works, audit existing docs, or build a technical handbook. Triggers on requests like "document this repo", "explain the architecture", "onboard me to this codebase", "write internal docs", or "what does this module do".
disable-model-invocation: true
---

# Codebase documentation

Study the repository as evidence. Explain what the system does in maintainable Markdown.

## Core principle

The source code is evidence. The documentation explains what the system does.

Ground every behavior claim in observable evidence: implementation, schemas, migrations, tests, API definitions, config, validation, permission checks, events, workers, or frontend behavior. Never invent behavior because it seems reasonable. If a behavior cannot be established, write it down explicitly:

```md
> Needs verification: It is unclear whether retries are bounded.
```

## Workflow overview

Run these phases in order. Each phase has a reference file with the full procedure.

```text
0. repository discovery      -> references/repository-mapping.md
1. domain and module mapping -> references/repository-mapping.md
2. documentation plan        -> references/methodology.md
3. bounded investigations    -> references/domain-investigation.md
4. documentation writing     -> references/module-documentation.md
5. independent verification  -> references/verification.md
6. architecture synthesis    -> references/architecture-documentation.md
7. cross-domain workflows    -> references/architecture-documentation.md
8. QA documentation          -> references/qa-documentation.md
9. final review              -> references/methodology.md
```

Supporting references:

- `references/methodology.md`: phase definitions, entry and exit criteria, resumability.
- `references/writing-style.md`: style contract. Applies to all canonical docs.
- `references/swarm-strategy.md`: how to parallelize with subagents, or run sequentially without them.
- `references/verification.md`: how to falsify docs before marking them verified.

Templates live in `templates/`. An optional helper lives in `scripts/docs.py`.

## Operating rules

1. Work in bounded chunks. Never attempt to document a large repository in one pass. One domain per investigation.
2. Separate research from canonical docs. Research files hold evidence, file paths, uncertainties, and hypotheses. Canonical docs hold only what a human needs. See `references/domain-investigation.md`.
3. Separate observation from hypothesis during research. Every research file uses `Observed`, `Unresolved`, and `Hypotheses` sections. Hypotheses never become canonical facts until verified. See `templates/research.md`.
4. Verify independently. A document is done only after a reviewer who did not write it checks it against the repository and tries to falsify it. See `references/verification.md`.
5. Document behavior, not code line by line. Describe observable system behavior. Mention implementation only when it matters for architecture, security, failure handling, consistency, performance, operations, extension, or debugging.
6. Keep state on disk, not in memory. Track progress in a module manifest so the effort survives long runs and restarts. See `references/methodology.md`.
7. Prefer logical domains over folders. A business domain can span backend, frontend, schema, queues, tests, and integrations. Map domains first, then assign work. See `references/repository-mapping.md`.

## Subagents

Subagent execution is first class but optional.

- If the runtime supports subagents, use them per `references/swarm-strategy.md`. Minimum useful roles: repository mapper, domain investigator, documentation writer, verification reviewer, cross-domain integration investigator, QA analyst.
- If subagents are unavailable, run the same phases sequentially. The workflow must produce the same artifacts either way.
- Do not hardcode any provider API. Describe task scope, inputs, and expected handoff format; let the runtime handle dispatch.
- Subagents communicate through files and compact structured handoffs (`templates/handoff.yml`), not conversational memory.

## Output layout

Default layout (overridable by project config):

```text
docs/internal/
  manifest.yml          # module tracking state
  index.md              # doc set entry point
  architecture.md       # system architecture
  workflows/            # cross-domain workflows
  modules/<id>.md       # one file per domain
  qa/<id>.md            # one QA file per domain or workflow
  research/<id>.md      # investigation notes (not canonical)
  handoffs/<id>.yml     # structured subagent handoffs
```

Research files are never published as canonical docs. They stay in `research/` for maintainers and reviewers.

## Configuration and helper

The skill works with sensible defaults and no tooling.

- Optional project config: `templates/docs.config.yml`. Copy it to the target repository root as `docs.config.yml` and adjust `docs_dir`, `ignore`, and `entrypoints`. The skill works without it.
- Optional module manifest: `templates/manifest.yml`. Copy it to `<docs_dir>/manifest.yml` once domains are mapped.
- Optional helper `scripts/docs.py` (Python 3 standard library only) can scaffold directories, report progress, suggest next work, detect stale docs from Git history, and validate frontmatter, module IDs, and internal links. It never generates prose. Run `python3 scripts/docs.py --help` for commands. Every command also has a manual fallback described in `references/methodology.md`.

## Quality bar for canonical docs

- Correct, searchable, predictable structure, short explanations, project terminology, links between related docs.
- No marketing language, no filler, no exaggerated claims, no code narration that does not help a human.
- No em dashes in prose. Use commas, colons, or parentheses instead.
- Sentence case headings. Minimal bold. No decorative emoji.
- Mermaid only when a diagram says something more clearly than prose. Keep diagrams small.
- Every canonical doc ends with source references and states its verification state in frontmatter.

Start at `references/methodology.md` unless the request is narrow (for example "document only the auth module"), in which case start at `references/domain-investigation.md` with that module as the bounded scope. Read `references/writing-style.md` before writing any canonical doc, and `references/swarm-strategy.md` before dispatching any subagent.
