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
- Policy as Code (PaC) via hooks

## Repository Structure

```text
ultra-framework-claude-code/
├── CLAUDE.md                    # control kernel (~320 words)
├── .claude/
│   ├── agents/                  # 9 bounded specialist roles
│   ├── commands/                # slash commands (/status, /gate, etc.)
│   ├── rules/                   # always-loaded rules (state-machine, routing)
│   └── skills/                  # pull-based skill documents
├── docs/
├── hooks/                       # runtime enforcement (PaC)
│   └── lib/                     # shared hook utilities
├── templates/
├── scripts/
└── examples/minimal-project/
```

## Core Model

- `CLAUDE.md` is the control kernel
- `.claude/rules/` holds always-loaded state machine and routing rules
- `docs/STATUS.md` is the operational state index
- canonical docs under `docs/` are the source of project truth
- `.claude/agents/` holds bounded specialist roles with enriched frontmatter
- `.claude/skills/` holds pull-based skill documents (native mechanism)
- `.claude/commands/` provides slash commands for common operations
- `hooks/` provides runtime enforcement via Claude Code hooks
- `templates/` is the project bootstrap source

## Quick Start

1. Read [CLAUDE.md](CLAUDE.md)
2. Copy `templates/CLAUDE.template.md` as your project's `CLAUDE.md`
3. Copy the templates you need from `templates/` into your project's `docs/`
4. Copy `.claude/agents/` into the project if you want the default specialist set
5. Copy `.claude/skills/` into the project for skill documents
6. Copy `.claude/rules/` into the project for state machine and routing rules
7. Copy `.claude/commands/` into the project for slash commands
8. Initialize `docs/STATUS.md` from `templates/STATUS.template.md`
9. Copy `templates/hooks.template.json` into `.claude/settings.local.json`
   and copy the `hooks/` directory (including `hooks/lib/`) into the project root
   (use `settings.local.json` for real projects so it can be gitignored;
   the example uses `settings.json` as a committed sample)
10. Copy `scripts/update-gate.sh` into the project's `scripts/` directory
    (required by the `/gate` command for gate approvals)
11. Validate the scaffold before use

**Skills** (`.claude/skills/`) are loaded by Claude Code natively. Each skill
has a `SKILL.md` with frontmatter (`disable-model-invocation: true` for
pull-based loading). Project CLAUDE.md references skills by name.

**Commands** (`.claude/commands/`) provide slash commands:

| Command | Purpose |
|---------|---------|
| `/status` | Display formatted STATUS.md summary |
| `/gate` | List and approve gates |
| `/recover` | Invoke session recovery |
| `/validate` | Run framework validators |
| `/next` | Show next action and phase transition suggestions |

**Hooks** (`hooks/`) enforce framework rules at runtime:

- **SessionStart**: injects current mode, phase, blockers; initializes gate snapshot
- **PreToolUse (Edit/Write)**: blocks code edits when plan gate is not approved;
  blocks framework file edits during non-framework tasks
- **PreToolUse (Bash)**: warns before destructive commands
- **PostToolUse (Bash)**: captures exit codes and error context
- **PostToolUse (Edit/Write)**: detects unauthorized gate tampering in STATUS.md

## Validation

From this repository root:

```bash
python3 scripts/check_framework_contract.py
python3 scripts/check_status.py --root .
python3 scripts/check_status.py --root examples/minimal-project
```

Optional strict YAML validation (requires PyYAML):

```bash
pip install pyyaml
python3 scripts/check_status.py --root . --strict
```

## Migration from v0.5.0

Key changes in v0.6.0:

1. **Skills moved**: `docs/skills/` → `.claude/skills/*/SKILL.md`
2. **Rules extracted**: State Machine and Routing moved from CLAUDE.md to `.claude/rules/`
3. **Commands added**: 5 slash commands in `.claude/commands/`
4. **Trust boundary hardened**: `check-gate.sh` blocks framework file edits;
   `post-status-audit.sh` detects gate tampering
5. **Hook library**: shared `hooks/lib/extract-input.sh` for input parsing
6. **Agent frontmatter enriched**: `model`, `permissionMode`, `effort`, `color` fields
7. **Agent language unified**: all agent files now in English
8. **CLAUDE.md slimmed**: 583 → 320 words

## Relationship to Ultra Framework v7

- `ultra-framework-v7` remains the stable, host-neutral framework line
- `ultra-framework-claude-code` is the Claude Code optimized distribution
- conceptual migration guidance lives in
  [docs/MIGRATION-FROM-v7.md](docs/MIGRATION-FROM-v7.md)

## Language Policy

- control files are written in English: `CLAUDE.md`, `.claude/agents/`,
  `.claude/commands/`, `.claude/rules/`, `hooks/`, `scripts/`
- skills (`.claude/skills/`) follow the project documentation language
  (they are user-facing reference documents loaded on demand)
- project-facing docs are written in Japanese by default
- if a team uses another language, update templates and validation together
