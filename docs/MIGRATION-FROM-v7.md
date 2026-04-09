# Migration from Ultra Framework v7

This guide maps the stable v7 concepts into the Claude Code native
distribution.

## What Stays the Same

- phase and gate discipline
- user approval for hard gates
- evidence-based completion
- canonical project artifacts under `docs/`
- `docs/STATUS.md` as the restart index

## What Changes

| Ultra Framework v7 | Claude Code Edition |
|---|---|
| `.agents/AGENTS.md` entrypoint | root `CLAUDE.md` |
| broad host-neutral loading | Claude-native routing |
| large skill and mode catalog | small `.claude/agents/` set |
| status as flat key list | status with YAML frontmatter plus compact body |
| multiple validator scripts tuned for v7 | lightweight Claude Code validators |

## What Is Intentionally Removed

- `.agents/` as the primary runtime entrypoint
- always-on, large rule payloads
- host-neutral abstractions that increase token cost in Claude Code
- broad specialist catalogs that are not justified by current work

## Recommended Migration Sequence

1. keep your existing v7 repo untouched
2. create a fresh Claude Code project scaffold from this distribution
3. copy or adapt the canonical docs from your v7 project
4. rewrite project `CLAUDE.md` to use the thin-kernel pattern
5. migrate active work into the new `docs/STATUS.md` schema
6. add only the subagents that you truly use

## Practical Mapping

### Entry Point

- v7: start from `.agents/AGENTS.md`
- Claude Code edition: start from `CLAUDE.md`

### Specialist Logic

- v7: broad skill loading via `.agents/`
- Claude Code edition: bounded specialist invocation via `.claude/agents/`

### Current Work State

- v7: flat key-value status index
- Claude Code edition: compact frontmatter with `current_refs`,
  `gate_approvals`, mode, phase, and next action

### Validation

- v7: richer validator family oriented around the original contract
- Claude Code edition: lighter validators focused on the control plane and
  project scaffold integrity
