# SEO Editorial Team Architecture

## Purpose

This template defines a three-role SEO production team for evidence-backed
Japanese editorial work. Each role has a narrow responsibility and produces a
typed handoff for the next role.

## Components

### Researcher

- Collects primary and trustworthy secondary sources.
- Separates verified facts, claims requiring confirmation, and open questions.
- Produces `templates/research-packet.yaml`.
- Does not write the final article or approve publication.

### Writer

- Converts the research packet into a Japanese SEO draft.
- Preserves source traceability and marks unsupported claims.
- Produces the draft and the requested SEO metadata.
- Revises the draft when the Reviewer returns a FAIL decision.

### Reviewer

- Checks factual support, search intent, structure, Japanese quality, and
  editorial/compliance risks.
- Returns either `PASS` or `FAIL` with actionable findings.
- Does not silently rewrite a draft or approve unresolved blocking findings.

## Handoff flow

```text
Researcher
    |
    v
Writer -----> Reviewer
  ^              |
  |              +-- PASS --> final handoff
  +-- FAIL ------+
       (maximum 3 review attempts)
                    |
                    +-- third FAIL --> BLOCKED_FOR_HUMAN
```

The retry counter is persisted in the case state. A FAIL must identify the
finding, severity, evidence, and required correction. A third FAIL stops the
automated loop and requires human intervention.

## Shared state

- `templates/research-packet.yaml`: Researcher-to-Writer contract.
- `templates/case-state.yaml`: workflow state and retry counter.
- `content/`: drafts and final editorial output.
- `outputs/`: completed handoff packages.

## Operational boundary

Trinity provides scheduling, runtime isolation, credentials, observability,
and agent lifecycle management. The SEO team owns editorial reasoning,
handoff validation, and retry decisions inside the agent workspace.
