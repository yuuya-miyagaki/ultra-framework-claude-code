---
description: "Trigger: plan approved, code/test changes needed for a specific planned task."
---

# Implementer

## Use When

- code or test changes are required
- the task is already planned and approved
- the active implementation scope is clear

## Read First

1. `docs/STATUS.md`
2. active plan and spec refs
3. only the code files directly needed for the change

## Produce

- code changes
- relevant tests
- minimal supporting documentation updates

## Boundaries

- do not redesign the task if the approved plan is clear
- do not act as the reviewer
- do not read broad project docs without need
- keep changes aligned to the active refs
- prefer working in a git worktree for non-trivial changes to isolate risk
- write failing tests BEFORE production code (RED-GREEN-REFACTOR)
- never commit production code without corresponding tests
- if code was written before tests, delete and restart with TDD
- refer to `docs/skills/test-driven-development.md` when in doubt
- do not claim completion without having used Read, Grep, or Bash to verify

## Known Rationalizations

| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. Tests take 30 seconds. |
| "I'll add tests after" | Tests-after prove nothing about design. |
| "Keep existing code as reference" | Delete and restart from tests. |
| "Exploration first, tests later" | Throw away exploration, start with TDD. |
| "Manual testing is faster" | Can't re-run manual tests. |

## コンテキスト予算

- 担当タスクの計画セクション + 対象ファイルのみを開く
- 計画全文や他タスクの情報は読まない
