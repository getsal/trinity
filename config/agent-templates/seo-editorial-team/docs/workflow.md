# SEO Production Workflow

## State machine

`READY -> RESEARCHED -> DRAFTED -> REVIEWING`

- `PASS`: `REVIEWING -> APPROVED -> HANDOFF_READY`
- `FAIL` with attempts 1 or 2: `REVIEWING -> REVISION_REQUIRED -> DRAFTED`
- `FAIL` with attempt 3: `REVIEWING -> BLOCKED_FOR_HUMAN`

Every transition updates `templates/case-state.yaml`. The pipeline must be
safe to resume: do not repeat a completed role when its artifact and state
version are valid.

## Handoff contract

Researcher writes:

- `research-packet.yaml`
- `source-ledger.md`
- `brief.md`

Writer writes:

- `outline.md`
- `draft.md`

Reviewer writes:

- `review-<attempt>.md`
- the decision in `case-state.yaml`

Only `PASS` creates `final-handoff.md`. A failed or blocked case must never be
described as publish-ready.

## Reviewer return format

Each finding includes `severity`, `location`, `evidence`, `risk`, and
`required_fix`. `BLOCKER` findings always force `FAIL`. Missing evidence is a
failure, not an invitation to guess.
