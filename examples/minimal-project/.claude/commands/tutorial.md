---
description: Phase transition walkthrough guide for learning the Dev flow
allowed-tools: Read
---

# Tutorial: Phase Transition Walkthrough

Walk through the framework's Dev flow to experience phase transitions and gates.

## Preparation

1. Read `docs/STATUS.md`
2. Note the current `phase` and `gate_approvals`

## Dev Flow (5 steps)

1. **brainstorm** — State the problem clearly. Ask the user to approve the brainstorm gate via `/gate`.
2. **plan** — Write an implementation plan in `docs/plans/`. Ask for plan gate approval.
3. **implement** — Write a failing test first (TDD), then make it pass. Code edits are blocked until the plan gate is approved.
4. **review** — Run `/gate` to approve the review gate. Invoke the reviewer agent for a fresh-context check.
5. **ship** — Approve remaining gates (`qa`, `security`, `deploy`). Update `docs/STATUS.md` with completion evidence.

## Key Points

- Use `/gate` at each transition to check and approve gate status.
- Update `docs/STATUS.md` every time the phase, refs, or blockers change.
- Completion without evidence violates the Completion Rule — hooks will block it.
- Use `/status` to see the current state at any time.
- Use `/next` for suggestions on what to do next.
