---
framework: ultra-framework-claude-code
framework_version: "0.7.3"
project_name: "Ultra Framework Claude Code"
mode: Dev
phase: docs
task_type: framework
task_size: L
task_size_rationale: "3本柱（qa-verification skill, agent skills preload, MCP catalog）。新規+編集で16ファイル。全フェーズ必須。"
iteration: 2
ui_surface: false
last_updated: "2026-04-17T00:00:00Z"
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
  plan: docs/specs/skills-mcp-improvement-report.md
  spec: docs/specs/skills-mcp-improvement-report.md
  review: docs/qa-reports/v073-review.md
  qa: docs/qa-reports/v073-qa.md
  security: docs/qa-reports/v073-security.md
  deploy: docs/qa-reports/v073-deploy-checklist.md
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
next_action: "v0.7.3 完了。LEARNINGS 更新済み。ship/docs コミット待ち。"
blockers: []
session_history:
  - date: "2026-04-15"
    mode: Dev
    phase: "implement"
    note: "v0.7.1 ネイティブ機能改善。PreCompactフック追加、qa-browserエージェント分離、auto-memoryポリシー緩和。Codexレビュー3ラウンド反映。"
  - date: "2026-04-15"
    mode: Dev
    phase: "implement"
    note: "v0.7.2 scaffold自己完結性+信頼境界ハードニング。/validate分離、NotebookEditマッチャー追加、check-control-plane.sh新規、参照名ドリフト修正。"
  - date: "2026-04-16"
    mode: Dev
    phase: "brainstorm"
    note: "v0.7.3 Skills & MCP 改善調査レポート作成。4フレームワーク比較+Web調査+ギャップ分析。3本柱スコープ決定。"
---

## Summary

Claude Code ネイティブの Ultra Framework 運用フレームワーク。v0.7.3 では
Skills & MCP 改善: qa-verification スキル新設、エージェント skills preload 統一
（reviewer/security/qa）、MCP カタログを extensions/mcp/ で提供。

主要な構成:

- 薄い `CLAUDE.md` 制御カーネル + `.claude/rules/` 分離ルール
- 明示的な `docs/STATUS.md` 運用スキーマ（failure_tracking, task_size_rationale 追加）
- 10のサブエージェント（コア6 + specialist 4）
- 8つのランタイムフック（session-start, check-gate, check-tdd, check-control-plane, check-destructive, post-bash, post-status-audit, pre-compact）
- 12の `.claude/skills/` ネイティブスキル（pull-based）
- 7つの Slash Commands（/status, /gate, /recover, /validate, /next, /retro, /tutorial）
- 17のドキュメントテンプレート + バリデータ2本
- MCP カタログ（extensions/mcp/ — manual opt-in）

## Recent Decisions

- v0.7.3 スコープは 3 本柱: qa-verification skill, agent skills preload 統一, MCP catalog。
- qa-verification は qa フェーズ唯一のスキル欠損を埋める。user-invocable: false。
- skills preload: reviewer→review, security→security-review, qa→qa-verification。implementer→tdd は既存。
- MCP catalog は extensions/ に配置（core 契約外、manual opt-in）。5 サーバー推奨。
- allowed-tools, paths 自動アクティベーション, Agent Teams は v0.8.0 へ延期。

## Session History

- 2026-04-14: v0.6.0 全5フェーズ実装。信頼境界ハードニング、Skills移行、Commands導入、CLAUDE.md分離、言語統一。
- 2026-04-15: v0.6.0 Codex レビュー5ラウンド完了。gate承認経路分離、example自己完結化、validator深度強化。
- 2026-04-15: v0.7.0-v0.7.2 実装。ネイティブ機能改善、scaffold自己完結性、信頼境界ハードニング。
- 2026-04-16: v0.7.3 Skills & MCP 改善調査レポート作成。4フレームワーク比較+ギャップ分析。
- 2026-04-17: v0.7.3 実装完了+コミット。qa-verification skill, agent skills preload, MCP catalog。レビュー指摘5件修正。
