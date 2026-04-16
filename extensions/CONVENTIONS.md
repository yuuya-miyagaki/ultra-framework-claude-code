# Extension Conventions

## Structure

```text
extensions/<name>/
├── README.md        # Required: purpose, prerequisites, setup instructions
├── WORKFLOW.md      # Optional: step-by-step procedures
└── ...              # Optional: additional files
```

## Rules

1. Extensions are not included in `setup.sh --profile` (manual opt-in only).
2. Core must not depend on the existence of any extension (dependency direction: extension → core).
3. Agents used by an extension may live in core `.claude/agents/`.
4. Extensions may depend on core contracts: STATUS.md, gates, hooks, validators.
5. Extension-specific files must not be registered in `check_framework_contract.py`.
6. `README.md` must document prerequisites (e.g., required MCP servers).

## Core Guarantees

Extensions may depend on these stable core contracts:

- `docs/STATUS.md` frontmatter fields (`ui_surface`, `phase`, `task_type`, `task_size`)
- Gate approval mechanism (`/gate` command + `scripts/update-gate.sh`)
- Hook PaC enforcement (`.claude/settings.json` or `settings.local.json`)
- Validator infrastructure (`scripts/run_eval.py` + `scripts/check_framework_contract.py`)
