# Writing style

Applies to all canonical docs (`modules/`, `architecture.md`, `workflows/`, `qa/`, `index.md`). Research files follow `domain-investigation.md` instead.

## Voice

- Plain professional English. Short sentences when possible.
- Active voice where natural. Name the actor: the user, the job, the integration, the system.
- Project terminology as used in code and schema. Define a term once, then reuse it. Do not invent synonyms.
- Concrete claims over abstractions. State what happens, who can trigger it, and what changes.

## Structure

- Sentence case headings. No title case.
- One idea per paragraph. Short lists over long paragraphs for rules, states, and failure modes.
- Common contract where useful, irrelevant sections omitted. Never pad a doc to match a template length.
- No mandatory conclusion or summary section. End on the most useful section, usually source references or related docs.
- Small tables for states, permissions, and error handling. Prose for everything else.

## Formatting

- No em dashes in prose. Use commas, colons, or parentheses.
- Minimal bold. Reserve it for terms being defined and critical warnings.
- No decorative emoji. No ASCII banners.
- Code identifiers in backticks only when they name something the reader acts on (table, event, endpoint, config key, job name).
- Mermaid only when a diagram says something more clearly than prose (state machines with more than three states, branching workflows). Keep diagrams small enough to read without scrolling. Never generate a full system diagram.
- Links between related docs with relative paths. Link the first mention; do not repeat the same link every paragraph.

## Wording

Concrete and checkable. Prefer numbers, states, roles, and named events over adjectives.

Avoid:

- Promotional language: robust, seamless, powerful, cutting edge, comprehensive ecosystem, pivotal, designed to enhance.
- Filler: in todays landscape, in general, basically, essentially, it is worth noting that, this ensures that.
- Fake certainty: always, never, guaranteed, instantly. If timing or guarantees come from code, cite the mechanism (unique constraint, transaction, idempotency key, retry limit). If they do not, mark the claim as needing verification.
- Code narration: do not walk through functions line by line. Describe observable behavior.
- Repetition: say a rule once in the section where it matters, then cross reference.

## Examples

Good:

```text
Refunds move a payment from settled to refunded. Only users with the refunds Approve permission can approve refunds above 500. Approval enqueues a payout job and emits payment.refunded.
```

Bad:

```text
Our robust refund ecosystem seamlessly ensures cutting edge money movement designed to enhance customer satisfaction.
```

Good edge handling:

```text
> Needs verification: It is unclear whether partial refunds are allowed after settlement. The UI suggests yes, but no backend path confirms it.
```

## Checklist before marking documented

- [ ] Every behavior claim traces to research evidence or a named source.
- [ ] Uncertain claims carry `> Needs verification` markers instead of confident wording.
- [ ] No banned phrasing, no em dashes, headings in sentence case.
- [ ] Frontmatter present with correct `area`, `audience`, `status`, and `source`.
- [ ] Related modules linked. Terms match the codebase.
