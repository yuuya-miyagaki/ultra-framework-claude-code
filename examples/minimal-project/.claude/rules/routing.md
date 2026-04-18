# Routing

- `brainstorm`: main context (requires user dialogue).
- `planner`: design notes and plans.
- `implementer`: code and test changes.
- `reviewer`: fresh-context review. `qa`: validation and QA reports.
- `security`: security review. `ui`: UI/UX-heavy work only.
- `qa-browser`: browser-based QA verification (delegated by qa agent).
- `integration-specialist`: external service integration (API setup, OAuth, webhooks).

- Use `reviewer-testing`/`reviewer-performance`/`reviewer-maintainability` as
  parallel specialists when diff-scope warrants.
- Default: subagents only when they make work clearer, safer, or smaller.
