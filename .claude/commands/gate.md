---
description: Show gate approvals and approve gates via the authorized script
allowed-tools: Read, Bash
---

# /gate

Show current gate approvals and optionally approve a gate.

Usage: `/gate` or `/gate approve <gate-name>`

## Display mode (no arguments)

1. Read `docs/STATUS.md`
2. Display all gate_approvals with status
3. Show which gate is the next expected approval based on current phase

## Approve mode (`$ARGUMENTS` contains "approve")

1. Read `docs/STATUS.md`
2. Parse the gate name from arguments
3. **Pre-validation check**: For gates with ref mappings (plan, review, qa, security, deploy), verify `current_refs.<gate>` is set. If empty, display the ref status and warn the user before proceeding. This will become a hard block in v0.13.0.
4. Confirm with the user: "Approve {gate} gate? This advances the workflow."
5. On confirmation, run:

```bash
bash scripts/update-gate.sh <gate-name>
```

This script is the ONLY authorized way to approve gates. It updates STATUS.md and .gate-snapshot atomically.

**Do NOT edit STATUS.md gate fields directly with Edit/Write.** Direct edits will be denied by the gate tamper detection hook.

Valid gates: client_ready_for_dev, brainstorm, plan, review, qa, security, deploy, dev_ready_for_client

Do not approve gates without explicit user confirmation.
