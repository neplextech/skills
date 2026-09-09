# Module documentation

Write one canonical file per domain at `modules/<id>.md` from `templates/module.md`. The reader is an engineer or QA specialist who needs to work with the system, not a reviewer of your research.

## Input discipline

Read the research file, the handoff, and spot checked sources. Do not re-investigate the repository from scratch. If the research is thin, send the module back to `researching` with a note instead of inventing content.

## Section contract

Include a section only when it applies. Omit the rest. Typical order:

1. Purpose: two or three sentences on what the domain does and who uses it.
2. Where it lives: paths, owned tables, entrypoints. Short.
3. Core concepts: terms the codebase actually uses, defined once.
4. Data model: entities, ownership, identifiers, lifecycle relevant fields. No column dumps.
5. Main workflows: observable behavior in plain steps. Name the trigger, the checks, the mutation, and the outcome.
6. Business rules: invariants the system enforces, with the enforcement point.
7. State transitions: allowed transitions, guards, illegal moves, and effects. Prefer a small table over prose.
8. Permissions: who can do what, where enforcement happens, what fails closed.
9. Side effects: events, jobs, messages, external calls, cache effects.
10. Failure behavior: validation, conflicts, retries, idempotency, compensation.
11. Important edge cases: only cases that change what an engineer or tester would do.
12. Relevant APIs or interfaces: operations humans call, with identifiers they need. Not a route dump.
13. Background processing: jobs, schedules, overlap guards, delivery guarantees.
14. Related modules: links to neighboring docs with the contract in one line each.
15. QA notes: pointer to the QA file, plus at most five high risk behaviors.
16. Source references: paths a maintainer can open to recheck. Grouped, not inline on every sentence.

No mandatory conclusion section. End on source references.

## Behavior over code

Bad: narrates call order inside one function.

```text
ExampleService.create() creates an Example and then calls NotificationService.
```

Good: states observable behavior with the reference grouped at the end.

```text
Creating an account moves it to pending until email confirmation. Confirmation activates it and enqueues a welcome message. Unconfirmed accounts cannot sign in.
```

Mention function, class, table, endpoint, event, or job names only when they help a maintainer act. A reader should understand the product without knowing the framework.

Technical implementation belongs in the doc when it affects architecture, security, failure handling, consistency, performance, operations, extension points, or debugging. Otherwise leave it in the research file.

## Frontmatter

Every module file starts with frontmatter:

```yaml
---
title: Accounts
area: accounts
audience:
  - engineering
  - qa
status: documented
source:
  - src/accounts
  - db/migrations/010_accounts.sql
verified_commit: null
---
```

Rules:

- `area` must equal the manifest module `id`.
- `source` lists the primary paths a maintainer would open. Keep it under about 10 entries.
- `status` is `documented` after writing, `verified` only after independent review.
- `verified_commit` is null until verification sets it to the reviewed SHA.
- The helper validates these fields with `docs.py verify`. See `references/verification.md`.

## Length and links

- Aim for what a competent engineer can read in 10 to 15 minutes. Split only when a section has a distinct audience (workflow docs move to `workflows/`, test detail moves to `qa/`).
- Link related modules with relative paths (`access-control.md` for a sibling module, `../workflows/signup-to-first-use.md` for a workflow). The helper checks these links.
- Record disagreements with neighboring research as `> Needs verification` notes, not as settled facts.
