---
framework: ultra-framework-claude-code
framework_version: "0.12.1"
project_name: "Ultra Framework Claude Code"
mode: Dev
phase: review
task_type: framework
task_size: M
task_size_rationale: "MCP deploy gate hook + ref check 強化 + name lint + health check。新規2ファイル + 既存多数修正。"
iteration: 6
ui_surface: false
last_updated: "2026-04-22T00:00:00Z"
gate_approvals:
  client_ready_for_dev: n/a
  brainstorm: approved
  plan: approved
  review: approved
  qa: pending
  security: pending
  deploy: pending
  dev_ready_for_client: pending
current_refs:
  requirements: []
  plan: "docs/plans/v0100-browser-assist-plan.md"
  spec: null
  review: docs/qa-reports/v0120-review.md
  qa: null
  security: null
  deploy: null
  translation: null
external_evidence:
  - type: "second-opinion-v0120"
    scope: "v0.12.0 計画レビュー"
    findings: "Item 3 延期、push matcher 除外、ref check 移行パス追加、テスト強化"
    resolution: "4点すべて反映し計画を修正"
next_action: "v0.12.1 レビュー修正完了。qa ゲートへ進む。118テスト PASS + tier 1/2 PASS を根拠とする。"
blockers: []
failure_tracking: null
session_history:
  - date: "2026-04-18"
    mode: Dev
    phase: "ship"
    note: "v0.9.0 integration-assist + check-secrets.sh。全ゲート通過+コミット+プッシュ (f3ffb47)。"
  - date: "2026-04-22"
    mode: Dev
    phase: "implement"
    note: "v0.12.0 実装完了。MCP deploy gate + ref check 強化 + name lint + health check。48テスト全PASS。"
  - date: "2026-04-22"
    mode: Dev
    phase: "review"
    note: "v0.12.0→v0.12.1 レビュー2ラウンド。Client/Dev境界・n/a model・reset ref・template保護等11件修正。118テスト全PASS。"
---

## Summary

Claude Code ネイティブの Ultra Framework 運用フレームワーク。v0.12.0 では
MCP deploy gate hook、/gate ref チェック強化（DEPRECATION WARNING）、
Skill/Agent/Command 名 lint、STATUS.md health check の 4 項目を実装。

## Recent Decisions

- MCP matcher: `mcp__.*__deploy.*` — `push` は除外（通常リモート更新と区別不能）
- Ref チェック: v0.12.0 は DEPRECATION WARNING のみ、v0.13.0 で ERROR 化予定
- Name lint: regex 一本ではなく、ファイル種別ごとの小さい extractor に分割
- Health check: 警告のみ（ブロックなし）、session-start.sh から呼び出し
- Item 3 (Lean/Full プロファイルモード) はセカンドオピニオンにより v0.13.0 に延期

## Session History

- 2026-04-15: v0.7.0-v0.7.2 実装。ネイティブ機能改善、scaffold自己完結性、信頼境界ハードニング。
- 2026-04-17: v0.8.0 Client モード強化 実装完了+全ゲート通過+コミット+プッシュ。48ファイル変更。
- 2026-04-18: v0.9.0-v0.10.0 integration-assist, browser-assist。全ゲート通過+コミット+プッシュ。
- 2026-04-22: v0.11.0 Hair Salon Bloom 振り返り7施策実装+コミット+プッシュ。
- 2026-04-22: v0.12.0 MCP gate + ref check + name lint + health check。48テスト全PASS。
