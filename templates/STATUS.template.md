---
framework: ultra-framework-claude-code
framework_version: "0.1.0"
project_name: ""
mode: Client
phase: onboard
task_type: feature
last_updated: ""
# gate name = phase whose output is approved; mode-transition gates unlock
# movement between Client and Dev
gate_approvals:
  client_ready_for_dev: pending
  brainstorm: pending
  plan: pending
  review: pending
  qa: pending
  security: pending
  dev_ready_for_client: pending
current_refs:
  requirements:
    - docs/requirements/PRD.md
    - docs/requirements/SCOPE.md
    - docs/requirements/NFR.md
    - docs/requirements/ACCEPTANCE.md
  plan: null
  spec: null
  review: null
  qa: null
  security: null
token_budget:
  model: opus
  estimated_tasks: 0
  notes: ""
next_action: ""
blockers: []
session_history:
  - date: ""
    mode: ""
    phase: ""
    note: ""
---

## Summary

- 現在の状況を 3〜5 行で簡潔に記録する
- 詳細本文は別ファイルに置き、ここは index と next step に集中する

## Recent Decisions

- 重要な判断だけを箇条書きで残す

## Session History

- 最新 3〜5 件だけを保持する
