# SEO Editorial Team

A Trinity-compatible, three-role SEO production team for evidence-backed
Japanese editorial work.

## Roles

- **Researcher**: brief analysis, search intent, keyword/SERP research, source
  ledger, claims and uncertainty notes.
- **Writer**: outline and draft based only on the approved research packet.
- **Reviewer**: editorial, factual, compliance, and final SEO gate.

## Workflow

```text
Researcher -> Writer -> Reviewer
                         | PASS -> final handoff
                         | FAIL -> Writer (max 3 attempts)
                         | 3rd FAIL -> BLOCKED_FOR_HUMAN
```

The retry counter is persisted in the case state. A reviewer cannot rewrite a
draft or approve an unresolved blocking finding.

## Install and run

Copy this directory or deploy it directly with Trinity. Configure local values
from `.env.example`, then run `/run-seo-pipeline` with a case brief. The
template intentionally has no MCP server enabled; add only approved tools to a
local `.mcp.json`.

## Reused knowledge

The role split and review gates adapt the existing `seo-agent-team` knowledge:
brief/SERP strategy, SEO writing, editorial review, fact/compliance audit, and
final SEO audit. The source vault remains external reference material and is
not copied into this template.
