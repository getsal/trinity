# /run-seo-pipeline

Run the bounded SEO pipeline for one case.

1. Load the brief and `templates/case-state.yaml`.
2. Invoke Researcher and validate the research packet.
3. Invoke Writer and validate the draft.
4. Invoke Reviewer.
5. On `PASS`, write the final handoff.
6. On `FAIL`, pass review notes to Writer and repeat from step 3.
7. Stop after three review attempts with `BLOCKED_FOR_HUMAN`.

Never skip a state transition. Summarize status, artifact paths, decision, and
next action in the final response.
