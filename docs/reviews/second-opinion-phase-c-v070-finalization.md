# Design Review Request: Phase C — v0.7.0 ファイナライズ

**Date:** 2026-04-15
**Scope:** v0.7.0 リリース前の残課題修正 + ドキュメント仕上げ
**Reviewer:** Codex (second opinion)

## Background

Ultra Framework Claude Code v0.7.0 では Phase B で以下のスキーマ変更を実施した:

- `failure_tracking` フィールド追加（goal/count/last_attempt）
- `task_size_rationale` フィールド追加（WARNING レベル）
- `session_history` / `external_evidence` のアーカイブ制限（MAX 3 件）
- `docs/evidence-archive.md` 新設
- バージョン 0.6.0 → 0.7.0 bump

Phase B の実装完了後にプロジェクト全体を再監査した結果、以下の残課題が判明した。

---

## P2-01: README.md に v0.7.0 マイグレーションセクションが欠落

### 問題

README.md には `## Migration from v0.5.0` セクション（v0.6.0 の変更点を列挙）が
あるが、v0.7.0 の変更に関する記述がない。

### 現状（README.md:117-129）

```markdown
## Migration from v0.5.0

Key changes in v0.6.0:

1. **Skills moved**: `docs/skills/` → `.claude/skills/*/SKILL.md`
2. **Rules extracted**: ...
...
8. **CLAUDE.md slimmed**: 583 → 320 words
```

### 提案

`## Migration from v0.5.0` を `## Migration` にリネームし、v0.7.0 セクションを追加:

```markdown
## Migration

### From v0.6.0 to v0.7.0

1. **STATUS.md schema**: `failure_tracking: null` と `task_size_rationale` を追加
2. **Archive limits**: `session_history` と `external_evidence` を最新 3 件に制限
3. **Archive file**: `docs/evidence-archive.md` を作成し、古い証拠を退避
4. **CLAUDE.md**: 3-failure ルールに `failure_tracking` 記録ルールを追記（338 語）
5. **Iteration reset**: `state-machine.md` に external_evidence アーカイブルールを追記
6. **Skills**: brainstorming, bug-diagnosis に `task_size_rationale` 記録手順を追記

### From v0.5.0 to v0.6.0

(既存内容をここに移動)
```

---

## P2-02: docs/STATUS.md Summary のスキル数が不正確

### 問題

Summary に「9つの `.claude/skills/` ネイティブスキル」と記載されているが、
実際のスキルディレクトリは 8 つ:

```
brainstorming, bug-diagnosis, client-workflow, deploy,
session-recovery, ship-and-docs, subagent-dev, tdd
```

deploy ディレクトリ内の `platforms.md` は別スキルではなく補足ファイル。

### 提案

「9つ」→「8つ」に修正。

---

## P2-03: docs/STATUS.md Summary のフック数とリストが不正確

### 問題

Summary に「7つのランタイムフック（SessionStart, Gate, TDD, Destructive, PostBash,
StatusAudit, CheckTDD）」と記載されているが、実際のフックファイルは 6 つ:

```
session-start.sh, check-gate.sh, check-tdd.sh,
check-destructive.sh, post-bash.sh, post-status-audit.sh
```

「TDD」と「CheckTDD」はどちらも `check-tdd.sh` を指しており、重複カウント。

### 提案

「7つ」→「6つ」に修正し、リストをファイル名ベースに整理:

```
6つのランタイムフック（session-start, check-gate, check-tdd,
check-destructive, post-bash, post-status-audit）
```

---

## P2-04: docs/STATUS.md body の Recent Decisions が v0.7.0 を反映していない

### 問題

Recent Decisions セクションは v0.5.0 時代の判断のみを記録しており、
v0.7.0 で行った以下の重要な設計判断が含まれていない:

- failure_tracking を薄い構造（attempts リストなし）にした理由
- task_size_rationale を WARNING（FAIL ではなく）にした理由
- session_history/external_evidence の MAX を 5→3 に下げた判断
- external_evidence のアーカイブ基準を iteration ベースではなく latest N にした判断

### 提案

v0.7.0 の設計判断を追加し、v0.5.0 の古い判断は一部整理する。

---

## P2-05: docs/STATUS.md の session_history frontmatter を更新

### 問題

frontmatter の session_history 最新3件がすべて v0.6.0 以前の記録:

```yaml
session_history:
  - date: "2026-04-10"  # ship
  - date: "2026-04-10"  # implement
  - date: "2026-04-10"  # docs (Phase 1-3)
```

v0.7.0 Phase B の実装記録が含まれていない。

### 提案

最も古い 1 件（Phase 1-3 docs）を body の Session History にアーカイブし、
Phase B 実装記録を追加:

```yaml
session_history:
  - date: "2026-04-10"
    mode: Dev
    phase: "ship"
    note: "Bootstrapped the repository, validated the contract, ..."
  - date: "2026-04-10"
    mode: Dev
    phase: "implement"
    note: "Cross-framework improvements (8件), Codex review remediation ..."
  - date: "2026-04-15"
    mode: Dev
    phase: "implement"
    note: "v0.7.0 Phase B実装。failure_tracking, task_size_rationale, アーカイブ制限(MAX 3)。Codexレビュー反映。"
```

---

## P3-01: second-opinion-phase-b-status-schema.md のアーカイブ

### 問題

Phase B の設計レビュー文書 `docs/second-opinion-phase-b-status-schema.md` が
残存している。Phase B は実装完了済み。

### 提案

選択肢:
- A) 削除する（実装完了し不要）
- B) `docs/reviews/` 等にアーカイブする（設計判断の記録として保持）
- C) そのまま残す（参照したい場合に便利）

### 補足

本ファイル（`second-opinion-phase-c-v070-finalization.md`）も Phase C 完了後に
同様の扱いになる。一貫したルールが望ましい。

---

## P3-02: docs/STATUS.md の body Session History が長大化

### 問題

body の Session History セクションに 6 件の履歴が蓄積しており、
今後も増え続ける。STATUS.md は毎セッション L0 で読み込まれるため、
body の肥大化もコンテキスト効率に影響する。

### 現状

```markdown
## Session History

- 2026-04-10: Phase 1-3 全11施策実装...
- 2026-04-13: v0.3.0 Tier 1 実装...
- 2026-04-14: v0.5.0 Phase 1-7 実装...
- 2026-04-14: Codex レビュー4ラウンド完了...
- 2026-04-14: v0.6.0 全5フェーズ実装...
- 2026-04-15: v0.6.0 Codex レビュー5ラウンド完了...
```

### 提案

body の Session History は直近 5 件程度を保持し、古いものは
`docs/session-archive.md` に退避する運用ルールを明文化する。
ただし、これは root STATUS.md 固有の問題であり、通常の利用プロジェクトでは
iteration リセットで body もリフレッシュされるため、強制する必要はない。

---

## Questions for Reviewer

1. **P2-01: README マイグレーションセクションの構造はどうあるべきか？**
   v0.5.0→v0.6.0 と v0.6.0→v0.7.0 を並列セクションにするか、
   それとも最新バージョンの変更点だけを目立たせるか？

2. **P2-02/03 の数値修正は STATUS.md Summary だけで十分か？**
   他に 9 スキルや 7 フックを参照している箇所がないか確認すべきか？

3. **P2-04: Recent Decisions をどの程度整理すべきか？**
   v0.5.0 の古い判断を全て残すか、v0.7.0 の判断と入れ替えるか、
   両方保持するか？

4. **P3-01: second-opinion ファイルの運用ルールはどうすべきか？**
   削除・アーカイブ・残留のどれが適切か？
   今後の一貫したルールを決めたい。

5. **Phase C 全体の変更でフレームワークバージョンを再度上げる必要はあるか？**
   P2-01〜05 はドキュメント修正のみでスキーマ変更を含まない。
   0.7.0 のままで patch 扱い（0.7.1）にするか、そのままか？

6. **Phase C 完了後、v0.7.0 改善報告書を作成すべきか？**
   v0.6.0 には `docs/v060-improvement-report.md` が存在する。
   v0.7.0 でも同様の報告書を作成すべきか、
   それとも STATUS.md の外部証拠で十分か？
