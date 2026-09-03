---
description: Run a multi-agent read-only code review of uncommitted changes
agent: orchestrator
subtask: true
---
Review the current staged and unstaged changes, including untracked files.

Changed file status (untracked files appear here as `??`):
!`git status --porcelain=v1`

Tracked changes (staged + unstaged vs HEAD):
!`git diff HEAD`

If both the status and diff above are empty, respond exactly with "No changes to review."
and stop without invoking any specialists. Otherwise run the full review pipeline and
output the synthesised review grouped by severity. Untracked files listed above are in
scope -- read their contents directly when reviewing.
