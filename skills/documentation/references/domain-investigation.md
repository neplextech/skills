# Domain investigation

One investigator owns one domain. The output is research, not canonical documentation. Research is thorough and cites evidence. Canonical docs come later and contain a fraction of it.

## Inputs

- Module entry from `manifest.yml`: `id`, `paths`, `depends_on`.
- Handoffs of dependency modules (`handoffs/<dep>.yml`) when they exist. Read those before the source tree.
- The repo sketch from repository mapping.

## Boundaries

- Primary scope: the listed paths plus owned tables, owned events, and owned config.
- Boundary scope: interfaces the domain calls (auth checks, shared services, queues, external clients). Read enough to name the contract and failure modes. Do not document the neighboring domain.
- Overlap is intentional. Two investigators may read the same boundary file from opposite sides. If they disagree, record both observations and flag a verification task. Do not negotiate the fact away.

## Evidence hierarchy

Prefer in this order:

1. Schema, migrations, constraints, validation code.
2. Permission checks and policy enforcement.
3. State transitions in code plus the tests that pin them.
4. API definitions, event schemas, job payloads.
5. Handler and worker implementation.
6. Frontend behavior that constrains or extends backend rules.
7. Existing docs and comments, treated as leads to confirm, not as facts.

Never assert behavior from names alone. A function called `sendReceipt` is not proof a receipt is sent. Find the call, the queue or client, and the failure path.

## What to capture

- Entities and data ownership: tables or collections, owners versus readers, identifiers, timestamps, soft delete versus hard delete.
- Lifecycle and states: allowed values, who transitions them, guards, illegal transitions, what breaks if a transition is skipped.
- Writes: create, update, archive, restore, merge, transfer. Preconditions, validation, atomicity, and what else changes in the same transaction.
- Reads with rules: listing, filtering, visibility scoping (tenant, role, ownership), pagination Consistent behavior matters more than endpoint lists.
- Permissions: required role or scope per operation, where enforcement happens, what fails closed versus open, privilege escalation risks.
- Side effects: events emitted, jobs enqueued, messages sent, cache invalidated, external calls made. Include payload keys and delivery guarantees where the code states them.
- Failure behavior: validation errors, conflict handling, retries, idempotency keys, dead letter handling, compensation or rollback.
- Concurrency and timing: locks, unique constraints, race windows, ordering assumptions, scheduled jobs and their overlap guards.
- Config and operations: environment keys, feature flags, limits, timeouts, extension points a maintainer would need.

## Research file contract

Write `research/<id>.md` from `templates/research.md`. Required sections:

- `Observed`: facts with file references. Each bullet should be traceable to a path.
- `Unresolved`: questions that could not be answered from the repo.
- `Hypotheses`: possible explanations, clearly labeled, never to be copied as facts.

Additional sections (state tables, event tables, flow sketches) are encouraged when they clarify. Keep findings concise. Record file paths with enough precision to recheck (`src/billing/invoices.py`, migration `db/migrations/042_add_invoice_state.sql`, test `tests/billing/test_refunds.py`).

Research files may contain uncertainties, conflicting observations, and dead ends. They must not contain chain of thought narration. State what was checked and what was found.

## Structured handoff

Write `handoffs/<id>.yml` from `templates/handoff.yml` alongside the research file. The handoff is the only thing other agents read in full. Keep it under roughly 60 lines: entities, states, writes, reads, events emitted and consumed, side effects, related modules, uncertainties.

The detailed research file carries context. The handoff carries dependencies. Another investigator should understand what your domain guarantees and what it needs without opening your prose.

## Uncertainty rules

- Every claim without direct evidence goes to `Unresolved` or `Hypotheses`, never to `Observed`.
- Canonical style bans guessing, so push doubt into the research file now. A long `Unresolved` list is a good research file. A short one on a complex domain usually means skimming.
- Use the exact marker for gaps that survive to canonical docs:

```md
> Needs verification: It is unclear whether ...
```

## Done when

- All paths in scope were read or explicitly excluded with a reason.
- Owned tables, states, writes, permission checks, events, jobs, and external calls are recorded or marked unresolved.
- Boundary contracts with each related module are named in both the research file and the handoff.
- The handoff validates against the expected keys and the manifest moves to `researched`.
