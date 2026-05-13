Agent must always respond in Japanese
Answering in Japanese only, except when it required by the user.
Readme and commit comment must be in English
As an option make readme in Japanese for a reference but public repositories are in English
in order to .env or necessary secret data/files, it is not exist because blocked for AI, so ask user to edit or make it
Ask review, and implemantation plan also in Japanese.


@RTK.md
# Agent Operating Rules

## Repository Scope (Critical)

All file operations MUST be performed relative to the repository root.

The repository root is the directory where this AGENTS.md file exists.

The agent MUST NOT search outside of the repository root.

The agent MUST NOT use absolute paths like `/`, `/home`, `/Users`, etc.

All paths must be treated as:

- `./state/current.md`
- `./logs/worklog.md`

## Mandatory State Handling

Before starting any work, the agent MUST read:

- `./state/current.md`
- `./logs/worklog.md`

If these files do not exist, the agent MUST create them in the repository root.

The agent MUST NOT search for similarly named files outside the repository.

## State Update Rules

The agent MUST update:

- `./state/current.md`
- `./logs/worklog.md`

These paths are fixed and must not be changed.

1. Before starting a new task or subtask
2. Before making a risky or broad change
3. After completing a meaningful step
4. When blocked
5. Before stopping work, handing off, or when context may be lost

`state/current.md` must always describe the latest active state only.


## Failure Handling

If the agent cannot locate the repository root or access the above files:

- STOP immediately
- Do NOT continue work
- Report the issue

## Worklog Rules

The agent MUST append to `logs/worklog.md` after each meaningful unit of work.

The worklog is append-only. Do not rewrite old entries unless explicitly instructed.

Each entry must include:

- Timestamp
- Task
- Result
- Files changed
- Next action
- Blockers, if any

## Required Format for state/current.md

```md
# Current State

## Active Task
Briefly describe the current task.

## Current Status
What has been completed so far.

## Next Action
The next concrete action to take.

## Blockers
Known problems, errors, or unclear points.

## Relevant Files
- path/to/file
- path/to/another-file

## Handover Note
Short instruction for the next agent/model/session.