# Ultra Framework Claude Code

## Operating Contract

- Thin Claude Code operating model. Claude orchestrates routing.
- Hard gates require explicit user approval.
- Completion requires evidence, not chat confidence.
- Load only docs required for the current task.
- Use framework phases, not `EnterPlanMode`.
- Persist lessons in `docs/LEARNINGS.md`, not auto-memory.
- Stop after 3 failures toward the same goal: write `docs/second-opinion.md`,
  update STATUS.md blockers, recommend IDE chat, then wait.
  Count by goal, not method. TDD red-to-green cycles excluded.
- Destructive commands require explicit user approval. Enforce via hooks (PaC).

## Session Start

1. Read `docs/STATUS.md`.
2. Read only `current_refs` relevant to the task.
3. Pull extra docs only when a dependency appears.
4. Invoke subagents only when isolation reduces risk or context.
5. Update `docs/STATUS.md` when phase, refs, blockers, or next step change.

## State Machine

- Modes: `Client`, `Dev`
- Client phases: `onboard -> discovery -> requirements -> scope -> acceptance -> handover`
- Dev phases: `brainstorm -> plan -> implement -> review -> qa -> security -> deploy -> ship -> docs`

Mode gates:

- `client_ready_for_dev`: required before entering `Dev`
- `dev_ready_for_client`: required before handing back to `Client`

In `Client`, load `docs/skills/client-workflow.md`.
Only `client_ready_for_dev` moves work to `Dev`.

Before `brainstorm`, reread `docs/STATUS.md`, confirm refs, and restate
objective, blockers, and next action. Required; not a phase.

`deploy`/`ship`/`docs` details live in their respective skills.

Iteration: after `dev_ready_for_client`, new task resets to `brainstorm`,
clears dev gates to `pending`, sets non-requirements refs to null,
increments `iteration`, keeps `current_refs.requirements`.

Phase transition: get approval → update gates/refs → update phase/next_action → invoke next route.

Phase gates:

- Do not enter a phase before its prior gate is approved.
  Task size routing overrides: skipped phases exempt their gates.
- Do not write production code before a failing test exists.
- Do not claim completion before the required evidence exists.

| type | required gates | S (1 file) | M (2-5) | L (6+) |
|------|---------------|------------|---------|--------|
| feature/refactor/framework | review+qa+security+deploy | impl→review→ship | skip deploy | all |
| bugfix | review; brainstorm+plan=n/a (bug-diagnosis) | same | same | same |
| hotfix | review preferred; brainstorm+plan=n/a (bug-diagnosis simplified) | same | same | same |

## Routing

- `brainstorm`: main context (requires user dialogue).
- `planner`: design notes and plans.
- `implementer`: code and test changes.
- `reviewer`: fresh-context review. `qa`: validation and QA reports.
- `security`: security review. `ui`: UI/UX-heavy work only.

- Use `reviewer-testing`/`reviewer-performance`/`reviewer-maintainability` as
  parallel specialists when diff-scope warrants.
- Default: subagents only when they make work clearer, safer, or smaller.

## Context Budget Policy

L0 `CLAUDE.md`+`STATUS.md` (always-on), L1 phase refs, L2 task files, L3 on-demand.

- Prefer repo files over chat history. Pull-based; max three docs at once.
- Summarize at phase transitions. Update `docs/STATUS.md` before pauses.

## Skills

- brainstorming
- bug-diagnosis
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
- Skills: `docs/skills/*`
- Actual behavior: code, tests, and command output

## Completion Rule

A task is only complete when:

- the relevant artifact exists
- zero-tool-call completions are invalid
- the relevant checks have been run or explicitly skipped with reason
- `docs/STATUS.md` points to the active refs
- blockers and residual risks are recorded
- the completion summary is evidence-based
