# Ultra Framework Claude Code

## Operating Contract

- Use this project with a thin Claude Code operating model.
- Claude is the orchestrator and should stay in control of routing.
- Hard gates require explicit user approval before crossing them.
- Completion claims must point to evidence, not chat confidence.
- Load only the documents required for the current task.
- Stop after 3 consecutive failures on the same error. Do not retry with the
  same approach — report the blocker to the user.
- Never run destructive commands (`push --force`, `reset --hard`, `rm -rf`,
  `DROP`, branch deletion) without explicit user approval.

## Session Start

1. Read `docs/STATUS.md`.
2. Read only the `current_refs` relevant to the task.
3. Pull extra docs only when a dependency appears.
4. Invoke a subagent only when specialist isolation reduces risk or context.
5. Update `docs/STATUS.md` when the active phase, refs, blockers, or next step
   change.

## State Machine

This framework uses a two-layer model:

- Modes: `Client`, `Dev`
- Client phases: `onboard -> discovery -> requirements -> scope -> acceptance -> handover`
- Dev phases: `onboard -> brainstorm -> plan -> implement -> review -> qa -> security -> ship -> docs`

Mode transitions are controlled by mode-transition gates:

- `client_ready_for_dev`: required before entering `Dev`
- `dev_ready_for_client`: required before handing back to `Client`

Client mode does not use per-phase gates. Client work is controlled by
artifact readiness and the `client_ready_for_dev` gate only.

Phase progression is controlled by gate approvals in `docs/STATUS.md`:

- Do not enter `plan` before `brainstorm` approval.
- Do not enter `implement` before `plan` approval.
- Do not write production code before a failing test exists.
- Do not enter `qa` before `review` approval.
- Do not enter `security` before `qa` approval.
- Do not claim completion before the required evidence exists.

There is no separate `implement` approval key. Entry into `implement` is
already controlled by `plan` approval.

## Routing

- Run `brainstorm` in the main context (requires user dialogue).
- Use `planner` for design notes and implementation plans.
- Use `implementer` for code and test changes.
- Use `reviewer` for fresh-context review and findings.
- Use `qa` for validation, reproduction, and QA reports.
- Use `security` for security-focused review and residual risk notes.
- Use `ui` only for UI or UX-heavy work.

Default rule: do not invoke subagents by habit. Invoke them when they make the
work clearer, safer, or smaller.

## Context Budget Policy

- Always-on context is limited to `CLAUDE.md` and `docs/STATUS.md`.
- Prefer repo files over long chat history.
- Keep detailed reads pull-based.
- Avoid opening more than three detailed docs at once unless blocked.
- Summarize at phase transitions, not after every micro-step.
- Keep `docs/STATUS.md` short and current rather than replaying prior sessions.

## Skills

Skills are conceptual references, not file paths. They are maintained in the
framework repository and not copied into each project. Load by name when needed:

- brainstorming: design phase (brainstorm)
- test-driven-development: implementation phase (implement)
- subagent-development: multi-task implementation
- session-recovery: context loss or session restart

## Source of Truth

- Operating rules: `CLAUDE.md`
- Current phase and next action: `docs/STATUS.md`
- Requirements: `docs/requirements/*`
- Design and planning artifacts: `docs/specs/*`, `docs/plans/*`
- Review, QA, and security evidence: `docs/qa-reports/*`
- Skills and process guides: referenced by name (see Skills section above)
- Actual behavior: code, tests, and command output

## Completion Rule

A task is only complete when:

- the relevant artifact exists
- the relevant checks have been run or explicitly skipped with reason
- `docs/STATUS.md` points to the active refs
- blockers and residual risks are recorded
- the user-facing completion summary is evidence-based

## Project Overrides

- Use `pnpm` for project-level commands.
- Treat the current search data source as a mock index until the real backend is
  approved.
