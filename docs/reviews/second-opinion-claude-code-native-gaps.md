# セカンドオピニオン依頼: Claude Code ネイティブ機能の活用度評価

**日付:** 2026-04-15
**スコープ:** v0.7.0 完了後の Claude Code ネイティブ適応度の総合評価
**レビュアー:** Codex (second opinion)

## 背景

Ultra Framework Claude Code v0.7.0 のリリースを完了した。
v0.7.0 では STATUS.md スキーマ拡張、フック修正、アーカイブ制限などを実施し、
「実害のあった問題」はすべて解消した。

ここで改めて、**Claude Code のネイティブ機能をどこまで活用できているか**、
**残っている制約は本当に仕方がないのか**を第三者視点で評価したい。

---

## 1. 解消済みの問題（参考情報）

以下は v0.7.0 で解消済み。レビュー不要。

| 問題 | 修正内容 |
|------|----------|
| `check-tdd.sh` 実行権限なし | chmod +x |
| LEARNINGS grep が非 POSIX | `[[:space:]]` パターンに修正 |
| QA ブラウザハンドオフ手順なし | 構造化ハンドオフブロック追加 |
| failure_tracking がメモリ依存 | STATUS.md に永続化（goal/count/last_attempt） |
| session_history/evidence 肥大化 | MAX 3 + アーカイブ運用 |

---

## 2. 意図的な妥協：本当にこのままでよいか

### 2-A. QA/Security エージェントの readOnly 制約

**現状:**
QA エージェントと Security エージェントは `readOnly: true` で動作する。
そのため Playwright MCP ツール（`browser_take_screenshot` 等）を直接呼べない。
ブラウザ QA が必要な場合、QA レポートに「Orchestrator Action Required」ブロックを
書き、オーケストレータ（メインの Claude Code）に実行を委任する。

**疑問:**
- この readOnly 制約は本当に必要か？
- QA エージェントを `readOnly: false` にして Playwright だけ許可する設計は
  リスクが高すぎるか？
- あるいは、QA エージェントの代わりに `/qa` コマンドを作り、
  メインコンテキストで Playwright を直接実行する方が合理的か？

**現在の判断:**
readOnly のままハンドオフで運用。理由は以下:
- QA エージェントがファイル編集権限を持つとレポート改ざんリスクがある
- Playwright は環境依存が強く、サブエージェントで失敗すると原因追跡が困難

**質問:** この判断は妥当か？もっと良い方法はあるか？

---

### 2-B. ゲート承認が STATUS.md（可変ファイル）に依存

**現状:**
ゲート承認状態は `docs/STATUS.md` の YAML frontmatter に記録される。
Claude Code（エージェント含む）は STATUS.md を編集できるため、
理論上はエージェントがゲートを自己承認できてしまう。

**現在の防御:**
1. **予防層**: `check-gate.sh`（PreToolUse フック）が STATUS.md への
   直接編集をブロック。ゲート更新は `scripts/update-gate.sh` 経由のみ
2. **検出層**: `post-status-audit.sh`（PostToolUse フック）が
   編集前後のゲート状態をスナップショット比較し、不正な変更を検出

**疑問:**
- 2 層防御で「実用上十分」としているが、本当に十分か？
- git tag や署名付きアーティファクトを使った外部ストアは
  本当に Claude Code ランタイム内で不可能か？
- 例えば `git tag gate/review/approved` のようなタグ戦略で
  STATUS.md 外にゲート状態を持つことは検討に値するか？

**現在の判断:**
STATUS.md + 2 層フック防御で運用。理由は以下:
- git tag は Claude Code が `git tag` コマンドを実行できるため、
  結局エージェントが自己タグ付けできる（trust boundary は変わらない）
- 外部ストア（CI/CD、署名）は Claude Code のランタイムから到達不能
- 2 層防御で検出+ブロックできるため、実用上のリスクは低い

**質問:** この分析は正しいか？見落としている防御手段はあるか？

---

### 2-C. hook `if` フィールドの後方互換対応

**現状:**
Claude Code v2.1.85 以降は hook 設定の `if` フィールドで
「どのツール/ファイルに対して発火するか」を宣言的に制御できる。
しかし、古いバージョンでは `if` が無視される。

**現在の対応:**
`if` フィールドを設定しつつ、シェルスクリプト内でも
同じファイルパスチェックを実施する（defense-in-depth）。

```bash
# settings.json
"if": "filePath.endsWith('STATUS.md')"

# post-status-audit.sh（スクリプト内でも同じチェック）
case "$TARGET_FILE" in
  *STATUS.md) ;; # proceed
  *) echo '{}'; exit 0 ;;
esac
```

**疑問:**
- 2026 年 4 月時点で、`if` フィールド非対応の Claude Code を
  サポートし続ける必要はあるか？
- defense-in-depth を残すコストは低い（数行のシェル）ので、
  削除する必要はないとも言えるが、逆に
  「不要な複雑さ」として除去すべきという考え方もある

**現在の判断:**
defense-in-depth を維持。理由は以下:
- 除去のメリットが小さい（数行の削減）
- `if` フィールドの挙動が Claude Code バージョン間で変わるリスクがゼロではない
- セキュリティ関連のコードは多層防御が原則

**質問:** この判断は過剰か、それとも妥当か？

---

## 3. Claude Code 側の成熟待ち

### 3-A. コンテキスト compaction フック

**現状:**
Claude Code がコンテキスト圧縮を行う前後にフック（PreCompact/PostCompact）を
提供していない。そのため、フェーズ遷移時の要約やドキュメント更新を
自動化する手段がない。

**影響:**
- 長いセッションでコンテキストが圧縮されると、フェーズ状態や
  作業進捗の情報が失われる可能性がある
- 現在は `session-start.sh` で STATUS.md から状態を復元しているが、
  セッション途中の圧縮には対応できない

**質問:**
- この制約に対して、フレームワーク側でできる追加の工夫はあるか？
- 例えば「定期的に STATUS.md を更新するリマインダー」を
  何らかの方法で実装できるか？
- それとも Claude Code の機能追加を待つのが正解か？

---

## 4. 意図的に不採用としたもの：再考の余地はあるか

### 4-A. `EnterPlanMode` の不採用

**現状:**
CLAUDE.md に「Use framework phases, not `EnterPlanMode`.」と明記。
フレームワークのフェーズ制御（brainstorm→plan→implement→...）が
Claude Code の `EnterPlanMode` と競合するため不採用とした。

**疑問:**
- フレームワークの plan フェーズと Claude Code の PlanMode を
  併用する方法はないか？
- 例えば「plan フェーズに入ったら自動的に PlanMode に切り替え、
  plan が承認されたら PlanMode を抜ける」という連携は可能か？
- それとも、両者は根本的に相容れないか？

**現在の判断:**
不採用を維持。理由は以下:
- PlanMode は Claude Code が独自の plan ファイルに書き込む。
  フレームワークは `docs/specs/` や `docs/plans/` にファイルを作る。
  出力先が競合する
- PlanMode の承認は Claude Code の UI で行う。
  フレームワークのゲート承認は STATUS.md で行う。承認経路が二重になる
- フレームワークの brainstorm フェーズが PlanMode の役割を包含している

**質問:** この分析は正しいか？PlanMode を部分的に活用する方法があれば知りたい。

---

### 4-B. auto-memory の不採用

**現状:**
CLAUDE.md に「Persist lessons in `docs/LEARNINGS.md`, not auto-memory.」と明記。
Claude Code の auto-memory（`~/.claude/projects/.../memory/`）ではなく、
プロジェクト内の `docs/LEARNINGS.md` に学習を記録する。

**疑問:**
- auto-memory と LEARNINGS.md を併用する方法はないか？
- 例えば「プロジェクト固有の技術的学習は LEARNINGS.md、
  ユーザーの好みやワークフロー設定は auto-memory」という役割分担は有効か？
- 現状は完全に auto-memory を排除しているが、それは最適か？

**現在の判断:**
LEARNINGS.md に一本化。理由は以下:
- LEARNINGS.md はバージョン管理され、チームで共有可能
- auto-memory はマシンローカルで、git に入らない
- confidence スコアによるフィルタリング（session-start.sh で >= 8 を注入）が
  auto-memory では実現困難
- 二重管理による情報の散逸リスク

**質問:** この判断は妥当か？auto-memory の部分活用に価値はあるか？

---

### 4-C. `TaskCreate`/`TaskUpdate` の不採用

**現状:**
Claude Code にはネイティブのタスク管理ツール（TaskCreate, TaskUpdate,
TaskGet, TaskList）があるが、フレームワークは STATUS.md をタスク状態の
single source of truth として使用し、これらのツールを活用していない。

**疑問:**
- STATUS.md とネイティブタスク管理を併用する方法はないか？
- 例えば「STATUS.md はフェーズ・ゲート管理、TaskCreate/TaskUpdate は
  実装フェーズ内のサブタスク管理」という役割分担は有効か？
- subagent-dev スキルでは TaskCreate を言及しているが
  実際には使われていない。これは矛盾ではないか？

**現在の判断:**
STATUS.md に一本化。理由は以下:
- TaskCreate/TaskUpdate はセッション内でのみ有効で、永続化されない
- STATUS.md はファイルとして永続化され、セッションをまたいで参照可能
- 二重管理は混乱のもと

**質問:** この判断は妥当か？実装フェーズ内での部分活用に価値はあるか？

---

## レビューで特に聞きたいこと

1. **2-A: QA の readOnly 問題に、我々が見落としている解法はあるか？**

2. **2-B: ゲート防御は 2 層で十分か？git tag 戦略は検討すべきか？**

3. **2-C: defense-in-depth は維持すべきか、除去すべきか？**

4. **3-A: compaction 対策としてフレームワーク側でできることはあるか？**

5. **4-A〜C の不採用判断のうち、再考すべきものはあるか？**
   特に、Claude Code の最新機能（2026年4月時点）で状況が変わった
   ものがあれば指摘してほしい。

6. **全体として、このフレームワークの Claude Code ネイティブ適応度を
   10 段階で評価するとどの程度か？改善の余地はどこにあるか？**
