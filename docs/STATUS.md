---
framework: ultra-framework-claude-code
framework_version: "0.1.0"
project_name: "Ultra Framework Claude Code"
mode: Dev
phase: ship
task_type: framework
last_updated: "2026-04-10T01:00:00Z"
gate_approvals:
  client_ready_for_dev: n/a
  brainstorm: approved
  plan: approved
  review: approved
  qa: approved
  security: approved
  dev_ready_for_client: approved
current_refs:
  requirements: []
  plan: docs/plans/2026-04-10-ultra-framework-claude-code-implementation-plan.md
  spec: null
  review: docs/qa-reports/bootstrap-review.md
  qa: docs/qa-reports/bootstrap-qa.md
  security: docs/qa-reports/bootstrap-security.md
next_action: "Use the scaffold on the first real project and collect adoption learnings."
blockers: []
session_history:
  - date: "2026-04-10"
    mode: Dev
    phase: "brainstorm"
    note: "Approved the Claude-native design and implementation direction."
  - date: "2026-04-10"
    mode: Dev
    phase: "ship"
    note: "Bootstrapped the repository, validated the contract, and recorded review, QA, and security evidence."
---

## Summary

This repository now contains the first Claude Code native distribution of Ultra
Framework.

The initial V0 includes:

- the thin `CLAUDE.md` control kernel
- the explicit `docs/STATUS.md` operational schema
- a bounded `.claude/agents/` set
- canonical templates and a minimal example project
- lightweight validators and bootstrap evidence notes

## Recent Decisions

- Keep `ultra-framework-v7` unchanged and build this distribution separately.
- Optimize for Claude Code first, not cross-host compatibility.
- Keep the specialist set small to reduce token and routing overhead.
- Treat V0 validation as structural and add richer checks only when a real need appears.

## Session History

- 2026-04-10: Design approved for a separate Claude Code distribution.
- 2026-04-10: Repository skeleton, templates, example project, and validators completed.
