# クライアント基本情報

<!-- exit-check: 全セクション記入済み・ステークホルダー特定済み・制約条件明確 → glossary へ -->

## プロジェクト概要

- プロジェクト名: Aegis
- ドメイン: AI エージェント運用フレームワーク
- 期間: 継続開発（v0.3.0 開始、現在 v0.8.0）
- 予算レンジ: OSS（個人開発）

## ステークホルダー

| 名前 | 役割 | 決定権限 |
|------|------|---------|
| 宮垣祐也 | フレームワーク開発者・設計者 | 最終決定 |
| Claude Code | AI エージェント（実行者） | 情報提供 |

## ビジネスコンテキスト

- ビジネスゴール: Claude Code セッションに構造化ワークフローを提供し、品質と再現性を向上させる
- 成功基準: フレームワーク適用プロジェクトで要件漏れゼロ、ゲート違反ゼロ
- KPI: CLAUDE.md 語数 700 以下維持、contract validator パス率 100%

## 技術環境

- 現行スタック: Claude Code CLI, Markdown ドキュメント, bash hooks, Python validators
- インフラ: GitHub リポジトリ、ローカル開発環境（macOS）
- 技術的制約: Claude Code の PreToolUse/PostToolUse フック機構に依存

## 制約条件

- 予算: なし（OSS）
- スケジュール: マイルストーン駆動（Phase A → Phase B → Phase C）
- 規制・法令: なし
- 組織的制約: CLAUDE.md は 700 語上限（thin framework 原則）、セッション間状態は STATUS.md で管理
