# QA documentation

QA docs do not repeat engineering docs. They answer: how can this system break, where do regressions hide, and what should a tester check first. Template: `templates/qa.md`.

Write QA docs after the corresponding module or workflow is verified. Ground every risk in repository behavior. A risk without evidence is a hypothesis, and must be labeled as one.

## QA analyst stance

Approach verified behavior with one question: how can this break. For each domain, examine:

- Critical workflows: the 3 to 5 user or system flows where failure costs the most. Name preconditions and expected end states.
- Business invariants: rules that must never be violated (balances reconcile, states move forward only, permissions deny by default). State how to detect a violation.
- Failure boundaries: validation, conflicts, retries, idempotency, dead letters, compensation. What happens on second submit, on timeout, on partial failure.
- Cross-module interactions: where this domain writes another domain state, emits events others consume, or depends on another domain check. These seams are regression hotspots.
- Error recovery: what the user sees, what support does, what self heals, what needs manual repair.
- Concurrency risks: double submit, parallel edits, overlapping job runs, race windows around unique constraints or state guards.
- State transition risks: illegal transitions, skipped steps, re-entry after terminal states, reset and restore paths.
- Permissions: role matrix worth testing, escalation paths, what fails open.
- External integrations: provider outages, webhook replays, slow responses, sandbox versus production differences stated in config or tests.
- Background jobs: schedules, overlap guards, retry limits, ordering assumptions, what piles up when the queue stalls.
- Data consistency: derived data versus authoritative data, cache invalidation, reporting lag.
- High risk regression areas: code with many callers, shared validators, migrations that reinterpret old rows.

## QA file contract

One file per domain or per workflow at `qa/<id>.md`. Include only sections that apply:

1. Scope: what behavior this file covers, linked to the module or workflow doc.
2. Critical paths: numbered test flows with setup, steps, and expected end state.
3. Invariants: checkable rules, each with how to observe a violation.
4. Failure and recovery matrix: small table of fault, expected behavior, and evidence path.
5. Concurrency and timing: races and overlaps worth testing, with the mechanism (lock, constraint, job guard) that should prevent them.
6. Permissions matrix: roles against operations, expected allow or deny.
7. Integration and job risks: provider and background failure modes.
8. Regression hotspots: where a small change breaks distant behavior.
9. Open questions: `> Needs verification` items a tester should confirm with engineering.

Keep each file testable. Prefer "submit the form twice and expect one record (unique constraint on X)" over "test thoroughly".

## Evidence rules

- Every invariant and failure claim cites the enforcement point (constraint, guard, test, handler) in parentheses or in a short evidence column.
- Behavior the repo does not prove is marked:

```md
> Needs verification: No test or handler confirms what happens when the provider times out. Likely surface for silent failure.
```

- Do not copy implementation prose from module docs. Reference the module doc and add what a tester does differently.

## Frontmatter

```yaml
---
title: QA notes for accounts
area: accounts
audience:
  - qa
status: documented
source:
  - src/accounts
verified_commit: null
---
```

`area` matches the module or workflow ID. Verification follows the same falsification procedure as module docs.
