# Ultra Framework Claude Code

## Operating Contract

- Use this project with a thin Claude Code operating model.
- Claude is the orchestrator and should stay in control of routing.
- Hard gates require explicit user approval.
- Completion claims require evidence, not chat confidence.
- Load only the documents required for the current task.
- Use framework phases, not `EnterPlanMode`.
- Persist project lessons in `docs/LEARNINGS.md`, not auto-memory.
- Stop after 3 failures toward the same goal and report the blocker.
  Count by goal, not method — changing approach does not reset the count.
  TDD red-to-green cycles are excluded. Each test case is a separate goal.
- Never run destructive commands (`push --force`, `reset --hard`, `rm -rf`,
  `DROP`, branch deletion) without explicit user approval.
- Enforce rules via hooks and validators (Policy as Code).

## Session Start

1. Read `docs/STATUS.md`.
2. Read only the `current_refs` relevant to the task.
3. Pull extra docs only when a dependency appears.
4. Invoke a subagent only when isolation reduces risk or context.
5. Update `docs/STATUS.md` when phase, refs, blockers, or next step change.

## State Machine

- Modes: `Client`, `Dev`
- Client phases: `onboard -> discovery -> requirements -> scope -> acceptance -> handover`
- Dev phases: `brainstorm -> plan -> implement -> review -> qa -> security -> deploy -> ship -> docs`

Mode gates:

- `client_ready_for_dev`: required before entering `Dev`
- `dev_ready_for_client`: required before handing back to `Client`

In `Client`, load `client-workflow`.
Only `client_ready_for_dev` moves work to `Dev`.

Before `brainstorm`, reread `docs/STATUS.md`, confirm refs, and restate
objective, blockers, and next action. Required; not a phase.

`deploy` runs `deploy` skill checklist (deploy-prep, staging, uat, production,
post-deploy). `ship` writes `docs/handover/TO-CLIENT.md`; `docs` updates
`docs/LEARNINGS.md` and requests `dev_ready_for_client`.

Phase transition protocol:

- get approval for the current artifact or summary
- update `gate_approvals` and `current_refs`
- update `phase` and `next_action`, then invoke the next route

Phase gates:

- Do not enter a phase before its prior gate is approved.
  Task size routing overrides: skipped phases exempt their gates.
- Do not write production code before a failing test exists.
- Do not claim completion before the required evidence exists.

Dev gates by task type:

- feature/refactor/framework: review + qa + security + deploy.
- bugfix: review only; rest n/a with reason.
- hotfix: review preferred; rest deferred with reason.

Task size (set in STATUS.md):

- S (1 file): implement → review → ship
- M (2-5 files): skip deploy
- L (6+): all Dev phases

## Routing

- Run `brainstorm` in the main context (requires user dialogue).
- Use `planner` for design notes and implementation plans.
- Use `implementer` for code and test changes.
- Use `reviewer` for fresh-context review and findings.
- Use `qa` for validation, reproduction, and QA reports.
- Use `security` for security review and residual risk notes.
- Use `ui` only for UI or UX-heavy work.

- Use `reviewer-testing`, `reviewer-performance`, `reviewer-maintainability`
  as parallel review specialists when diff-scope warrants.

Default: use subagents only when they make work clearer, safer, or smaller.

## Context Budget Policy

Context layers: L0 `CLAUDE.md` + `docs/STATUS.md` (always-on), L1 phase refs,
L2 task files, L3 history and external (on-demand).

- Prefer repo files over chat history.
- Pull-based reads; max three docs at once.
- Summarize at phase transitions only.
- Update `docs/STATUS.md` before pauses or context compression.

## Skills

- brainstorming
- test-driven-development
- subagent-development
- deploy
- client-workflow
- session-recovery
- ship-and-docs

Load skills for the current phase or recovery only.
Do not preload.

## Source of Truth

- Operating rules: `CLAUDE.md`
- Current phase and next action: `docs/STATUS.md`
- Requirements: `docs/requirements/*`
- Design and plans: `docs/specs/*`, `docs/plans/*`
- Review, QA, and security evidence: `docs/qa-reports/*`
- Skills: named skills
- Actual behavior: code, tests, and command output

## Completion Rule

A task is only complete when:

- the relevant artifact exists
- zero-tool-call completions are invalid
- the relevant checks have been run or explicitly skipped with reason
- `docs/STATUS.md` points to the active refs
- blockers and residual risks are recorded
- the completion summary is evidence-based

## Project Overrides

Add project-specific rules here. Do not duplicate the sections above.
