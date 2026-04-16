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
│   ├── agents/                  # 10 bounded specialist roles
│   ├── commands/                # slash commands (/status, /gate, etc.)
│   ├── rules/                   # always-loaded rules (state-machine, routing)
│   └── skills/                  # pull-based skill documents
├── docs/
├── hooks/                       # runtime enforcement (PaC)
│   └── lib/                     # shared hook utilities
├── templates/
├── scripts/
├── extensions/                  # optional addons (manual opt-in)
│   └── qa-browser/              # browser QA workflow
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

### Automated setup (recommended)

```bash
bin/setup.sh --profile=standard --target=<your-project-dir>
```

Available profiles: `minimal` (core only), `standard` (recommended), `full` (everything including agents).

### Manual setup

1. Read [CLAUDE.md](CLAUDE.md)
2. Copy `templates/CLAUDE.template.md` as your project's `CLAUDE.md`
3. Copy the templates you need from `templates/` into your project's `docs/`
4. Copy `.claude/rules/` into the project for state machine and routing rules
5. Copy `.claude/commands/` into the project for slash commands
6. Copy `hooks/` directory and generate `.claude/settings.local.json` from `templates/hooks.template.json`
7. Copy `scripts/check_status.py` and `scripts/update-gate.sh` into the project
8. Validate the scaffold before use

**Skills** (`.claude/skills/`) are loaded by Claude Code natively. Each skill
has a `SKILL.md` with frontmatter (`disable-model-invocation: true` for
pull-based loading). Project CLAUDE.md references skills by name.

**Commands** (`.claude/commands/`) provide slash commands:

| Command | Purpose |
|---------|---------|
| `/status` | Display formatted STATUS.md summary |
| `/gate` | List and approve gates |
| `/recover` | Invoke session recovery |
| `/validate` | Run tiered framework evaluation |
| `/next` | Show next action and phase transition suggestions |
| `/retro` | Generate retrospective report |

**Hooks** (`hooks/`) enforce framework rules at runtime:

- **SessionStart**: injects current mode, phase, blockers; initializes gate snapshot
- **PreToolUse (Edit/Write/NotebookEdit)**: blocks code edits when plan gate is not approved;
  blocks framework file edits during non-framework tasks
- **PreToolUse (Bash)**: denies control plane file writes during non-framework tasks;
  warns before destructive commands
- **PostToolUse (Bash)**: captures exit codes and error context
- **PostToolUse (Edit/Write/NotebookEdit)**: detects unauthorized gate tampering in STATUS.md
- **PreCompact**: blocks compaction when STATUS.md is stale (not updated within 5 min during active phase); allows with context summary when current

## Validation

From this repository root:

```bash
python3 scripts/run_eval.py --tier 1
```

Profile-based validation for scaffold projects:

```bash
python3 scripts/check_framework_contract.py --profile=standard --root examples/minimal-project
```

Available profiles: `minimal` (4 core files), `standard` (14 required + 7 recommended). `full` is framework repo root only (do not use with `--root`).
Profile definitions: `templates/profiles/*.json`.

Optional strict YAML validation (requires PyYAML):

```bash
pip install pyyaml
python3 scripts/check_status.py --root . --strict
```

## Migration

### From v0.7.1 to v0.7.2

1. **check-control-plane.sh added**: new Bash PreToolUse hook that denies
   control plane file writes (STATUS.md, CLAUDE.md, .claude/, hooks/, scripts/)
   during non-framework tasks; register in Bash PreToolUse before check-destructive.sh
2. **NotebookEdit added to matchers**: PreToolUse and PostToolUse matchers
   expanded from `Edit|Write` to `Edit|Write|NotebookEdit` (defense-in-depth)
3. **extract\_file\_path notebook\_path fallback**: `hooks/lib/extract-input.sh`
   now falls back to `notebook_path` when `file_path` is empty (NotebookEdit support)
4. **Template reference drift fixed**: corrected stale skill/agent names in
   PLAN, VERIFICATION, DEPLOY-CHECKLIST templates and session-start.sh
5. **`/validate` scaffold-safe**: example project's `/validate` now runs
   `check_status.py` only (not `check_framework_contract.py`)
6. **check\_status.py in Quick Start**: step 11 added for copying the script
   into scaffolded projects

### From v0.7.0 to v0.7.1

1. **PreCompact hook added**: `hooks/pre-compact.sh` blocks compaction when
   STATUS.md is stale (not updated within 5 min during active phase);
   register `PreCompact` in your hooks settings
2. **qa-browser agent added**: `.claude/agents/qa-browser.md` provides safe
   Playwright MCP access via `disallowedTools` (Edit/Write/NotebookEdit/Bash denied);
   update routing rules to include `qa-browser`
3. **QA agent updated**: browser QA section now delegates to qa-browser
   instead of the "Orchestrator Action Required" handoff
4. **Auto-memory policy relaxed**: CLAUDE.md now permits auto-memory for
   personal preferences (LEARNINGS.md remains primary for technical lessons)
5. **external\_evidence.type lint**: validator now warns on non-kebab-case type values
6. **`/next` enhanced**: suggests trimming body Session History when entries exceed 10
7. **subagent-dev TaskCreate clarified**: TaskCreate usage scoped to
   session-local subtask management only

### From v0.6.0 to v0.7.0

1. **STATUS.md schema expanded**: add `failure_tracking: null` and
   `task_size_rationale` fields to frontmatter
2. **Archive limits enforced**: `session_history` and `external_evidence` capped
   at 3 entries each; older entries archived to body or `docs/evidence-archive.md`
3. **Archive file**: create `docs/evidence-archive.md` for overflow evidence
4. **CLAUDE.md updated**: 3-failure rule now requires writing to
   `failure_tracking` (goal/count/last_attempt); reset to null on resolution
5. **Iteration reset**: `state-machine.md` updated — archive external_evidence
   older than latest 3 on iteration reset
6. **Skills updated**: brainstorming and bug-diagnosis skills now include
   `task_size_rationale` recording step

### From v0.5.0 to v0.6.0

1. **Skills moved**: `docs/skills/` → `.claude/skills/*/SKILL.md`
2. **Rules extracted**: State Machine and Routing moved from CLAUDE.md to `.claude/rules/`
3. **Commands added**: 5 slash commands in `.claude/commands/`
4. **Trust boundary hardened**: `check-gate.sh` blocks framework file edits;
   `post-status-audit.sh` detects gate tampering
5. **Hook library**: shared `hooks/lib/extract-input.sh` for input parsing
6. **Agent frontmatter enriched**: `model`, `permissionMode`, `effort`, `color` fields
7. **Agent language unified**: all agent files now in English
8. **CLAUDE.md slimmed**: 583 → 320 words

## Extensions

Optional addons that are not included in `setup.sh` profiles. Copy manually.

### qa-browser

Browser-based QA workflow using Playwright MCP. Provides a 4-step verification
process: Snapshot → Interact → Verify → Evidence Capture.

```bash
cp -r extensions/qa-browser <your-project>/extensions/qa-browser
```

See [extensions/qa-browser/README.md](extensions/qa-browser/README.md) for details.

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
