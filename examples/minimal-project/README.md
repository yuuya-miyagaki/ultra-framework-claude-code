# Minimal Project Example

This example shows the intended happy path for a small Claude Code project
using Ultra Framework Claude Code.

## Included

- root `CLAUDE.md`
- `docs/STATUS.md`
- canonical requirement documents
- one design note
- one implementation plan
- review, QA, and security evidence
- handover documents
- `.claude/agents/` — bounded specialist roles (10 agents)
- `.claude/commands/` — slash commands (`/status`, `/gate`, `/next`, `/recover`, `/validate`)
- `.claude/rules/` — always-loaded state machine and routing rules
- `.claude/skills/` — pull-based skill documents (8 skills)
- `.claude/settings.json` — hooks configuration
- `hooks/` — runtime enforcement hooks (including `hooks/lib/`)
- `scripts/update-gate.sh` (required by `/gate` command for gate approvals)
- `scripts/check_status.py` (required by `/validate` command for status validation)

## Validate

Run from the framework repository root:

```bash
python3 scripts/check_status.py --root examples/minimal-project
```
