# Repository mapping

Map logical domains before writing any documentation. Folders are not domains. A domain can span backend, frontend, schema, migrations, queues, tests, and integrations.

## Goals

- Identify what the system is and who it serves, in two or three sentences grounded in the repo.
- List entrypoints: HTTP servers, CLIs, workers, schedulers, frontend apps.
- List datastores, queues, caches, and external integrations with the config or client code that proves each one.
- Propose logical documentation domains with stable IDs, scope paths, and dependency hints.
- Produce a human reviewable map before large documentation work starts.

## Procedure

1. Start from the outside. Read top level files first: `README`, package or module manifests, build files, container files, compose files, CI configs. Record what each entrypoint runs.
2. Follow config to runtime. Check environment examples, config schemas, and wiring (routers, DI containers, job registrations, cron definitions). Note which services talk to which datastores or external APIs.
3. Inspect data definitions. Read schemas, migrations, and validation code before business logic. Data shapes constrain behavior more reliably than handler code.
4. Inspect tests for intent. Test names and fixtures often state invariants that implementation hides. Treat tests as supporting evidence, not as proof that production behaves the same way.
5. Sketch call paths for 2 to 4 core flows (for example: inbound request through auth, mutation, event, worker, external call). Keep the sketch to named components and evidence paths.
6. Propose domains. Group by business capability and data ownership, not by folder prefix. Typical split points: identity and access, core domain entities, money or inventory movement, notifications, search and reporting, integrations, platform and jobs.
7. Assign IDs. Use short lowercase slugs with hyphens (`accounts`, `access-control`, `order-fulfillment`). IDs are stable and appear in the manifest, frontmatter, and filenames.
8. Record dependencies. A domain depends on another when it imports its code, writes its tables, emits events the other consumes, or enforces its rules. Keep `depends_on` to direct dependencies only.

## Output

Write the map to `<docs_dir>/map.md` or present it in chat for small repos, and encode the module list in `<docs_dir>/manifest.yml` with every module at `status: discovered`. Template: `templates/manifest.yml`.

Each mapped domain needs:

- `id` and one line scope statement.
- `paths`: repository paths that belong to it (may span unrelated trees).
- `depends_on`: IDs that must be understood first.
- Open questions that affect scope.

Example scope statements:

- `accounts`: user and organization records, profile lifecycle, deactivation effects.
- `access-control`: authentication, session handling, role and permission enforcement.
- `notifications`: event triggered messages, templates, delivery retries, provider wiring.

## Scope heuristics

- Aim for 4 to 12 domains on a large repo. Fewer than 4 usually means domains are too broad for bounded investigation. More than 12 usually means folders were mirrored instead of grouped.
- Keep each domain investigable in one bounded pass: roughly the amount one agent can read carefully without skimming (on the order of 10 to 40 source files plus schema and tests, not hundreds).
- Split when a domain has independent data ownership, independent lifecycle, or a distinct expert audience. Merge when two candidates share tables, share state machines, and always change together.
- Frontend and backend for the same capability belong to one domain unless the frontend is a separate product with its own release cycle.

## Anti-patterns

- Mirroring `src/` subfolders one to one into modules. This preserves accidental structure instead of business structure.
- Declaring a `utils` or `shared` documentation domain. Shared code is documented where it is used, with a short shared kernel section in `architecture.md` if it affects the whole system.
- Mapping from file names alone without opening schemas, routers, and job registrations.
- Asserting integrations (payment provider, email provider, analytics) without naming the client code or config key that proves them.

## Review gate

Stop after mapping when the repo is large or boundaries are unclear. Ask a human to confirm, merge, or split domains before dispatching investigations. A wrong early split costs more than a short review pause.
