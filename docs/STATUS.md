---
framework: ultra-framework-claude-code
framework_version: "0.7.0"
project_name: "Ultra Framework Claude Code"
mode: Dev
phase: docs
task_type: framework
task_size: L
task_size_rationale: "フレームワーク全体構造の変更、30+ファイル、全フェーズ必須"
iteration: 1
ui_surface: false
last_updated: "2026-04-15T00:00:00Z"
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
  - type: "codex-review-v060-round-3"
    scope: "v0.6.0 example構造"
    findings: "P2x2 (example native構造欠落, validator coverage不足), P3x1 (/next Client flow欠落)"
    resolution: "example .claude/全構造コピー、validator拡充、/next Client table追加"
  - type: "codex-review-v060-round-4"
    scope: "v0.6.0 example hooks"
    findings: "P2x2 (example hooks/実体欠落, validator hooks検証なし)"
    resolution: "example hooks/コピー、validator hooks実体チェック追加"
  - type: "codex-review-v060-round-5"
    scope: "v0.6.0 validator深度+報告資料"
    findings: "P2x1 (command/settings意味的整合未検証), P3x1 (報告書+STATUS追随不足)"
    resolution: "command frontmatter検証+settings→hooks整合チェック追加、報告書+STATUS更新"
next_action: "v0.7.0 Phase A+B+C 全完了。改善報告書作成済み。コミット待ち。"
blockers: []
session_history:
  - date: "2026-04-10"
    mode: Dev
    phase: "implement"
    note: "Cross-framework improvements (8件), Codex review remediation (3 rounds), design-phase review F-01〜F-11 全件完了。"
  - date: "2026-04-15"
    mode: Dev
    phase: "implement"
    note: "v0.7.0 Phase A+B実装。P1/P2修正、failure_tracking、task_size_rationale、アーカイブ制限(MAX 3)。Codexレビュー反映。"
  - date: "2026-04-15"
    mode: Dev
    phase: "docs"
    note: "v0.7.0 Phase C ファイナライズ。README Migration、STATUS数値修正、archive運用ルール整備。"
---

## Summary

Claude Code ネイティブの Ultra Framework 運用フレームワーク。v0.7.0 では
STATUS.md スキーマ拡張（failure_tracking, task_size_rationale）、
session_history/external_evidence アーカイブ（MAX 3件制限）を実施。

主要な構成:

- 薄い `CLAUDE.md` 制御カーネル + `.claude/rules/` 分離ルール
- 明示的な `docs/STATUS.md` 運用スキーマ（failure_tracking, task_size_rationale 追加）
- 9つのサブエージェント（コア6 + レビュー specialist 3）
- 6つのランタイムフック（session-start, check-gate, check-tdd, check-destructive, post-bash, post-status-audit）
- 8つの `.claude/skills/` ネイティブスキル（pull-based）
- 5つの Slash Commands（/status, /gate, /recover, /validate, /next）
- 17のドキュメントテンプレート + バリデータ2本

current_refs は bootstrap 成果物。外部レビュー証拠は `external_evidence` を参照。

## Recent Decisions

- failure_tracking は薄い構造（goal/count/last_attempt）。attempts 配列は narrow YAML パーサーの制約で不採用。
- task_size_rationale は WARNING レベル。既存プロジェクト互換性を優先し FAIL にしない。
- session_history/external_evidence は MAX 3 件。アーカイブ基準は iteration ベースではなく latest N。
- bug-diagnosis スキルで bugfix/hotfix は brainstorm+plan=n/a。gate 接続を明示。
- iteration リセット時に requirements 以外の refs を null クリア。external_evidence は archive へ退避。
- check_status.py の YAML パーサーは narrow subset 前提。nested/multiline 拡張時は PyYAML 導入を検討。

## Session History

- 2026-04-10: Dev/ship — Bootstrapped the repository, validated the contract, and recorded review, QA, and security evidence.
- 2026-04-10: Dev/docs — Phase 1-3 実装完了（11施策）。4並列レビュー+Codex レビューで計14件修正。
- 2026-04-10: Phase 1-3 全11施策実装。4並列レビュー+Codex レビューで計14件修正。
- 2026-04-13: v0.3.0 Tier 1 実装。検証V1 結果統合。v0.5.0 改善計画策定。
- 2026-04-14: v0.5.0 Phase 1-7 実装。スリム化+機能追加（bug-diagnosis, iteration, browser QA, hotfix）。
- 2026-04-14: Codex レビュー4ラウンド完了。gate接続、contract保証、証拠構造、schema validation を段階的に強化。
- 2026-04-14: v0.6.0 全5フェーズ実装。信頼境界ハードニング、Skills移行、Commands導入、CLAUDE.md分離、言語統一。
- 2026-04-15: v0.6.0 Codex レビュー5ラウンド完了。gate承認経路分離、example自己完結化、validator深度強化。
