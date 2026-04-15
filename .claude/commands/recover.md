---
description: Invoke session recovery protocol
allowed-tools: Read, Bash, Glob, Grep
---

# /recover

Invoke the `session-recovery` skill to restore session state.

1. Load the `session-recovery` skill from `.claude/skills/session-recovery/SKILL.md`
2. Follow the recovery protocol steps:
   - Read `docs/STATUS.md`
   - Read current phase refs
   - Check git status
   - Detect partial artifacts
   - Report recovery summary to user
3. Wait for user confirmation before resuming work
