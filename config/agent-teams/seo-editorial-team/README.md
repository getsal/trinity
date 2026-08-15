# SEO Editorial Team

This is a deployment manifest for three independent Trinity-compatible agents:

1. `seo-researcher` — evidence and source packet.
2. `seo-writer` — Japanese SEO draft and revisions.
3. `seo-reviewer` — factual, SEO, quality, and compliance gate.

The team is an organization and execution boundary, not a single execution
container. Members are permanent department roles and must not be deployed as
standalone general-purpose Agents. Each role has its own `template.yaml`,
`CLAUDE.md`, `AGENTS.md`, skills, commands, workspace, and Trinity lifecycle.

Individual customization is allowed for domain prompts, approved tools,
resource limits, dashboard widgets, and local skill extensions. Role identity,
workflow edges, approval authority, evidence preservation, and the three-attempt
retry limit are Team policies and require operator changes.

## Communication

Agents use Trinity MCP `chat_with_agent` for short control messages and
Trinity shared folders for research packets, drafts, and review evidence.
Configure Agent permissions so the Writer can call and consume Researcher
artifacts, and the Reviewer can call and consume Writer artifacts.

## Department view

Assign the tag `dept-seo-editorial-team` to all three Agents. Trinity's
Dashboard Grid will render them as one Department zone. The production flow is
represented by the Team workflow edges; do not model the Reviewer as a
manager merely because it is the approval gate. If a human or Agent manager is
added later, use a `reports-to-<agent-name>` tag separately.

## Workflow

```text
Researcher -> Writer -> Reviewer
                         | PASS -> final handoff
                         | FAIL -> Writer (maximum 3 attempts)
                         | 3rd FAIL -> BLOCKED_FOR_HUMAN
```

See `team.yaml` and `docs/workflow.md` for the deployment contract.
