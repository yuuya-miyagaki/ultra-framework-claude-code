# Ultra Framework Claude Code

## Operating Contract

- Use this repository as a thin Claude Code operating model.
- Claude is the orchestrator and should stay in control of routing.
- Hard gates require explicit user approval before crossing them.
- Completion claims must point to evidence, not chat confidence.
- Load only the documents required for the current task.
- Use framework phases, not `EnterPlanMode`.
- Persist project lessons in `docs/LEARNINGS.md`, not auto-memory.
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

- Modes: `Client`, `Dev`
- Client phases: `onboard -> discovery -> requirements -> scope -> acceptance -> handover`
- Dev phases: `brainstorm -> plan -> implement -> review -> qa -> security -> ship -> docs`

Mode gates:

- `client_ready_for_dev`: required before entering `Dev`
- `dev_ready_for_client`: required before handing back to `Client`

In `Client`, load `docs/skills/client-workflow.md`.
Only `client_ready_for_dev` moves work to `Dev`.

Before `brainstorm`, reread `docs/STATUS.md`, confirm refs, and restate
objective, blockers, and next action. Required; not a phase.

`ship` writes `docs/handover/TO-CLIENT.md`; `docs` updates
`docs/LEARNINGS.md` and requests `dev_ready_for_client`.

Phase transition protocol:

- get approval for the current artifact or summary
- update `gate_approvals` and `current_refs`
- update `phase` and `next_action`, then invoke the next route

Phase gates:

- Do not enter `plan` before `brainstorm` approval.
- Do not enter `implement` before `plan` approval.
- Do not write production code before a failing test exists.
- Do not enter `qa` before `review` approval.
- Do not enter `security` before `qa` approval.
- Do not claim completion before the required evidence exists.

No separate `implement` approval key; `plan` approval controls entry.

Dev verification by task type:

- `feature`, `refactor`, `framework`: require `review`, `qa`, `security`.
- `bugfix`: require `review`; `qa` or `security` may be `n/a` with reason.
- `hotfix`: prefer `review`; `qa` or `security` may be deferred with reason.

## Routing

- Run `brainstorm` in the main context (requires user dialogue).
- Use `planner` for design notes and implementation plans.
- Use `implementer` for code and test changes.
- Use `reviewer` for fresh-context review and findings.
- Use `qa` for validation, reproduction, and QA reports.
- Use `security` for security-focused review and residual risk notes.
- Use `ui` only for UI or UX-heavy work.

Default: use subagents only when they make work clearer, safer, or smaller.

## Context Budget Policy

- Always-on context is limited to `CLAUDE.md` and `docs/STATUS.md`.
- Prefer repo files over long chat history.
- Keep detailed reads pull-based.
- Avoid opening more than three detailed docs at once unless blocked.
- Summarize at phase transitions, not after every micro-step.
- Keep `docs/STATUS.md` short and current rather than replaying prior sessions.
- Update `docs/STATUS.md` before long pauses or likely context compression.

## Skills

- brainstorming
- test-driven-development
- subagent-development
- client-workflow
- session-recovery
- ship-and-docs

Load skills only for the relevant phase or recovery scenario.
Do not preload.

## Source of Truth

- Operating rules: `CLAUDE.md`
- Current phase and next action: `docs/STATUS.md`
- Requirements: `docs/requirements/*`
- Design and planning artifacts: `docs/specs/*`, `docs/plans/*`
- Review, QA, and security evidence: `docs/qa-reports/*`
- Skills: `docs/skills/*`
- Actual behavior: code, tests, and command output

## Completion Rule

A task is only complete when:

- the relevant artifact exists
- the relevant checks have been run or explicitly skipped with reason
- `docs/STATUS.md` points to the active refs
- blockers and residual risks are recorded
- the user-facing completion summary is evidence-based
