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
├── hooks/
├── templates/
├── scripts/
└── examples/minimal-project/
```

## Core Model

- `CLAUDE.md` is the control kernel
- `docs/STATUS.md` is the operational state index
- canonical docs under `docs/` are the source of project truth
- `.claude/agents/` holds bounded specialist roles
- `hooks/` provides runtime enforcement via Claude Code hooks
- `templates/` is the project bootstrap source

## Quick Start

1. Read [CLAUDE.md](CLAUDE.md)
2. Copy `templates/CLAUDE.template.md` as your project's `CLAUDE.md`
3. Copy the templates you need from `templates/` into your project's `docs/`
4. Copy `.claude/agents/` into the project if you want the default specialist set
5. Initialize `docs/STATUS.md` from `templates/STATUS.template.md`
6. Validate the scaffold before use

**Skills** (`docs/skills/`) are framework-level reference documents. They are
not copied into each project — Claude reads them from the framework repository
when needed. Project CLAUDE.md references skills by name, not by file path.

**Hooks** (`hooks/`) enforce framework rules at runtime. Copy
`templates/hooks.template.json` into your project's `.claude/settings.local.json`
and copy the `hooks/` directory into the project root. The hooks provide:

- **SessionStart**: injects current mode, phase, and blockers from STATUS.md
- **PreToolUse (Edit/Write)**: blocks code edits when plan gate is not approved
- **PreToolUse (Bash)**: warns before destructive commands

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
