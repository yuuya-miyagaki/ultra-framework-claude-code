# Ultra Framework Claude Code

Ultra Framework Claude Code is a Claude Code native distribution of Ultra
Framework v7 principles.

It keeps the strongest parts of v7:

- explicit phase control
- user-approved hard gates
- evidence-based completion
- durable handover and restart artifacts

It removes the parts that add overhead in Claude Code:

- `.agents/AGENTS.md` as the primary entrypoint
- broad host-neutral instruction loading
- large always-on rule sets
- unnecessary token-heavy routing

## Design Priorities

- Thin working context by default
- Explicit operational state in `docs/STATUS.md`
- Pull-based document loading
- Small subagent surface area
- Low token waste

## Repository Structure

```text
ultra-framework-claude-code/
├── CLAUDE.md
├── .claude/agents/
├── docs/
├── templates/
├── scripts/
└── examples/minimal-project/
```

## Core Model

- `CLAUDE.md` is the control kernel
- `docs/STATUS.md` is the operational state index
- canonical docs under `docs/` are the source of project truth
- `.claude/agents/` holds bounded specialist roles
- `templates/` is the project bootstrap source

## Quick Start

1. Read [CLAUDE.md](CLAUDE.md)
2. Copy the files you need from `templates/` into a project repo
3. Copy `.claude/agents/` into the project if you want the default specialist set
4. Initialize `docs/STATUS.md`
5. Validate the scaffold before use

## Validation

From this repository root:

```bash
python3 scripts/check_framework_contract.py
python3 scripts/check_status.py --root .
python3 scripts/check_status.py --root examples/minimal-project
```

## Relationship to Ultra Framework v7

- `ultra-framework-v7` remains the stable, host-neutral framework line
- `ultra-framework-claude-code` is the Claude Code optimized distribution
- conceptual migration guidance lives in
  [docs/MIGRATION-FROM-v7.md](docs/MIGRATION-FROM-v7.md)

## Language Policy

- control files are written in English
- project-facing docs are written in Japanese by default
- if a team uses another language, update templates and validation together
