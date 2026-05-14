# Current State

## Active Task
Finish Gemini runtime propagation so local templates create agents with `AGENT_RUNTIME=gemini-cli`.

## Current Status
Local template loading and Gemini runtime propagation are patched in code. `/api/templates` returns the local Gemini template, and `docker/base-image/startup.sh` now has a single simplified runtime export block that reads `/template/template.yaml` and exports `AGENT_RUNTIME` / `AGENT_RUNTIME_MODEL`.
The remaining blocker is re-running the rebuilt image path on the remote host and rechecking a fresh agent container, because the previous container still booted with `claude-code`.

## Next Action
Sync the cleaned startup script to the remote host, rebuild the base image if needed, restart backend, and recreate `test-gemini` to verify the Gemini env values.

## Blockers
Remote verification still needed; prior container already proved the old image path kept `claude-code`.

## Relevant Files
- src/backend/services/template_service.py
- src/backend/routers/templates.py
- src/backend/services/agent_service/crud.py
- docker/base-image/startup.sh
- config/agent-templates/test-gemini/template.yaml
- state/current.md
- logs/worklog.md

## Handover Note
Remote SSH is working. Continue from the in-flight build and finish the runtime verification.
