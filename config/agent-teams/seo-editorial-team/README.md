# SEO Editorial Team

This is a deployment manifest for three independent Trinity-compatible agents:

1. `seo-researcher` — evidence and source packet.
2. `seo-writer` — Japanese SEO draft and revisions.
3. `seo-reviewer` — factual, SEO, quality, and compliance gate.

The team is an installation and coordination unit, not an execution container.
Each role has its own `template.yaml`, `CLAUDE.md`, `AGENTS.md`, skills,
commands, workspace, and Trinity lifecycle.

## Communication

Agents use Trinity MCP `chat_with_agent` for short control messages and
Trinity shared folders for research packets, drafts, and review evidence.
Configure Agent permissions so the Writer can call and consume Researcher
artifacts, and the Reviewer can call and consume Writer artifacts.

## Workflow

```text
Researcher -> Writer -> Reviewer
                         | PASS -> final handoff
                         | FAIL -> Writer (maximum 3 attempts)
                         | 3rd FAIL -> BLOCKED_FOR_HUMAN
```

See `team.yaml` and `docs/workflow.md` for the deployment contract.
