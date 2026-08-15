# SEO Coordinator Architecture

## Position

`seo-coordinator` is the control-plane Agent for the `seo-editorial`
department. The Researcher, Writer, and Reviewer remain independent data-plane
Agents.

## Communication

Control messages use Trinity MCP `chat_with_agent`. Research packets, drafts,
review results, and history use the permitted shared workspace. The Coordinator
passes references and state, not large document bodies, through messages.

## Invariants

- The Reviewer remains independent from the Writer.
- The Coordinator cannot approve publication.
- A Reviewer FAIL returns to the Writer and increments the attempt count.
- Attempt three escalates to the operator and terminates automation.
