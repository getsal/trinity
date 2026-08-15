# SEO Coordinator

The dedicated orchestration member of the `seo-editorial` Team. It is a
team-only runtime and is not intended for standalone deployment.

The Coordinator is the operator's single entrypoint. It routes work to the
Researcher, Writer, and Reviewer, tracks the case state, and returns the final
result. It does not research, write, review, or approve content.

Use the Team manifest at
[`config/agent-teams/seo-editorial-team`](../agent-teams/seo-editorial-team)
for deployment and communication rules.
