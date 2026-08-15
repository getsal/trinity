# SEO Writer Architecture

This is an independent Writer runtime. It consumes the Researcher's packet,
produces the Japanese SEO draft, and sends it to `seo-reviewer` using Trinity
MCP. It revises on FAIL, up to three review attempts, but never approves its
own work.
