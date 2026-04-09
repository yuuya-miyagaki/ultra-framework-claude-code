# Ultra Framework Claude Code

## Operating Contract

- Use this project with a thin Claude Code operating model.
- Claude is the orchestrator and should stay in control of routing.
- Hard gates require explicit user approval before crossing them.
- Completion claims must point to evidence, not chat confidence.
- Load only the documents required for the current task.

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
- Do not enter `qa` before `review` approval.
- Do not enter `security` before `qa` approval.
- Do not claim completion before the required evidence exists.

There is no separate `implement` approval key. Entry into `implement` is
already controlled by `plan` approval.

## Routing

- Use `planner` for ambiguity, design, and implementation planning.
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

## Source of Truth

- Operating rules: `CLAUDE.md`
- Current phase and next action: `docs/STATUS.md`
- Requirements: `docs/requirements/*`
- Design and planning artifacts: `docs/specs/*`, `docs/plans/*`
- Review, QA, and security evidence: `docs/qa-reports/*`
- Actual behavior: code, tests, and command output

## Completion Rule

A task is only complete when:

- the relevant artifact exists
- the relevant checks have been run or explicitly skipped with reason
- `docs/STATUS.md` points to the active refs
- blockers and residual risks are recorded
- the user-facing completion summary is evidence-based

## Project Overrides

Use this section in real projects to add only project-specific rules such as:

- stack-specific commands
- naming conventions
- deployment constraints
- paths that require special care

Do not duplicate the control-kernel sections above.
