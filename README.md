<p align="center">
  <img src="./assets/banner.webp" alt="Neplex skills banner" />
</p>

<h1 align="center">Neplex skills</h1>

<p align="center">
  Public, reusable agent skills maintained by Neplex.
</p>

Each skill is a small engineering protocol that a coding agent loads to perform a task consistently across repositories and runtimes.

## What is a skill

A skill is a directory with an entry point (`SKILL.md`), detailed procedures (`references/`), copyable starting points (`templates/`), and optional deterministic helpers (`scripts/`). It complements the agent. The agent does semantic reasoning. The skill defines workflow, evidence rules, and output contracts. Runtime specific metadata lives in `agents/`.

## Installation

```bash
npx skills add neplextech/skills
```

## Available skills

| Skill                                          | What it does                                                                                                                            |
| ---------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| [documentation](skills/documentation/SKILL.md) | Study a codebase in bounded chunks and produce verified Markdown docs for engineering onboarding, QA, architecture, and troubleshooting |

## Using the documentation skill

1. Point the agent at the skill: `skills/documentation/SKILL.md`.
2. Ask for the outcome you need, for example "document this repository for engineering onboarding" or "document the billing module and its QA risks".
3. The agent follows the phased workflow (map, investigate, write, verify, synthesize, QA) and tracks progress in a module manifest inside the target repository.
4. Optional helper (Python 3, no dependencies) scaffolds output and validates progress:
   `python3 skills/documentation/scripts/docs.py --help`.

The skill works without subagents and without the helper. Subagents parallelize independent domains when the runtime supports them.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the process and [AGENTS.md](AGENTS.md) for skill content rules.

## License

MIT. See [LICENSE](LICENSE).
