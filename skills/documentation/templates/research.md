# Research notes: <module id>

Module: <id>
Investigator: <name or role>
Date: <YYYY-MM-DD>
Commit: <reviewed SHA>
Scope paths: <paths in scope>

## Observed

Facts directly supported by the repository. One bullet per fact with evidence path.

- <fact> (`path/to/file`, <test or migration where relevant>)
- Owned tables: <tables> (`path/to/schema`)
- Entry points: <handlers, routes, jobs> (`path/to/wiring`)

## Unresolved

Questions that could not be answered confidently.

- <question> (checked: <paths searched>)

## Hypotheses

Possible explanations. Must not become canonical documentation until verified.

- <hypothesis> (would confirm via: <what to check>)

## State table (when relevant)

| State | Meaning | Set by | Guards |
| --- | --- | --- | --- |
| active | usable | confirmation handler | prior state pending |

## Events and side effects

| Kind | Name | Producer | Consumer | Evidence |
| --- | --- | --- | --- | --- |
| event | example.created | this domain | notifications | `src/example/events.py` |
| job | send-welcome | this domain | worker queue | `src/workers/jobs.py` |

## Boundary contracts

- With <related module>: <what this domain guarantees, what it expects> (`evidence path`)

<!--
Usage: copy to <docs_dir>/research/<id>.md, one per domain.
This file is not canonical documentation. It stays in research/ for reviewers.
Keep findings concise. Record paths precisely enough to recheck.
-->
