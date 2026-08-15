# SEO Editorial Team Workflow

## State machine

```text
BRIEFED -> COORDINATING -> RESEARCHING -> RESEARCH_COMPLETE -> WRITING -> REVIEWING
                                               ^             |
                                               | FAIL        | PASS
                                               +-------------+--> COMPLETE
                                                     attempt < 3
REVIEWING -- FAIL on attempt 3 --> BLOCKED_FOR_HUMAN
```

## Communication contract

- Coordinator sends `research_requested` to `seo-researcher`.
- Researcher sends `research_packet_ready` to `seo-coordinator`.
- Coordinator sends `draft_requested` to `seo-writer`.
- Writer sends `draft_ready` to `seo-coordinator`.
- Coordinator sends `review_requested` to `seo-reviewer`.
- Reviewer sends `review_fail` to `seo-coordinator` with findings and attempt number.
- Coordinator sends `revision_requested` to `seo-writer` unless the limit is reached.
- Reviewer sends PASS or `blocked_for_human` to `seo-coordinator`.
- Coordinator sends final handoff or human escalation to the operator.

Use `chat_with_agent` for these control messages. Put large artifacts in the
permitted shared folder; never pass an entire draft through the MCP message.

## Independence rules

- No role may perform another role's approval decision.
- Reviewer never edits the Writer's draft.
- Writer revisions preserve the original research packet and review history.
- A third FAIL terminates automation and requires a human decision.
