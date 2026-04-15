# Design Review Request: Phase B — STATUS.md Schema Improvements

**Date:** 2026-04-15
**Scope:** P2-09, P3-01, P2-07, P2-08 — STATUS.md のスキーマ拡張
**Reviewer:** Codex (second opinion)

## Background

Ultra Framework Claude Code の STATUS.md は YAML frontmatter + Markdown body で
構成される運用状態ファイル。CLAUDE.md の Session Start で毎回読み込まれるため、
ファイルサイズがコンテキスト効率に直結する。

現在 STATUS.md は以下の問題を抱えている:

1. **session_history** が上限 5 に迫っている（root: 4/5）
2. **external_evidence** が 7 エントリ（~500語）に膨張し、常時ロードされている
3. **task_size** の判定根拠が記録されない（S で QA/Security をスキップした理由が不明）
4. **failure_count**（3-failure ルール）が永続化されず、会話メモリに依存

## Current Data

### Root STATUS.md frontmatter (抜粋)

```yaml
session_history:   # 4 entries (max 5)
  - date: "2026-04-10"
    mode: Dev
    phase: "brainstorm"
    note: "Approved the Claude-native design..."
  - date: "2026-04-10"
    mode: Dev
    phase: "ship"
    note: "Bootstrapped the repository..."
  - date: "2026-04-10"
    mode: Dev
    phase: "implement"
    note: "Cross-framework improvements..."
  - date: "2026-04-10"
    mode: Dev
    phase: "docs"
    note: "Phase 1-3 実装完了..."

external_evidence:   # 7 entries (~500 words)
  - type: "codex-review-round-1"
    scope: "v0.5.0 Phase 1-7"
    findings: "P1x3 (gate接続, contract, security pattern)..."
    resolution: "全P1修正済み..."
  # ... 6 more entries
```

### Body (Summary + Recent Decisions + Session History)

Body 側の Session History にも 6 件のテキスト記録がある。
frontmatter の session_history と body の Session History は別物
（frontmatter = 構造化データ、body = 人間向けサマリ）。

### Validator 制約

- `check_status.py`: MAX_SESSION_HISTORY_ENTRIES = 5
- external_evidence: エントリ数上限なし（検証はスキーマのみ）
- task_size: 存在チェックのみ（rationale なし）
- failure_count: フィールド自体が存在しない

---

## P2-09 + P3-01: 履歴セクションのアーカイブ

### 問題

session_history と external_evidence は iteration をまたいで蓄積する。
STATUS.md は毎セッション L0 で読み込まれるため、過去の履歴が
コンテキストを圧迫する。

### 提案: アーカイブ分離方式

**session_history:**

- frontmatter 内は最新 3 件のみ保持（MAX を 5 → 3 に変更）
- 4 件目以降は body の `## Session History` セクションに移動
  （body はテキストなので validator 制約を受けない）
- body 側も肥大したら `docs/session-archive.md` に手動退避を推奨

**external_evidence:**

- frontmatter 内は最新 iteration の証拠のみ保持
- 過去 iteration の証拠は `docs/evidence-archive.md` に移動
- iteration リセット時にアーカイブを実行

**実装変更:**

| ファイル | 変更 |
|----------|------|
| `check_status.py` | MAX_SESSION_HISTORY_ENTRIES: 5 → 3 |
| `templates/STATUS.template.md` | body Session History セクションに保持ルールを注記 |
| `.claude/rules/state-machine.md` | iteration リセット時に external_evidence アーカイブを追記 |
| `/next` command | 上限接近時にアーカイブ提案を表示 |

**やらないこと:**

- 自動アーカイブスクリプトの新設（過剰）
- frontmatter から external_evidence を完全除去（最新 iteration 分は有用）

### Alternative: external_evidence を frontmatter から body に全面移動

external_evidence は validator の構造検証を受けているが、
実運用では「過去レビューの要約」としてしか使われない。
body に移せば frontmatter が軽量化するが、構造検証を失う。

---

## P2-07: task_size_rationale の導入

### 問題

task_size が S の場合、QA/Security/Deploy がスキップされる。
しかし「なぜ S と判断したか」の根拠がどこにも残らない。
後から「本来 M だったのに S として QA をスキップした」ケースを検出できない。

### 提案: STATUS.md に task_size_rationale フィールド追加

```yaml
task_size: S
task_size_rationale: "1ファイル変更、既存関数のバグ修正のみ"
```

**実装変更:**

| ファイル | 変更 |
|----------|------|
| `check_status.py` | OPTIONAL_TOP_LEVEL_KEYS に `task_size_rationale` 追加 |
| `check_status.py` | task_size が設定されている場合に rationale の存在を WARNING（FAIL ではない） |
| `templates/STATUS.template.md` | `task_size_rationale: ""` を追加 |
| `examples/minimal-project/docs/STATUS.md` | rationale を記入 |
| `.claude/skills/brainstorming/SKILL.md` | brainstorm 完了時に rationale 記録を手順に追加 |
| `.claude/skills/bug-diagnosis/SKILL.md` | 同上 |

**やらないこと:**

- rationale 未記入を FAIL にする（既存プロジェクトの互換性を壊す）
- rationale の内容を機械検証する（自然言語なので不可能）

### Alternative: brainstorm record に書くだけで STATUS.md に入れない

brainstorm-record.md にサイズ判定の根拠を書き、STATUS.md には入れない案。
→ brainstorm をスキップする bugfix/hotfix で根拠が残らないため不採用。

---

## P2-08: failure_count の永続化

### 問題

CLAUDE.md の 3-failure ルール:
> Stop after 3 failures toward the same goal: write docs/second-opinion.md,
> update STATUS.md blockers, recommend IDE chat, then wait.

現状、カウントは Claude Code の会話内メモリに依存。
コンテキスト圧縮やセッション跨ぎでカウントがリセットされる。

### 提案: STATUS.md に failure_tracking フィールド追加

```yaml
failure_tracking:
  goal: "Playwright MCP でスクリーンショット取得"
  count: 2
  attempts:
    - "browser_take_screenshot 直接呼び出し → permission denied"
    - "browser_navigate 後に screenshot → timeout"
```

**実装変更:**

| ファイル | 変更 |
|----------|------|
| `check_status.py` | OPTIONAL_TOP_LEVEL_KEYS に `failure_tracking` 追加 |
| `check_status.py` | failure_tracking のスキーマ検証（goal, count, attempts） |
| `templates/STATUS.template.md` | `failure_tracking: null` を追加 |
| `CLAUDE.md` | 3-failure ルールに「failure_tracking に記録せよ」を追記 |
| `templates/CLAUDE.template.md` + example | 同上 |
| `.claude/agents/implementer.md` | 3-failure ルール参照時に failure_tracking 更新を追記 |
| `hooks/session-start.sh` | failure_tracking が存在する場合に警告を注入 |

**ライフサイクル:**

1. 1 回目の失敗: failure_tracking を作成（goal, count=1, attempts[0]）
2. 2 回目の失敗: count=2, attempts[1] 追加
3. 3 回目の失敗: count=3 → second-opinion.md 作成、STATUS.md blockers 更新
4. ゴール達成 or ゴール変更: failure_tracking を null にリセット
5. session-start.sh: count >= 1 なら「failure tracking active: {goal} ({count}/3)」を注入

**やらないこと:**

- hook で failure を自動カウント（ゴール判定は Claude Code の判断が必要）
- failure_tracking の history 保持（解決したら null にリセットで十分）

### Alternative: docs/failure-log.md に書く

STATUS.md を重くしたくない場合、別ファイルに書く案。
→ session-start.sh が STATUS.md しか読まないため、
別ファイルだと警告注入ができない。STATUS.md に入れるのが合理的。

---

## 実装順序の提案

```
Step 1: P2-09 + P3-01 (session_history + external_evidence アーカイブ)
  → STATUS.md スキーマの「減らす」側。先にやると後続の追加が軽くなる。

Step 2: P2-07 (task_size_rationale)
  → フィールド追加 + validator WARNING + スキル手順追記

Step 3: P2-08 (failure_tracking)
  → 最も変更箇所が多い。CLAUDE.md 全 variant + agent + hook + validator
```

## Questions for Reviewer

1. **session_history MAX を 5 → 3 に下げるのは妥当か？**
   root は既に 4 件あるため、先に 1 件をアーカイブしてから MAX を下げる必要がある。

2. **external_evidence のアーカイブ戦略として「最新 iteration のみ frontmatter」は妥当か？**
   root STATUS.md は iteration=1 で 7 件すべてが同一 iteration。
   この場合のアーカイブ基準をどうすべきか（例: 最新 N 件に変更？）。

3. **task_size_rationale は WARNING と FAIL のどちらが適切か？**
   互換性を考慮して WARNING を提案しているが、
   「S で QA スキップ」の安全性を考えると FAIL にすべきかもしれない。

4. **failure_tracking の YAML 構造は適切か？**
   attempts リストを STATUS.md の narrow YAML パーサーで扱えるか。
   check_status.py の regex ベースパーサーの制約を考慮すべき。

5. **Phase B 全体の実装順序に問題はないか？**

6. **Phase B の変更でフレームワークバージョンを 0.7.0 に上げるべきか？**
   Phase A の修正は patch レベルだったが、Phase B はスキーマ変更を含む。
