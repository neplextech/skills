---
title: QA notes for <module>
area: module-id
audience:
  - qa
status: documented
source:
  - src/example
verified_commit: null
---

# QA notes for <module>

Scope: what behavior this file covers. Links to [module doc](../modules/module-id.md) and related [workflow](../workflows/example-flow.md) docs.

## Critical paths

1. <Flow name>
   Setup: <preconditions, roles, seed state>
   Steps: <numbered actions>
   Expected: <end state and observable effects>

## Invariants

- <rule> (enforced by: <constraint, guard, or test path>)
- <rule> (violation visible as: <what to observe>)

## Failure and recovery

| Fault | Expected behavior | Evidence |
| --- | --- | --- |
| double submit | one record, second request rejected or deduped | `src/example/handlers.py`, unique constraint in `db/migrations/010_example.sql` |
| provider timeout | job retries with backoff, then dead letter | `src/workers/jobs.py` |

## Concurrency and timing

- <race or overlap risk> (prevented by: <lock, constraint, or job guard>)

## Permissions

| Role | Operation | Expected |
| --- | --- | --- |
| staff | approve refund | allow |
| customer | approve refund | deny |

## Integration and job risks

- <provider or background failure mode and what piles up>

## Regression hotspots

- <where a small change breaks distant behavior>

## Open questions

> Needs verification: <what a tester should confirm with engineering>

<!--
Usage: copy to <docs_dir>/qa/<id>.md. Include only sections that apply.
Every risk needs evidence or an explicit Needs verification marker.
-->
