---
title: Workflow title
area: workflows
audience:
  - engineering
  - qa
status: documented
source:
  - src/example
  - src/other
verified_commit: null
---

# Workflow title

Trigger and preconditions. Who or what starts this flow, required states and permissions.

## Steps

1. <Step>: <domain responsible>, <what changes> (tables, events, jobs).
2. <Step>: <domain responsible>, <what changes>.

## State changes and side effects

| Step | State change | Side effect | Evidence |
| --- | --- | --- | --- |
| 1 | request moves to authorized | auth audit row written | `src/auth/audit.py` |

## Failure and recovery

What happens when a step fails, what retries, what compensates, what needs a human.

## Observability

Logs, metrics, or dashboards a maintainer checks when this flow breaks, if the repo defines them.

## Open questions

> Needs verification: <unresolved chain links or unclear retry behavior>

## Source references

- `path/to/producer`
- `path/to/consumer`

<!--
Usage: copy to <docs_dir>/workflows/<name>.md, one per cross-domain flow.
Trace with identifiers (event names, job names, routes). Write breaks honestly
instead of inventing a complete chain.
-->
