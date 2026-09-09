# Verification

A document is verified only after an independent source review that tries to falsify it. Reading for tone is not verification.

## Independence rule

The reviewer must differ from the writer. With subagents, dispatch a verification reviewer who reads only the draft plus the repository. Without subagents, perform a fresh pass: close the research file, re-open the cited sources, and check each claim. Record self review honestly in the manifest notes or frontmatter so readers know the review depth.

## Falsification checklist

For each canonical doc, check:

- Unsupported statements: every behavior claim has a cited path, schema, test, or config. Flag claims with no evidence.
- Outdated statements: the cited code still exists and still behaves as described at `verified_commit`.
- Contradictions: the doc agrees with neighboring module docs and handoffs on shared boundaries. Treat disagreements as defects, not style differences.
- Missing branches: error cases, permission denials, validation failures, and empty states are covered or explicitly marked unresolved.
- Missing side effects: events, jobs, messages, cache writes, and external calls named in research appear in the doc or were deliberately excluded with a reason.
- State mistakes: allowed and illegal transitions match guards in code and constraints in schema. Check initial states and terminal states.
- Permission mistakes: enforcement point named, roles correct, fail open versus fail closed stated correctly.
- Concurrency and async behavior: locks, unique constraints, retries, idempotency, ordering, and job overlap handling described correctly where they matter.
- Cross-domain effects: writes to other domains tables, events other domains consume, and config shared across domains are all named.

## Procedure

1. Read the draft once for structure. Note anything confusing before opening code.
2. Walk every source path in frontmatter `source` plus the research file evidence paths. Confirm or refute each behavior claim.
3. Search for what the writer missed: error handlers, permission middleware, event emissions, and job registrations touching the domain paths.
4. Check links: every relative link resolves, every `area` reference matches a manifest ID.
5. Decide: pass, fix directly, or send back. Trivial fixes (wording, links, missing paths) may be applied by the reviewer. Behavior corrections go back to the writer or are fixed and re-checked against source.
6. On pass, set frontmatter `status: verified` and `verified_commit` to the reviewed SHA (from `git rev-parse HEAD` in the target repo). Update the manifest to `verified` with the same SHA. On failure, set `needs-review` with a note listing the defects.

## Stale detection

Docs decay when source changes. Any doc whose source paths changed after `verified_commit` is a re-verify candidate:

```bash
git log --oneline <verified_commit>..HEAD -- <source paths>
```

Any output means the doc may be stale. The helper automates this with `docs.py stale`. Mark confirmed stale docs `needs-review` with a note naming the changed paths. Re-verify by repeating the falsification pass on the changed scope only, then update `verified_commit`.

## Anti-patterns

- Approving because the doc reads well.
- Verifying against the research file alone without opening sources.
- Marking `verified` without a commit SHA.
- Silently resolving a cross-module contradiction by editing one side. Record the resolution and re-verify the other side.
- Letting `verifying` sit in the manifest. It is transient. Resolve it the same session.
