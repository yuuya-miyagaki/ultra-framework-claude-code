# Routing

## Agent roles

- `brainstorm`: runs in session context (not a subagent) because it requires live user dialogue.
- `planner`: design notes, plans, boundary maps. Subagent when plan scope is well-defined.
- `implementer`: code and test changes. Subagent for isolated file sets.
- `reviewer`: fresh-context code review (no prior session state).
- `qa`: validation runs and QA report generation.
- `security`: security-focused review.
- `ui`: UI/UX-heavy work only (visual components, styling).
- `qa-browser`: browser-based QA verification (delegated by qa agent when UI verification needed).
- `integration-specialist`: external service integration (API setup, OAuth, webhooks).
- `translation-specialist`: Client→Dev handover translation support.

## Specialist reviewers

Use `reviewer-testing`/`reviewer-performance`/`reviewer-maintainability` as
parallel specialists when the diff touches 5+ files or spans multiple concerns.

## Browser automation

`browser-assist` skill is available for any agent needing browser automation
($B or Playwright MCP). Use when the task involves UI verification or web interaction.

## Default rule

Subagents only when they make work clearer, safer, or smaller.
When in doubt, keep work in the session context.
