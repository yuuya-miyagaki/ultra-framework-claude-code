---
framework: ultra-framework-claude-code
framework_version: "0.9.0"
project_name: "Ultra Framework Claude Code"
mode: Dev
phase: ship
task_type: framework
task_size: M
task_size_rationale: "integration-assist skill + integration-specialist agent 追加。新規2ファイル + 既存8ファイル更新。推定11ファイル。"
iteration: 4
ui_surface: false
last_updated: "2026-04-18T12:00:00Z"
gate_approvals:
  client_ready_for_dev: n/a
  brainstorm: approved
  plan: approved
  review: approved
  qa: approved
  security: approved
  deploy: n/a
  dev_ready_for_client: pending
current_refs:
  requirements: []
  plan: "docs/plans/v090-integration-assist-plan.md"
  spec: null
  review: "docs/qa-reports/v090-review.md"
  qa: "docs/qa-reports/v090-qa.md"
  security: "docs/qa-reports/v090-security.md"
  deploy: null
  translation: null
external_evidence:
  - type: "browser-handoff-research"
    scope: "AI ブラウザ自動化 handoff パターン調査"
    findings: "11ツール比較。gstack $B handoff/resume が最もユーザー工数少。Playwright MCP は handoff 未対応。"
    resolution: "gstack $B をオプショナル依存として活用。未インストール時はフォールバック案内型。"
next_action: "v0.9.0 全ゲート通過。コミット+プッシュ待ち。"
blockers: []
session_history:
  - date: "2026-04-17"
    mode: Dev
    phase: "docs"
    note: "v0.7.3 実装完了+コミット。qa-verification skill, agent skills preload, MCP catalog。"
  - date: "2026-04-17"
    mode: Dev
    phase: "ship"
    note: "v0.8.0 Client モード強化 実装+全ゲート通過+コミット+プッシュ。48ファイル変更。"
  - date: "2026-04-18"
    mode: Dev
    phase: "plan"
    note: "v0.9.0 integration-assist 調査+プラン作成。11ツール比較、gstack $B handoff 採用決定。"
---

## Summary

Claude Code ネイティブの Ultra Framework 運用フレームワーク。v0.9.0 では
外部サービス連携支援: gstack $B handoff/resume を活用した integration-assist
skill と integration-specialist agent を追加。ユーザー工数を最小化。

## Recent Decisions

- gstack $B をオプショナル依存として採用（バンドルしない）。
- $B 未インストール時は案内型フォールバック。
- パスワードは handoff 経由でユーザーが直接入力（Claude に渡さない）。
- integration-specialist agent は Bash 含む allowedTools で $B コマンド実行可能。

## Session History

- 2026-04-15: v0.7.0-v0.7.2 実装。ネイティブ機能改善、scaffold自己完結性、信頼境界ハードニング。
- 2026-04-17: v0.8.0 Client モード強化 実装完了+全ゲート通過+コミット+プッシュ。48ファイル変更。
- 2026-04-18: v0.9.0 integration-assist 調査+プラン作成。gstack $B handoff 採用。
