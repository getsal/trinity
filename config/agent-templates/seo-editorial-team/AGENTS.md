# Codex Instructions: SEO Editorial Team

## Mission

Operate a bounded three-role SEO production line:

1. `Researcher` creates an evidence-backed brief and source ledger.
2. `Writer` creates the draft from the approved research packet.
3. `Reviewer` returns `PASS`, `FAIL`, or `BLOCKED_FOR_HUMAN`.

Keep research, writing, and review responsibilities separate. Do not silently
skip a gate or convert a review failure into a pass.

## Source and artifact rules

- Read the brief and existing case context before researching.
- Prefer primary or official sources and record URLs, access dates, and claims.
- Treat unsupported legal, financial, safety, bonus, or performance claims as
  review failures.
- Write intermediate artifacts under `content/<case-id>/` and final handoffs
  under `outputs/<case-id>/`.
- Never write credentials, tokens, or private MCP configuration to artifacts.

## Orchestration contract

Run `Researcher -> Writer -> Reviewer`. On `FAIL`, pass the review notes and
the unchanged research packet back to `Writer`; increment `review_attempt`.
Allow at most three review attempts. After the third `FAIL`, stop with
`BLOCKED_FOR_HUMAN` and preserve all evidence and review notes.

Use the schemas in `templates/` and the shared skills in `.claude/skills/`.
