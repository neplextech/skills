# Contributing

Thanks for helping improve these skills. This file covers the contribution process. Content rules for skills live in [AGENTS.md](AGENTS.md). Read both before opening a PR.

## Ways to contribute

- Fix inaccurate instructions, broken paths, or stale examples in an existing skill.
- Improve templates or references where a section is missing or unclear.
- Fix bugs in helper scripts or extend their validation coverage.
- Propose a new skill by opening an issue first, describing the problem it solves and why existing skills do not cover it.

## Getting started

1. Fork the repository and create a branch from `main`.
2. Read the skill entry point first (`skills/<skill-name>/SKILL.md`), then the references it points to.
3. Make your change following the layout and rules below.
4. Run the validation checklist, then open a PR.

## Skill layout

```text
skills/<skill-name>/
  SKILL.md        # skill entry point
  references/     # detailed procedures
  templates/      # copyable starting points
  scripts/        # optional deterministic helpers
  agents/         # runtime specific metadata (for example openai.yaml)
```

Each file needs a clear role. Prefer editing existing files over adding new ones. If you add a file, state its role in the skill or in the reference that points to it.

`SKILL.md` must keep valid frontmatter (`name`, `description`) and stay a concise orchestrator. Detail belongs in `references/`, not in the entry point.

## Content rules

The full rules are in [AGENTS.md](AGENTS.md). The short version:

- Project neutral and vendor neutral. No internal architecture, module names, URLs, credentials, or proprietary examples. Use generic examples.
- Skills must work without helpers or subagents. Tooling and parallel execution are optional improvements, never requirements.
- Plain professional English, sentence case headings, no em dashes, no marketing language, no decorative emoji.

## Helper scripts

- Standard library only. Test with the system Python (`python3 scripts/...`). Do not add dependencies without prior discussion.
- A helper complements the agent. It may scaffold files, validate state, or report progress. It must not generate prose or make semantic decisions.
- Cover init, happy path, and failure output when you change behavior. See the existing skill for the expected pattern.

## Validation checklist

Run these before opening a PR:

- [ ] Every path and example in changed files was verified against the actual repository.
- [ ] Helper changes were executed locally, including at least one failure case.
- [ ] No em dash characters in prose. No internal or proprietary details.
- [ ] The root `README.md` skill list was updated when adding or removing a skill.
- [ ] Headings use sentence case. No new marketing language or filler.

## Opening a PR

- Keep PRs scoped to one skill unless the change affects shared repo files.
- Describe what changed and why. Link the related issue when one exists.
- Call out anything you could not verify so reviewers know where to look.
- Expect review on correctness, neutrality, and scope. Small, focused PRs move fastest.
