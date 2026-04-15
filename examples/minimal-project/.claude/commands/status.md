---
description: Display current STATUS.md state summary with phase hints
allowed-tools: Read, Bash
---

# /status

Read `docs/STATUS.md` and display a formatted summary:

1. Read `docs/STATUS.md`
2. Extract: mode, phase, task_type, task_size, iteration, next_action, blockers
3. Extract: gate_approvals (all gates with current status)
4. Extract: current_refs (non-null entries only)
5. Check if `docs/second-opinion.md` exists

Display as:

```
Ultra Framework Status
━━━━━━━━━━━━━━━━━━━━━
Mode: {mode} | Phase: {phase} | Size: {task_size} | Iteration: {iteration}
Task: {task_type}
Next: {next_action}
Blockers: {blockers or "none"}

Gates: {gate}={status} for each gate
Refs: {ref}={path} for non-null refs

{if second-opinion exists: "⚠ BLOCKER: docs/second-opinion.md exists"}
```

Do not modify any files. Display only.
