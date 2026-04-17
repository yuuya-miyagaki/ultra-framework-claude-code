---
framework: ultra-framework-claude-code
framework_version: "0.8.0"
project_name: "Ultra Framework Claude Code"
mode: Dev
phase: docs
task_type: framework
task_size: L
task_size_rationale: "Client モード強化。translation artifact, agent 1体, skill 1つ, hook 1つ, テンプレート3つ, ディレクトリ3つ, 既存ファイル多数更新。推定20ファイル。"
iteration: 3
ui_surface: false
last_updated: "2026-04-17T12:00:00Z"
gate_approvals:
  client_ready_for_dev: n/a
  brainstorm: approved
  plan: approved
  review: approved
  qa: approved
  security: approved
  deploy: approved
  dev_ready_for_client: pending
current_refs:
  requirements: []
  plan: "docs/plans/v080-client-enhancement-plan.md"
  spec: "docs/specs/v080-client-enhancement-brainstorm.md"
  review: "docs/qa-reports/v080-review.md"
  qa: "docs/qa-reports/v080-qa.md"
  security: "docs/qa-reports/v080-security.md"
  deploy: "docs/plans/v080-client-enhancement-plan.md"
  translation: null
external_evidence:
  - type: "client-mode-enhancement-proposal"
    scope: "v0.8.0 Client モード強化 10ステップ提案"
    findings: "translation フェーズ新設提案、Agent 5体+Skill 6つ+Hook 4つの全面拡張案"
    resolution: "2名のレビューを経て最小拡張案に絞込み。translation は artifact-first、Agent 2→1体、Hook 4→1つ"
next_action: "v0.8.0 docs フェーズ完了。README migration + LEARNINGS 更新済み。コミット待ち。"
blockers: []
session_history:
  - date: "2026-04-16"
    mode: Dev
    phase: "brainstorm"
    note: "v0.7.3 Skills & MCP 改善調査レポート作成。4フレームワーク比較+Web調査+ギャップ分析。3本柱スコープ決定。"
  - date: "2026-04-17"
    mode: Dev
    phase: "docs"
    note: "v0.7.3 実装完了+コミット。qa-verification skill, agent skills preload, MCP catalog。レビュー指摘5件修正。"
  - date: "2026-04-17"
    mode: Dev
    phase: "ship"
    note: "v0.8.0 Client モード強化 実装+全ゲート通過+コミット+プッシュ。48ファイル変更。translation artifact必須化, agent/skill/hook/テンプレート追加。"
---

## Summary

Claude Code ネイティブの Ultra Framework 運用フレームワーク。v0.8.0 では
Client モード強化: translation artifact 必須化、translation-specialist agent 追加、
docs/client/ + docs/translation/ + docs/decisions/ ディレクトリ新設、
check-client-info.sh hook 追加。

## Recent Decisions

- v0.8.0 スコープは最小拡張案。10ステップ全面提案から2名レビューを経て絞込み。
- translation は「独立 phase」ではなく「handover 前必須 artifact」として導入。
- Agent は translation-specialist 1体のみ（5体提案から絞込み）。
- Hook は check-client-info.sh 1つのみ（4つ提案から絞込み）。
- STATUS.md 拡張は client_context: { client_id, context_loaded } のみ。
- 新プロファイル（client-heavy, solo-consultant）は Phase B 以降に延期。

## Session History

- 2026-04-15: v0.7.0-v0.7.2 実装。ネイティブ機能改善、scaffold自己完結性、信頼境界ハードニング。
- 2026-04-17: v0.7.3 実装完了+コミット。qa-verification skill, agent skills preload, MCP catalog。
- 2026-04-17: v0.8.0 Client モード強化 実装完了+全ゲート通過+コミット+プッシュ (e186a18)。48ファイル変更。
