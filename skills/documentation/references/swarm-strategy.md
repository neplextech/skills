# Swarm strategy

Parallelize independent domains. Respect dependencies. Keep the coordinator lightweight and keep state on disk.

## When to parallelize

- 2 or more `discovered` modules with no unfinished dependencies: dispatch investigators in parallel.
- Writing: a module whose research is complete can go to a writer while other domains are still investigated.
- Verification: dispatch a reviewer as soon as a draft exists, with the writer moving to the next module.
- QA and workflows: start once 2 or more modules are verified. These passes read handoffs, not full research files.

Small repos (1 to 3 modules, clear boundaries) often finish faster sequentially. Parallelism pays off when investigation passes are independent and each pass is large enough to justify handoff overhead.

## Roles

Define each dispatch with scope, inputs, outputs, and handoff format. Role prompts stay vendor neutral: describe the task, not the API.

- Repository mapper: runs phases 0 and 1. Inputs: repo root, ignore list. Outputs: repo sketch, `manifest.yml` with `discovered` modules. One instance only.
- Domain investigator: runs phase 3 for one module. Inputs: module entry, dependency handoffs, boundary list. Outputs: `research/<id>.md`, `handoffs/<id>.yml`. Narrow scope; no canonical docs.
- Documentation writer: runs phase 4 for one researched module. Inputs: research file, handoff, spot check access. Outputs: `modules/<id>.md` with `status: documented`. No re-investigation.
- Verification reviewer: runs phase 5 for one draft. Inputs: draft, research file, repo access. Outputs: reviewed doc set to `verified` or `needs-review` with defects listed. Must differ from the writer.
- Cross-domain integration investigator: runs phases 6 and 7. Inputs: verified handoffs and workflow relevant sources. Outputs: `architecture.md`, `workflows/<name>.md`.
- QA analyst: runs phase 8. Inputs: verified module and workflow docs plus evidence paths. Outputs: `qa/<id>.md` grounded in repo behavior.

Suggested scope block for any dispatch:

```text
Scope: <module id + paths>
Read first: <dependency handoffs, mapping sketch>
Do not touch: <out of scope paths, except named boundary interfaces>
Write: <expected artifact paths>
Handoff format: <templates/handoff.yml keys>
Done when: <exit criterion from methodology.md>
```

## Coordinator loop

The coordinator (main agent or a designated lightweight agent) does not investigate. It:

1. Discovers work from the manifest and dependency order.
2. Assigns bounded tasks with the scope block above.
3. Tracks progress by reading manifest statuses and handoffs, not by re-reading sources.
4. Collects structured handoffs and checks them for missing keys and unknown `related_modules` IDs.
5. Identifies contradictions between handoffs touching the same boundary and dispatches targeted verification against source.
6. Orders verification before synthesis. No architecture or QA dispatch consumes unverified drafts.
7. Re-queues failures as `needs-review` with a defect note, never by silently picking a side.

## Communication

- Filesystem as coordination: `manifest.yml` for progress, `handoffs/` for dependencies, `research/` for detail, canonical paths for drafts.
- Handoffs stay compact (roughly 60 lines). Detail lives in research files. Reviewers and downstream roles read handoffs first and open research only on demand.
- Contradiction protocol: when two handoffs disagree on shared behavior, freeze synthesis for the affected workflows, dispatch verification scoped to the disputed paths, record the resolution, and re-verify affected docs.

## Dependency ordering

A module is dispatchable when all its `depends_on` entries are `researched` (for investigation) or `verified` (for synthesis and QA). The helper `docs.py next` computes this. Manual equivalent: pick a `discovered` module whose dependencies are all `verified`, preferring modules that unblock the most dependents.

Allow bounded overlap at integration boundaries: neighbors may read shared interfaces concurrently. Overlap is limited to named boundary files, not full scope merges.

## Sequential fallback

Without subagents, the same roles run as passes in one context window per phase:

1. Map fully, then stop and review.
2. Investigate one domain at a time, writing research and handoff before moving on.
3. Write one module doc, then verify it with a fresh source pass before writing the next.
4. Synthesize architecture and workflows, then QA, then final review.

Artifacts are identical. Only the parallelism changes.
