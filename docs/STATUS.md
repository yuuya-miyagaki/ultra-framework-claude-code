---
framework: ultra-framework-claude-code
framework_version: "0.3.0"
project_name: "Ultra Framework Claude Code"
mode: Dev
phase: docs
task_type: framework
task_size: L
last_updated: "2026-04-13T00:00:00Z"
gate_approvals:
  client_ready_for_dev: n/a
  brainstorm: approved
  plan: approved
  review: approved
  qa: approved
  security: approved
  deploy: approved
  dev_ready_for_client: approved
current_refs:
  requirements: []
  plan: docs/plans/2026-04-10-ultra-framework-claude-code-implementation-plan.md
  spec: null
  review: docs/qa-reports/bootstrap-review.md
  qa: docs/qa-reports/bootstrap-qa.md
  security: docs/qa-reports/bootstrap-security.md
  deploy: docs/qa-reports/bootstrap-deploy-checklist.md
next_action: "v0.3.0 Tier 1 完了。Tier 2-3 の改善、または検証V2 の開始。"
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
  - date: "2026-04-10"
    mode: Dev
    phase: "implement"
    note: "Cross-framework improvements (8件), Codex review remediation (3 rounds), design-phase review F-01〜F-11 全件完了。"
  - date: "2026-04-10"
    mode: Dev
    phase: "docs"
    note: "Phase 1-3 実装完了（11施策）。4並列レビュー+Codex レビューで計14件修正。Visual Brainstorm追加。"
---

## Summary

Claude Code ネイティブの Ultra Framework 運用フレームワーク。Phase 1-3 の改善を
経て、ルールの自動強制（Hooks）、学習の構造化（Learnings）、レビューの専門化
（Review Army）、計画の境界定義（Boundary Map）が実装済み。

主要な構成:

- 薄い `CLAUDE.md` 制御カーネル（685語）
- 明示的な `docs/STATUS.md` 運用スキーマ
- 9つのサブエージェント（コア6 + レビュー specialist 3）
- 4つのランタイムフック（SessionStart, Gate, TDD, Destructive）
- 7つのプルベーススキル（deploy スキル追加）
- 17のドキュメントテンプレート（DEPLOY-CHECKLIST 追加）+ バリデータ2本

## Recent Decisions

- v0.3.0: 検証V1 フィードバック反映。Tier 1 改善5件を実装。
- Deploy フェーズ（deploy-prep/staging/uat/production/post-deploy）を追加。
- 3回失敗ルールをゴールベースカウントに改定。
- PLAN テンプレートに Deploy Target（必須）、Deliverable Checklist、External Integrations を追加。
- Security エージェントに Deploy Security Blockers セクションを追加。

## Session History

- 2026-04-10: Phase 1-3 全11施策実装。4並列レビュー+Codex レビューで計14件修正。
- 2026-04-12: NotebookLM + フレームワーク比較分析。進化ロードマップ v1 作成。
- 2026-04-13: Best Practice + ECC 分析。進化ロードマップ v2 作成。
- 2026-04-13: 検証V1 結果を統合。最終改善計画を作成。
- 2026-04-13: v0.3.0 Tier 1 実装（Deploy フェーズ、3回失敗ルール、成果物チェックリスト、認証ブロッカー）。
