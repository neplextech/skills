# Contributor guide

This repository holds public, reusable agent skills maintained by Neplex.

## Layout

```text
skills/<skill-name>/
  SKILL.md        # skill entry point
  references/     # detailed procedures
  templates/      # copyable starting points
  scripts/        # optional deterministic helpers
  agents/         # runtime specific metadata (for example openai.yaml)
```

`CLAUDE.md` references this file. Do not duplicate its content elsewhere.

## Rules for contributions

- Keep every skill project neutral and vendor neutral. No internal architecture, module names, URLs, credentials, or proprietary examples. Use generic examples.
- Keep the skill usable without helpers or subagents. Helpers and swarms must be optional improvements, never requirements.
- Prefer editing existing files over adding new ones. Each new file needs a clear role stated in the skill or reference that points to it.
- Match the existing prose style: plain professional English, sentence case headings, no em dashes, no marketing language, no decorative emoji.
- Validate all paths and examples before opening a PR. If you add executable tooling, run it and cover init, happy path, and failure output.
- Update the root `README.md` skill list when adding or removing a skill.

## Working with this repo

- Read `skills/<skill-name>/SKILL.md` first, then the references it points to.
- Test helper scripts with the system Python only (`python3 scripts/...`). Do not add dependencies without discussion.
- Keep PRs scoped to one skill unless the change affects shared repo files.
