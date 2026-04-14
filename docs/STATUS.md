---
framework: ultra-framework-claude-code
framework_version: "0.5.0"
project_name: "Ultra Framework Claude Code"
mode: Dev
phase: docs
task_type: framework
task_size: L
iteration: 1
ui_surface: false
last_updated: "2026-04-14T00:00:00Z"
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
external_evidence:
  - type: "codex-review-round-1"
    scope: "v0.5.0 Phase 1-7"
    findings: "P1x3 (gate接続, contract, security pattern), P2x2 (iteration refs, browser QA), P3x1 (STATUS更新)"
    resolution: "全P1修正済み、P2修正済み、P3一部修正+理由付き現状維持"
  - type: "codex-review-round-2"
    scope: "v0.5.0 修正後"
    findings: "P2x1 (n/a gate stale ref), P3x1 (external evidence構造化)"
    resolution: "P2 PaC実装、P3 external_evidence追加"
next_action: "v0.5.0 Codex レビュー全ラウンド修正完了。リリース準備。"
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

Claude Code ネイティブの Ultra Framework 運用フレームワーク。v0.5.0 では
CLAUDE.md のスリム化（684→583語）、テンプレート圧縮、機能追加
（bug-diagnosis, iteration, browser QA, hotfix パス）を実施。

主要な構成:

- 薄い `CLAUDE.md` 制御カーネル（583語）
- 明示的な `docs/STATUS.md` 運用スキーマ（iteration, ui_surface 追加）
- 9つのサブエージェント（コア6 + レビュー specialist 3）
- 4つのランタイムフック（SessionStart, Gate, TDD, Destructive）
- 9つのプルベーススキル（bug-diagnosis, deploy-platforms 追加）
- 17のドキュメントテンプレート + バリデータ2本

current_refs は bootstrap 成果物。v0.5.0 証拠は `external_evidence` を参照。

## Recent Decisions

- v0.5.0: スリム化と機能追加を同時実施。先にトークン予算を確保し、余裕で機能追加。
- bug-diagnosis スキル追加。bugfix/hotfix で brainstorm+plan=n/a とし、gate 接続を明示。
- iteration サポート追加。refs クリア（requirements 以外 null）を明記。
- browser QA 統合。ui_surface フラグで条件分岐、証拠フィールド構造化。
- deploy プラットフォーム固有情報を deploy-platforms.md に分離し contract で保証。
- check_status.py の YAML パーサーは narrow subset 前提。external_evidence を nested/multiline に拡張する場合は PyYAML 導入を検討。

## Session History

- 2026-04-10: Phase 1-3 全11施策実装。4並列レビュー+Codex レビューで計14件修正。
- 2026-04-13: v0.3.0 Tier 1 実装。検証V1 結果統合。v0.5.0 改善計画策定。
- 2026-04-14: v0.5.0 Phase 1-7 実装。スリム化+機能追加（bug-diagnosis, iteration, browser QA, hotfix）。
- 2026-04-14: Codex レビュー4ラウンド完了。gate接続、contract保証、証拠構造、schema validation を段階的に強化。
