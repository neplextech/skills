---
title: Module title
area: module-id
audience:
  - engineering
  - qa
status: documented
source:
  - src/example
verified_commit: null
---

# Module title

Purpose in two or three sentences. What this domain does and who uses it.

## Where it lives

Paths, owned tables, entrypoints. Keep short.

## Core concepts

Terms the codebase actually uses, defined once.

## Data model

Entities, ownership, identifiers, lifecycle relevant fields. No column dumps.

## Main workflows

Observable behavior in plain steps. Trigger, checks, mutation, outcome.

## Business rules

Invariants with enforcement points.

## State transitions

| From | To | Guard | Effect |
| --- | --- | --- | --- |
| pending | active | confirmation received | sign in allowed, welcome message enqueued |

Omit this section when the domain has no state machine.

## Permissions

Who can do what, where enforcement happens, what fails closed.

## Side effects

Events, jobs, messages, external calls, cache effects.

## Failure behavior

Validation, conflicts, retries, idempotency, compensation.

## Important edge cases

Only cases that change what an engineer or tester would do.

## Relevant APIs or interfaces

Operations humans call, with identifiers they need. Not a route dump.

## Background processing

Jobs, schedules, overlap guards, delivery guarantees. Omit when none.

## Related modules

- [Access control](access-control.md): enforces permissions for all writes in this domain.
- [Notifications](notifications.md): consumes `example.created` to send messages.

## QA notes

Pointer to `../qa/module-id.md` plus at most five high risk behaviors.

## Source references

- `src/example/` : handlers and validation
- `db/migrations/010_example.sql` : table and constraints
- `tests/example/test_lifecycle.py` : state transition coverage

<!--
Usage: copy to <docs_dir>/modules/<id>.md. Omit sections that do not apply.
Do not add a conclusion section. Keep frontmatter area equal to the manifest id.
-->
