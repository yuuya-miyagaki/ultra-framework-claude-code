# Routing

- `brainstorm`: main context (requires user dialogue).
- `planner`: design notes and plans.
- `implementer`: code and test changes.
- `reviewer`: fresh-context review. `qa`: validation and QA reports.
- `security`: security review. `ui`: UI/UX-heavy work only.

- Use `reviewer-testing`/`reviewer-performance`/`reviewer-maintainability` as
  parallel specialists when diff-scope warrants.
- Default: subagents only when they make work clearer, safer, or smaller.
