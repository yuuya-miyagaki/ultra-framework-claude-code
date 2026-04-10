---
framework: ultra-framework-claude-code
framework_version: "0.2.0"
project_name: "Ultra Framework Claude Code"
mode: Dev
phase: docs
task_type: framework
last_updated: "2026-04-10T12:00:00Z"
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
next_action: "Phase 1-3 完了。実プロジェクトでの検証、または次の改善サイクルの開始。"
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

- 薄い `CLAUDE.md` 制御カーネル（649語）
- 明示的な `docs/STATUS.md` 運用スキーマ
- 9つのサブエージェント（コア6 + レビュー specialist 3）
- 4つのランタイムフック（SessionStart, Gate, TDD, Destructive）
- 6つのプルベーススキル
- 16のドキュメントテンプレート + バリデータ2本

## Recent Decisions

- Phase 1: CSO, Rationalization Tables, Hallucination Guard, Hooks 基盤を導入。
- Phase 2: Boundary Map, Learnings 構造化, Review Army を実装。
- Phase 3: Phase-Aware Session Context, TDD Guard, Agent Validation を追加。
- P2-04: Visual Brainstorm（Mermaid/Draw.io 連携）を追加。
- 語数上限は機能効果が大きい場合に柔軟対応（ユーザー承認済み）。

## Session History

- 2026-04-10: 設計承認。Claude Code 専用ディストリビューションとして独立構築。
- 2026-04-10: リポジトリスケルトン、テンプレート、サンプル、バリデータ完成。
- 2026-04-10: クロスフレームワーク改善、Codex レビュー修正、設計レビュー F-01〜F-11 全件完了。
- 2026-04-10: Phase 1-3 全11施策実装。4並列レビュー+Codex レビューで計14件修正。
