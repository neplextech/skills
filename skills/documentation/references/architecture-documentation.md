# Architecture documentation

Write `architecture.md` and `workflows/` only after at least two modules are verified, or one verified module plus the repo sketch. Architecture built on unverified drafts invents structure.

## Architecture file

`architecture.md` answers: what is this system, what are its parts, how do they interact, and where does state live. Template: `templates/architecture.md`.

Include:

- System summary: two to four sentences grounded in entrypoints and datastores found during mapping.
- Runtime map: processes and services that run (API server, workers, schedulers, frontend apps), with the wiring that proves each one.
- Data architecture: datastores, ownership per domain, caches, and what is derived versus authoritative.
- Integration map: external systems called, direction of calls, config keys or clients that prove them, and failure posture (retry, timeout, fallback) where the code states it.
- Cross cutting concerns in one place: auth model, tenancy, job and event infrastructure, observability, configuration strategy. Domain detail stays in module docs.
- Small diagram only if it clarifies. One runtime sketch or one data flow sketch at most. Prefer named lists when the system is small.

Exclude: per endpoint lists, per table column lists, framework tutorials, speculation about scale the repo does not address.

## Cross-domain workflows

Module docs explain parts. Workflow docs explain behavior that crosses parts. Typical shape:

```text
request -> authorization -> domain mutation -> event -> background job -> external integration -> reporting
```

Not every system has every stage. Document the stages the repo actually wires together. Never invent stages to fit the shape.

### Selecting workflows

Derive candidates from evidence, not imagination:

- Events with both a producer and a consumer in different domains.
- Jobs enqueued by one domain and processed with effects in another.
- Requests that write tables owned by two or more domains.
- State changes in one domain that gate behavior in another.
- External callbacks that re-enter the system.

Aim for 3 to 8 workflows on a large system. Each workflow file follows `templates/workflow.md` (or the workflow section of `templates/architecture.md` for small systems that need only one or two).

### Workflow file contract

Each `workflows/<name>.md` states:

- Trigger and preconditions (who or what starts it, required states and permissions).
- Step sequence with the domain responsible for each step.
- State changes and side effects per step (tables, events, jobs, messages, external calls).
- Failure and recovery: what happens when a step fails, what retries, what compensates, what needs a human.
- Observability: logs, metrics, or job dashboards a maintainer checks when this flow breaks, if the repo defines them.
- Open questions as `> Needs verification` notes.

Frontmatter mirrors module docs with `area: workflows` and `source` listing the crossed paths.

### Tracing without inventing

Follow identifiers through the repo: event names, job names, queue names, webhook routes, correlation IDs. If the chain breaks (producer found, consumer missing), write the break explicitly:

```text
> Needs verification: payment.settled is emitted, but no consumer was found in this repository. Delivery may happen in a separate service.
```

A broken chain documented honestly is more useful than a complete chain invented smoothly.

## Integration investigator role

With subagents, assign cross-domain integration after module verification. That investigator reads handoffs and workflow relevant sources only, not every module research file. Without subagents, do the same pass sequentially: read all handoffs, then trace 3 to 8 chains through code.

Contradictions between handoffs become verification tasks against source. The workflow doc records the resolved behavior plus the SHA it was verified at.
