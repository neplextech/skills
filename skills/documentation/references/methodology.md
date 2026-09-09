# Methodology

This file defines the phase sequence, entry and exit criteria, and resumability contract. Read it first, then follow the phase reference for the phase you are in.

## Phase map

| Phase | Name | Reference | Produces |
| --- | --- | --- | --- |
| 0 | Repository discovery | `repository-mapping.md` | Repo sketch: languages, entrypoints, datastores, queues, integrations |
| 1 | Domain and module mapping | `repository-mapping.md` | `manifest.yml` with `discovered` modules and dependency hints |
| 2 | Documentation plan | This file | Human reviewable plan: scope, order, audiences, output paths |
| 3 | Bounded investigations | `domain-investigation.md` | `research/<id>.md` plus `handoffs/<id>.yml` per domain |
| 4 | Documentation writing | `module-documentation.md` | `modules/<id>.md` drafts with frontmatter `status: documented` |
| 5 | Independent verification | `verification.md` | Reviewed docs with frontmatter `status: verified` or `needs-review` |
| 6 | Architecture synthesis | `architecture-documentation.md` | `architecture.md` |
| 7 | Cross-domain workflows | `architecture-documentation.md` | `workflows/<name>.md` files |
| 8 | QA documentation | `qa-documentation.md` | `qa/<id>.md` files |
| 9 | Final review | This file | `index.md`, validated links and manifest, clean status |

Phases 6 to 8 require at least two verified modules, or one verified module plus the repo sketch, before they start. Do not synthesize architecture from unverified drafts.

## Phase 0 and 1: discover and map

Follow `references/repository-mapping.md`. Do not write module docs yet. The output is a manifest with one entry per logical domain, not per folder.

## Phase 2: documentation plan

Write a short plan and stop for human review on large repositories (roughly: more than 6 modules, or any unclear domain boundary). The plan fits on one page:

1. Goal and audiences (engineering onboarding, QA, architecture reference, troubleshooting, handbook).
2. Output directory and config file location.
3. Module list with one line of scope each, in dependency order.
4. Explicit non-goals (what will not be documented).
5. Verification rule (who reviews, independent reviewer requirement).
6. First batch of 2 to 3 modules to investigate.

If the request is narrow ("document module X"), skip the stop and record the reduced scope in the plan file or chat reply.

## Phase 3: bounded investigations

Follow `references/domain-investigation.md`. One investigator per domain. Scope is narrow: the listed paths plus named boundary interfaces. Overlap at boundaries is expected; contradictions become verification tasks, not silent choices.

Exit criterion per module: `research/<id>.md` exists with `Observed`, `Unresolved`, and `Hypotheses` sections, plus a `handoffs/<id>.yml` with entities, states, writes, events, side effects, related modules, and uncertainties. Manifest status moves from `discovered` to `researched` (via `researching` while work is active).

## Phase 4: documentation writing

Follow `references/module-documentation.md` and `references/writing-style.md`. The writer reads only the research file, the handoff, and spot checked sources. The writer does not re-investigate the whole repo.

Exit criterion: `modules/<id>.md` matches the module contract, passes style checks, and carries `status: documented` frontmatter. Manifest status becomes `documented` (via `documenting` while active).

## Phase 5: independent verification

Follow `references/verification.md`. The reviewer must differ from the writer. Single agent setups satisfy this by re-reading sources in a fresh pass with falsification checks, but must record that the review was self performed in frontmatter or the manifest notes.

Exit criterion: each claim is supported, contradicted claims are fixed or marked `> Needs verification`, and frontmatter is set to `status: verified` with `verified_commit` set to the reviewed Git SHA. Failures move the module to `needs-review` with a note. Manifest status becomes `verified` or `needs-review` (via `verifying` while active).

## Phase 6 to 8: synthesis

Architecture, cross-domain workflows, and QA docs build only on verified modules. Follow `references/architecture-documentation.md` and `references/qa-documentation.md`. If verification exposed a contradiction between two modules, resolve it first and re-verify the affected docs before synthesizing.

## Phase 9: final review

1. Write or update `index.md`: what the doc set covers, audience per doc, verification state, and known gaps.
2. Validate: frontmatter on every canonical doc, module IDs referenced by `related modules` sections exist in the manifest, internal links resolve, and `verified_commit` values are real SHAs in the target repo.
3. Run a stale check: list docs whose source paths changed after `verified_commit`. Mark them `needs-review` or re-verify.
4. Confirm the manifest has no module stuck in a transient state (`researching`, `documenting`, `verifying`). Transient states must resolve to a resting state before handoff.

## Manifest state model

Statuses, in normal order:

```text
discovered -> researching -> researched -> documenting -> documented -> verifying -> verified
```

`needs-review` is a resting state reachable from `documented`, `verified`, or any verification failure. A module in `needs-review` returns to `researching` or `documenting` with a note explaining what to recheck.

Rules:

- Statuses live in `<docs_dir>/manifest.yml`. That file is the source of truth for progress.
- Every status change includes the doc path and, once verified, the commit SHA.
- Never mark `verified` without an independent source review and a recorded `verified_commit`.
- Keep progress outside model memory. Update the manifest after each module phase so a restart resumes cleanly.

Minimal manifest entry:

```yaml
modules:
  - id: accounts
    title: Accounts
    status: verified
    paths:
      - src/accounts
    depends_on: []
    doc: modules/accounts.md
    research: research/accounts.md
    verified_commit: abc123
```

Full schema and example: `templates/manifest.yml`.

## Resumability

Any agent picking up the work midstream runs these steps:

1. Read the config (`docs.config.yml` if present) and the manifest.
2. Check for transient states and resume or reset them with a note.
3. Run the stale check if Git history is available.
4. Pick the next module per dependency order (or run the helper `docs.py next`).
5. Continue from the phase implied by that module status.

## Manual fallback (no helper)

If `scripts/docs.py` is unavailable, do the equivalent by hand:

- Progress: read `manifest.yml` and list modules by status.
- Next work: choose a `discovered` module whose `depends_on` entries are all `verified`.
- Stale check: run `git log --oneline <verified_commit>..HEAD -- <paths>` per module. Any output means the doc is a re-verify candidate.
- Link check: search canonical docs for relative links and confirm each target exists.
