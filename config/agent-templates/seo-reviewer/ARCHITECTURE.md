# SEO Reviewer Architecture

This is an independent Reviewer runtime. It consumes the Writer's draft and
the original research evidence, then returns PASS or actionable FAIL through
Trinity MCP. The third FAIL becomes `BLOCKED_FOR_HUMAN`; the Reviewer never
rewrites the draft.
