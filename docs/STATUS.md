---
framework: ultra-framework-claude-code
framework_version: "0.7.2"
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
next_action: "v0.7.2 実装完了。全バリデータ PASS。コミット待ち。"
blockers: []
session_history:
  - date: "2026-04-15"
    mode: Dev
    phase: "docs"
    note: "v0.7.0 Phase C ファイナライズ。README Migration、STATUS数値修正、archive運用ルール整備。"
  - date: "2026-04-15"
    mode: Dev
    phase: "implement"
    note: "v0.7.1 ネイティブ機能改善。PreCompactフック追加、qa-browserエージェント分離、auto-memoryポリシー緩和。Codexレビュー3ラウンド反映。"
  - date: "2026-04-15"
    mode: Dev
    phase: "implement"
    note: "v0.7.2 scaffold自己完結性+信頼境界ハードニング。/validate分離、NotebookEditマッチャー追加、check-control-plane.sh新規、参照名ドリフト修正。"
---

## Summary

Claude Code ネイティブの Ultra Framework 運用フレームワーク。v0.7.2 では
scaffold 自己完結性修正（/validate をプロジェクト用に分離）、
信頼境界ハードニング（NotebookEdit マッチャー追加 + Bash control plane 保護）、
テンプレート参照名ドリフト修正を実施。

主要な構成:

- 薄い `CLAUDE.md` 制御カーネル + `.claude/rules/` 分離ルール
- 明示的な `docs/STATUS.md` 運用スキーマ（failure_tracking, task_size_rationale 追加）
- 10のサブエージェント（コア6 + specialist 4）
- 8つのランタイムフック（session-start, check-gate, check-tdd, check-control-plane, check-destructive, post-bash, post-status-audit, pre-compact）
- 11の `.claude/skills/` ネイティブスキル（pull-based）
- 7つの Slash Commands（/status, /gate, /recover, /validate, /next, /retro, /tutorial）
- 17のドキュメントテンプレート + バリデータ2本

current_refs は bootstrap 成果物。外部レビュー証拠は `external_evidence` を参照。

## Recent Decisions

- check-control-plane.sh は allowlist 方式。control plane パスを含む Bash コマンドは原則 deny。allowlist は「コマンド全体が許可スクリプトのみ」の場合に限定し、チェーン演算子（;, &&, ||, |, $()）を含むコマンドは allowlist 対象外。task_type=framework 時は全許可。
- example project に check_status.py を同梱。REQUIRED_EXAMPLE_FILES で存在検証。
- NotebookEdit は .ipynb 専用ツールだが defense-in-depth として Edit|Write|NotebookEdit マッチャーに追加。extract_file_path() に notebook_path フォールバックを実装。
- /validate は framework repo 用（両バリデータ実行）と scaffold project 用（check_status.py のみ）を分離。example は check_status.py 同梱で自己完結。
- テンプレート参照名ドリフト（subagent-development→subagent-dev 等）は v0.6.0 の skills 移行時の更新漏れ。lint 自動化は v0.8.0 で対応。
- /gate 文脈妥当性チェック、lean/full validator 一本化、STATUS.md 劣化対策は v0.8.0 へ延期。

## Session History

- 2026-04-10: Dev/ship — Bootstrapped the repository, validated the contract, and recorded review, QA, and security evidence.
- 2026-04-10: Dev/docs — Phase 1-3 実装完了（11施策）。4並列レビュー+Codex レビューで計14件修正。
- 2026-04-10: Phase 1-3 全11施策実装。4並列レビュー+Codex レビューで計14件修正。
- 2026-04-13: v0.3.0 Tier 1 実装。検証V1 結果統合。v0.5.0 改善計画策定。
- 2026-04-14: v0.5.0 Phase 1-7 実装。スリム化+機能追加（bug-diagnosis, iteration, browser QA, hotfix）。
- 2026-04-14: Codex レビュー4ラウンド完了。gate接続、contract保証、証拠構造、schema validation を段階的に強化。
- 2026-04-14: v0.6.0 全5フェーズ実装。信頼境界ハードニング、Skills移行、Commands導入、CLAUDE.md分離、言語統一。
- 2026-04-15: v0.6.0 Codex レビュー5ラウンド完了。gate承認経路分離、example自己完結化、validator深度強化。
- 2026-04-10: Cross-framework improvements (8件), Codex review remediation (3 rounds), design-phase review F-01〜F-11 全件完了。
