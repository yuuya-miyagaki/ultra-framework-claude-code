# セカンドオピニオン依頼: v0.7.1 残課題の棚卸しと修正計画

**日付:** 2026-04-15
**スコープ:** v0.7.1 実装後の未修正項目の特定と修正計画
**レビュアー:** Codex (second opinion)

## 背景

v0.7.1 で以下のネイティブ機能改善を実施した:
- PreCompact フック追加（STATUS.md 鮮度チェック + コンパクション阻止）
- qa-browser エージェント分離（disallowedTools で安全な Playwright アクセス）
- auto-memory ポリシー緩和（個人設定のみ許可）

実装後の監査で、**バージョン管理とドキュメントの不整合**が発見された。
加えて、v0.7.0 改善報告書に記載された**残課題 3 件**が未着手のまま残っている。

本資料では、これらを優先度順に整理し、修正計画を提案する。

---

## カテゴリ A: v0.7.1 実装漏れ（即時修正）

### A-1. バージョン番号が 0.7.0 のまま（CRITICAL）

**現状:**
v0.7.1 の変更（PreCompact、qa-browser、auto-memory）はコミット済み（622d7e3）だが、
以下のファイルでバージョンが `0.7.0` のまま:

| ファイル | 現在の値 | あるべき値 |
|---------|---------|-----------|
| `scripts/check_framework_contract.py` L14 | `FRAMEWORK_VERSION = "0.7.0"` | `"0.7.1"` |
| `docs/STATUS.md` L3 | `framework_version: "0.7.0"` | `"0.7.1"` |
| `templates/STATUS.template.md` L3 | `framework_version: "0.7.0"` | `"0.7.1"` |
| `examples/minimal-project/docs/STATUS.md` L3 | `framework_version: "0.7.0"` | `"0.7.1"` |

**修正案:** 4 ファイルのバージョンを `0.7.1` に更新。

**質問:** バージョン bump のタイミングとして、この残課題をすべて修正してから
bump すべきか、それとも先に bump して残課題は次バージョンに回すべきか？

---

### A-2. README.md のエージェント数が旧値のまま（HIGH）

**現状:**
README.md L35 に `"9 bounded specialist roles"` と記載されているが、
qa-browser 追加で実際は **10 エージェント**。

`docs/STATUS.md` の Summary は正しく `10のサブエージェント` に更新済み。

**修正案:**
- README.md L35: `"9 bounded specialist roles"` → `"10 bounded specialist roles"`
- Repository Structure セクションのコメントも更新

---

### A-3. v0.7.1 改善報告書が未作成（HIGH）

**現状:**
`docs/v070-improvement-report.md` は存在するが、v0.7.1 の改善報告書がない。
v0.7.1 の変更内容（PreCompact、qa-browser、auto-memory、Codex レビュー修正）が
STATUS.md の session_history にしか記録されていない。

**修正案:** `docs/v071-improvement-report.md` を作成。内容:
- 変更概要（3 件 + Codex レビュー修正 3 件）
- 設計判断の記録（PostCompact 不採用理由、qa-browser 責務分離）
- バリデーション結果
- 変更ファイル一覧

---

## カテゴリ B: v0.7.0 からの持ち越し課題

### B-1. external_evidence の type 命名規則の標準化（MEDIUM）

**現状:**
`external_evidence` の `type` フィールドがフリーテキスト。現在の値:
- `"codex-review-v060-round-3"`
- `"codex-review-v060-round-4"`
- `"codex-review-v060-round-5"`

命名規則が暗黙的で、バリデータも `type` の形式を検証していない。

**修正案:**
1. 命名規則を定義: `{source}-{scope}-{sequence}` 形式
   - 例: `codex-review-v060-3`, `self-review-native-gaps-1`
2. `check_status.py` に WARNING レベルの format チェックを追加
3. `templates/STATUS.template.md` にコメントで形式を案内

**質問:**
- 命名規則を強制（FAIL）するか推奨（WARNING）にとどめるか？
- 現在の 3 件は新規則に合わせてリネームすべきか、既存は許容すべきか？

---

### B-2. body Session History の自動アーカイブ（LOW）

**現状:**
frontmatter の `session_history` は MAX 3 で自動管理されるが、
body の `## Session History` セクションは手動退避のまま。
現在 body には 9 エントリが蓄積されている。

**修正案の選択肢:**

**案 1: `/next` コマンドでリマインダー表示**
body のエントリ数が閾値（例: 10）を超えたら `/next` 実行時に
「Session History の整理を推奨」と表示。実装コスト低。

**案 2: check_status.py で WARNING**
body の `## Session History` 配下の箇条書き行数を数え、
閾値超過で WARNING。自動検出可能だが、body パースの複雑さが増す。

**案 3: 現状維持**
body Session History は人間が読むための参考情報であり、
自動化の価値が低い。手動管理で十分。

**質問:** どの案が最適か？案 3（現状維持）で十分か？

---

### B-3. narrow YAML パーサーの PyYAML 移行判断（LOW）

**現状:**
`check_status.py` は正規表現ベースの narrow YAML パーサーを使用。
以下の制約がある:
- 3 段以上のネストに非対応
- マルチラインバリューに非対応
- YAML のエッジケース（特殊文字、フロースタイル等）に非対応

v0.7.1 で `failure_tracking`（2 段ネスト）を追加した際も、
narrow パーサーで対応可能な薄い構造に設計を合わせた。

**現在の判断:**
PyYAML は外部依存。フレームワークは依存ゼロ（Python 標準ライブラリのみ）を
原則としている。narrow パーサーで対応できる範囲でスキーマ設計を行う。

**修正案:**
- `--strict` オプション（既存）で PyYAML が利用可能な場合のみ厳密検証
- デフォルトは narrow パーサーのまま
- 現状で十分機能しているため、移行トリガーは「3 段ネストが必要になった時」

**質問:** この判断を維持してよいか？
PyYAML を必須依存に格上げするメリットはあるか？

---

## カテゴリ C: 意図的に維持した設計判断（確認のみ）

以下は Codex ネイティブ機能レビューで検討し、**意図的に現状維持**とした項目。
修正は不要だが、判断の妥当性を確認したい。

### C-1. EnterPlanMode 不採用

**理由:** フレームワークの brainstorm→plan フェーズと PlanMode が競合。
出力先（docs/plans/ vs Claude Code plan file）と承認経路（STATUS.md vs UI）が二重になる。

### C-2. ゲート承認の 2 層防御

**理由:** check-gate.sh（予防）+ post-status-audit.sh（検出）で実用上十分。
git tag 戦略はエージェントが `git tag` を実行できるため trust boundary が変わらない。

### C-3. hook `if` フィールドの defense-in-depth

**理由:** 除去のメリットが小さく（数行）、セキュリティコードの多層防御として残す価値がある。

### C-4. TaskCreate/TaskUpdate の不採用

**理由:** セッション内でのみ有効で永続化されない。STATUS.md が single source of truth。
ただし、subagent-dev スキルでは TaskCreate の使用を案内している
（実装フェーズ内のセッション内タスク管理として）。これは矛盾ではなく、
セッション横断の状態管理は STATUS.md、セッション内のサブタスク進捗は TaskCreate
という役割分担。

**質問:** C-1〜C-4 の判断に再考の余地はあるか？

---

## 修正の優先順序案

| 優先度 | ID | 内容 | 工数 |
|--------|-----|------|------|
| 1 | A-1 | バージョン bump (0.7.0→0.7.1) | 4 ファイル編集 |
| 2 | A-2 | README エージェント数修正 | 1 ファイル編集 |
| 3 | A-3 | v0.7.1 改善報告書作成 | 新規 1 ファイル |
| 4 | B-1 | external_evidence type 命名規則 | validator + template 修正 |
| 5 | B-2 | body Session History 管理 | 検討のみ or 軽微修正 |
| 6 | B-3 | YAML パーサー判断 | 現状維持（判断確認のみ） |

---

## レビューで特に聞きたいこと

1. **A-1: バージョン bump はこの残課題修正と同時に行うべきか、先に行うべきか？**

2. **B-1: external_evidence の type 命名規則は WARNING と FAIL どちらが適切か？**

3. **B-2: body Session History の管理は案 1〜3 のどれが最適か？
   それとも別のアプローチがあるか？**

4. **B-3: narrow YAML パーサーの維持は正しい判断か？**

5. **C-1〜C-4 の意図的維持判断に、再考すべきものはあるか？**

6. **上記以外に、現在のフレームワークで見落としている問題はあるか？**
   特に、v0.7.1 で追加した PreCompact フックと qa-browser エージェントの
   実装品質について、改善点があれば指摘してほしい。
