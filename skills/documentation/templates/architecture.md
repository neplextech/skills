---
title: System architecture
area: architecture
audience:
  - engineering
status: documented
source:
  - src
verified_commit: null
---

# System architecture

Two to four sentences on what the system is, grounded in entrypoints and datastores.

## Runtime map

Processes and services that run, with wiring evidence.

- <process>: <what it runs> (`path/to/wiring`)

## Data architecture

Datastores, ownership per domain, caches, derived versus authoritative data.

## Integrations

| External system | Direction | Proved by | Failure posture |
| --- | --- | --- | --- |
| <provider> | outbound | `src/integrations/client.py`, config key `PROVIDER_KEY` | retry with backoff, then dead letter |

## Cross cutting concerns

Auth model, tenancy, job and event infrastructure, observability, configuration strategy. Domain detail stays in module docs.

## Related docs

- [Module index](index.md)
- [Workflows](workflows/): per flow files for behavior that crosses domains.

## Source references

- `path/to/wiring`
- `path/to/schema`

<!--
Usage: copy to <docs_dir>/architecture.md after at least two modules are verified.
Keep diagrams small. Prefer named lists over a full system diagram.
-->
