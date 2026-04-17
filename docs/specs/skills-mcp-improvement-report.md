# Ultra Framework CC — Skills & MCP 改善調査レポート

> 作成日: 2026-04-16
> 改訂日: 2026-04-16（セカンドオピニオンレビュー反映）
> 対象: Ultra Framework Claude Code v0.7.2
> 調査範囲: ワークスペース内フレームワーク比較 + Web リサーチ + ギャップ分析

---

## 1. エグゼクティブサマリー

Ultra Framework CC v0.7.2 の Skills と MCP を、ワークスペース内の 4 フレームワーク
（Superpowers, gstack, Everything Claude Code, claude-code-best-practice）および
最新の Claude Code 公式機能と比較調査した。

### 現状評価

エージェント frontmatter は v0.7.x で大幅に前進済み。`maxTurns`, `readOnly`,
`permissionMode`, `effort`, `color` は全 10 エージェントに設定されている。
スキル frontmatter も `disable-model-invocation` + `user-invocable` は全 11 スキルに
導入済み。**ただし導入は不均一であり、一部のフィールドが未活用のまま残っている。**

| カテゴリ | 導入済み | 未活用 |
| -------- | -------- | ------ |
| スキル数 | 11 | qa フェーズのみスキルなし |
| スキル frontmatter | `name`, `description`, `disable-model-invocation`, `user-invocable` | `allowed-tools`, `paths`, `context`/`agent` |
| エージェント frontmatter | `maxTurns`, `readOnly`, `permissionMode`, `effort`, `color`, `skills`(implementer), `disallowedTools`(qa-browser) | `skills` preload（reviewer/security/qa）、`mcpServers` |
| MCP 構成 | Playwright（qa-browser 推奨） | 推奨カタログ・設定テンプレートなし |
| Hook イベント | 4/7 使用（SessionStart, PreToolUse x3） | Stop, SubagentStart, SubagentStop |

### v0.7.3 推奨スコープ（3 本柱）

レビューを踏まえ、**薄さを維持したまま効果が高い 3 点に絞る:**

1. **qa-verification スキル新設** — 唯一スキルなしの qa フェーズをカバー
2. **エージェント hardening** — reviewer/security に skills preload + 不均一部分の統一
3. **MCP カタログを extension として提供** — core 契約外、manual opt-in

---

## 2. 比較フレームワーク概要

### 2.1 Superpowers (v5.0.7)

- **スキル数:** 14（brainstorming, writing-plans, subagent-driven-development 等）
- **特徴的パターン:**
  - `<HARD-GATE>` タグによるスキル内制約
  - Visual Companion（Mermaid/Draw.io 連携の提案を brainstorming 内で実施）
  - Spec Self-Review チェックリスト
  - Skill から Skill へのチェーン（brainstorming → writing-plans → implementing）
- **MCP:** 未使用（ゼロ依存方針）
- **Hook:** SessionStart のみ（`hooks.json` + `hooks-cursor.json` でハーネス分岐）

**Ultra FC への示唆:**
- スキル内 `<HARD-GATE>` は state-machine.md のゲートと重複するが、スキル単体でも制約を明示する方式は堅牢
- Spec Self-Review はレビュースキルの前段として有効

### 2.2 gstack (v0.16.x)

- **スキル数:** 41+（各トップレベルディレクトリが 1 スキル）
- **特徴的パターン:**
  - **Preamble System:** 全スキルに共通プリアンブルを注入。`SKILL.md.tmpl` → `gen-skill-docs` で生成。セッション追跡、repo-mode 検出、テレメトリを含む
  - **PROACTIVE ルーティング:** スキル冒頭で「ユーザーの発話パターン → スキル起動」のマッピングテーブル
  - **allowed-tools:** frontmatter で `Bash`, `Read`, `AskUserQuestion` 等を明示制限
  - **Browse Binary:** Playwright をラップした専用 CLI（`$B` コマンド）
  - **Analytics JSONL:** `~/.gstack/analytics/skill-usage.jsonl` にスキル使用ログを記録
  - **3 層テスト:** 静的検証 / E2E (`claude -p`) / LLM-as-judge でスキル品質を検証
- **MCP:** 未使用（Browse binary で代替）

**Ultra FC への示唆:**
- `allowed-tools` の活用は今回の改善対象
- Preamble System は有用だが Ultra FC の薄さと矛盾する → 将来検討
- PROACTIVE ルーティングテーブルは `routing.md` の将来強化に参考

### 2.3 Everything Claude Code (ECC)

- **スキル数:** 183 / **コマンド数:** 79 / **エージェント数:** 48+
- **特徴的パターン:**
  - **MCP カタログ:** `mcp-configs/mcp-servers.json` に 20+ サーバー定義（Jira, GitHub, Firecrawl, Supabase, Memory, Vercel, Railway, Cloudflare x4, ClickHouse, Exa, Context7, Playwright, fal.ai 等）
  - **MCP 無効化:** `filterMcpConfig()` で `ECC_DISABLED_MCP_SERVERS` 環境変数によるサーバー単位の無効化
  - **MCP ヘルスチェック:** `mcp-health-check.js` が PreToolUse/PostToolUseFailure で死活監視。バックオフ・リコネクト・状態永続化を実装
  - **Hook プロファイル:** `ECC_HOOK_PROFILE` + `ECC_DISABLED_HOOKS` による実行時制御
- **Hook:** 全 7 イベント対応

**Ultra FC への示唆:**
- MCP カタログ方式は `extensions/` 戦略と親和性が高い → 今回採用
- MCP 無効化機構はカタログと同時に提供すべき
- ヘルスチェックは過剰 → 将来検討

### 2.4 claude-code-best-practice

- **構成:** ベストプラクティスドキュメント集 + Weather System 実装例
- **特徴的パターン:**
  - **Command → Agent → Skill:** コマンド（エントリ）→ エージェント（実行）→ スキル（知識）の 3 層分離
  - **Agent Skills vs Skills:** `skills:` preload（全文注入）と Skill ツール呼び出し（オンデマンド）の明確な区別
  - **Frontmatter 網羅文書:** スキル 13 フィールド、エージェント 16 フィールドを完全文書化
  - **Agent `disallowedTools`:** 読み取り専用エージェントへのツール拒否
  - **Agent `mcpServers`:** エージェント単位の MCP サーバー割り当て

**Ultra FC への示唆:**
- `skills:` preload は reviewer/security に適用 → 今回採用
- `mcpServers` per agent は qa-browser + Playwright で将来検討
- `disallowedTools` は readOnly エージェントの補強として将来検討（現状 `readOnly: true` + `permissionMode: plan` で同等の効果あり）

---

## 3. Claude Code 最新機能（2026 年 4 月時点）

### 3.1 スキル frontmatter — Ultra FC 導入状況

| フィールド | 説明 | Ultra FC 状況 |
| ---------- | ---- | ------------- |
| `name` | 表示名 | 導入済み（全 11） |
| `description` | 用途説明 | 導入済み（全 11） |
| `disable-model-invocation` | 自動起動無効化 | **導入済み（全 11）** |
| `user-invocable` | `/` メニュー表示 | **導入済み（全 11）** |
| `allowed-tools` | 許可ツール | **未導入** |
| `context: fork` | 隔離実行 | 未導入（将来検討） |
| `agent` | fork 時のエージェント | 未導入（将来検討） |
| `paths` | 自動アクティベーション | 未導入（将来検討） |
| `hooks` | スキルスコープフック | 未導入（将来検討） |
| `model` | モデル指定 | 未導入（将来検討） |
| `effort` | 努力レベル | 未導入（将来検討） |

### 3.2 エージェント frontmatter — Ultra FC 導入状況

| フィールド | 説明 | Ultra FC 状況 |
| ---------- | ---- | ------------- |
| `description` | 起動トリガー | **導入済み（全 10）** |
| `maxTurns` | 最大ターン数 | **導入済み（全 10）** |
| `readOnly` | 読み取り専用 | **導入済み（7/10）** |
| `permissionMode` | 権限モード | **導入済み（全 10）** |
| `effort` | 努力レベル | **導入済み（全 10）** |
| `color` | 表示色 | **導入済み（全 10）** |
| `model` | モデル指定 | **導入済み（全 10）** |
| `skills` | スキル preload | **部分導入**（implementer のみ `tdd`） |
| `disallowedTools` | ツール拒否 | **部分導入**（qa-browser のみ） |
| `mcpServers` | MCP 割り当て | 未導入 |
| `isolation: worktree` | Git worktree 隔離 | 未導入（将来検討） |
| `memory` | 永続メモリスコープ | 未導入 |
| `background` | バックグラウンド実行 | 未導入 |

### 3.3 Hook イベント

| イベント | 説明 | Ultra FC 状況 |
| -------- | ---- | ------------- |
| SessionStart | セッション開始 | **使用中**（session-start.sh） |
| PreToolUse | ツール実行前 | **使用中**（check-gate, check-tdd, check-destructive） |
| PostToolUse | ツール実行後 | 未使用 |
| Stop | セッション終了 | 未使用（慎重に検討 — 下記注記参照） |
| SubagentStart | サブエージェント起動 | 未使用 |
| SubagentStop | サブエージェント終了 | 未使用 |
| PreCompact | コンテキスト圧縮前 | 未使用 |

> **Stop Hook に関する注記:** STATUS.md への自動書き込みは、「誰がこの状態を
> 書いたのか分かりにくい」副作用がある。Ultra FC は STATUS を人間が読める
> 明示的な状態台帳として置くところに価値がある。最初の段階では自動更新ではなく
> 「WARNING を出す」「restart summary を出す」に留めるのが安全。

---

## 4. ギャップ分析（現状を正確に反映）

### 4.1 スキル

| ギャップ | 説明 | 優先度 |
| -------- | ---- | ------ |
| **qa フェーズにスキルなし** | Dev フェーズ 9 中、唯一スキルが紐づいていない | **高** |
| **`allowed-tools` 未導入** | 全 11 スキルでツール制限なし | 中（将来検討） |
| **スキルテスト基盤なし** | gstack は 3 層テストを持つが Ultra FC にはない | 低（将来検討） |

### 4.2 MCP

| ギャップ | 説明 | 優先度 |
| -------- | ---- | ------ |
| **推奨カタログなし** | MCP サーバーの選定ガイド・設定テンプレートが存在しない | **高** |
| **フェーズ別ヒントなし** | session-start.sh が MCP 推奨を出さない | 低（将来検討） |

### 4.3 エージェント

| ギャップ | 説明 | 優先度 |
| -------- | ---- | ------ |
| **`skills` preload が不均一** | implementer に tdd があるが、reviewer/security/qa に対応スキルがない | **高** |
| **`disallowedTools` が不均一** | qa-browser にはあるが、reviewer 系には readOnly で代替中 | 低（readOnly + plan で実質同等） |

### 4.4 Hook

| ギャップ | 説明 | 優先度 |
| -------- | ---- | ------ |
| **Stop 未使用** | セッション終了時のアクションなし | 低（WARNING のみなら将来検討可） |

---

## 5. 改善提案

### v0.7.3 スコープ（3 本柱）

レビューを踏まえ、薄さを壊さない範囲で 3 点に絞る。

#### 柱 1: qa-verification スキル新設

**ファイル:** `.claude/skills/qa-verification/SKILL.md`

```yaml
---
name: qa-verification
description: "QA phase verification: reproduce reported behavior, run test suites, generate evidence."
disable-model-invocation: true
user-invocable: false
---
```

**内容（日本語）:**

- テストスイート実行手順（プロジェクトの CLAUDE.md からコマンドを読む）
- 再現手順の構造化テンプレート
- エビデンス収集チェックリスト（テスト結果、ログ、スクリーンショット）
- qa-browser エージェントへの委譲ルール（UI サーフェスがある場合）
- QA レポートテンプレート（`docs/qa-reports/` 配置）

**根拠:** Dev フェーズで唯一スキルが紐づいていない。session-start.sh の QA ヒントにも
専用 skill 名が出ておらず、qa エージェント内にプロセスが埋まっている状態。

**連動変更:**

- `session-start.sh` の qa ヒントを更新: `HINT="skill: qa-verification / ..."`
- qa エージェントに `skills: [qa-verification]` を preload

#### 柱 2: エージェント hardening（skills preload 統一）

既存の frontmatter 基盤の上に、不均一な `skills` preload を統一する。

| エージェント | 現状 | 追加 |
| ------------ | ---- | ---- |
| reviewer | skills なし | `skills: [review]` |
| security | skills なし | `skills: [security-review]` |
| qa | skills なし | `skills: [qa-verification]`（柱 1 で新設） |
| implementer | `skills: [tdd]` | 変更なし |
| planner | skills なし | 変更なし（subagent-dev は手動 pull で十分） |

> **注記:** qa に tdd を preload する案はレビューで却下。QA は実装規律ではなく
> 検証と証拠収集であり、新設する qa-verification を preload すべき。

**`disallowedTools` について:** 現状 `readOnly: true` + `permissionMode: plan` で
読み取り専用制約は実質的に機能している。`disallowedTools` の追加は二重制約となり、
メンテナンスコストが増えるため今回は見送り。

#### 柱 3: MCP カタログを extension で提供

**ディレクトリ:** `extensions/mcp/`

```
extensions/mcp/
├── README.md              # 推奨 MCP サーバー一覧と選定ガイド
├── playwright.json        # Playwright MCP 設定テンプレート
├── github.json            # GitHub MCP 設定テンプレート
├── context7.json          # Context7 MCP 設定テンプレート
├── vercel.json            # Vercel MCP 設定テンプレート
└── figma.json             # Figma MCP 設定テンプレート
```

**設計方針:**

- core 契約外。`extensions/` は manual opt-in（CLAUDE.md Source of Truth に明記済み）
- 各 `.json` はそのまま `.mcp.json` や `settings.json` にマージ可能な形式
- README.md にフェーズ別の推奨マッピングを記載

**推奨 5 サーバー:**

| サーバー | 用途 | 推奨フェーズ |
| -------- | ---- | ------------ |
| Playwright | ブラウザ QA・UI 検証 | qa |
| GitHub | PR/Issue 操作 | deploy, review |
| Context7 | ライブラリドキュメント検索 | implement, brainstorm |
| Vercel | デプロイ管理 | deploy |
| Figma | デザイン参照 | brainstorm, implement |

---

### 将来検討（v0.8.0+）

以下は v0.7.3 では実装しない。薄さを壊すリスクがあるか、設計コストが高い。

| 項目 | 理由 |
| ---- | ---- |
| `allowed-tools` スキル frontmatter | 有効だが全 11 スキル × テスト → 次バージョンで |
| `paths` 自動アクティベーション | ルーティングを暗黙化するリスク |
| MCP 検出 (session-start.sh) | heavy な処理をセッション開始に入れたくない |
| Preamble System | gstack 的な厚い注入は Ultra FC の薄さと矛盾 |
| Agent Teams | Review Army 強化に有用だが、まず基盤を固める |
| Stop Hook | WARNING のみなら検討可だが、自動書き込みは危険 |
| Plugin System | 配布戦略は v1.0 以降 |
| スキルテスト基盤 | 有用だが優先度は低い |
| `disallowedTools` エージェント | readOnly + plan で実質同等。二重制約のコスト |

---

## 6. フレームワーク間の借用可能パターン一覧

| パターン | 出典 | 採否 | 理由 |
| -------- | ---- | ---- | ---- |
| Agent `skills` preload | best-practice | **v0.7.3 採用** | reviewer/security/qa に即適用 |
| MCP カタログ（extension 方式） | ECC | **v0.7.3 採用** | extensions/ 契約と一致 |
| `<HARD-GATE>` タグ | Superpowers | 見送り | state-machine.md のゲートで代替済み |
| Spec Self-Review | Superpowers | 見送り | review スキルに類似機能あり |
| `allowed-tools` frontmatter | gstack | **v0.8.0 候補** | 有効だがテスト工数が必要 |
| PROACTIVE ルーティング | gstack | 見送り | routing.md で十分、暗黙化リスク |
| MCP 無効化機構 | ECC | **v0.8.0 候補** | カタログ運用後に必要性を判断 |
| MCP ヘルスチェック | ECC | 見送り | 過剰。薄さに反する |
| Command → Agent → Skill 分離 | best-practice | 不要 | 既に類似構造を持つ |
| `disallowedTools` | best-practice | 見送り | readOnly + plan で同等 |
| Preamble System | gstack | 見送り | 薄さに反する |
| Agent Teams | Claude Code | **v0.8.0 候補** | Review Army 強化に有用 |
| Plugin System 配布 | ECC / Claude Code | 見送り | v1.0 以降 |
| 3 層スキルテスト | gstack | 見送り | 優先度低 |

---

## 7. v0.7.3 実装チェックリスト

| # | 柱 | 作業内容 | ファイル数 |
| --- | --- | -------- | ---------- |
| 1 | QA skill | qa-verification SKILL.md 新設 | 1 新規 |
| 2 | QA skill | session-start.sh の qa ヒント更新 | 1 編集 |
| 3 | Agent | qa.md に `skills: [qa-verification]` 追加 | 1 編集 |
| 4 | Agent | reviewer.md に `skills: [review]` 追加 | 1 編集 |
| 5 | Agent | security.md に `skills: [security-review]` 追加 | 1 編集 |
| 6 | MCP | extensions/mcp/ ディレクトリ + README.md + 5 json | 6 新規 |
| 7 | Sync | example project への反映（skill, agents, hook, mcp） | ~8 ファイル |
| 8 | Validator | check_framework_contract.py に qa-verification 追加 | 1 編集 |
| 9 | 検証 | run_eval.py --tier 1 全 PASS 確認 | - |

---

## 8. 結論

Ultra Framework CC v0.7.2 は「薄いカーネル + ステートマシン + pull-based スキル」
という設計思想で独自の強みを持ち、エージェント frontmatter も v0.7.x で大幅に
前進している。

v0.7.3 では**薄さを壊さず、不均一な部分を統一し、欠けているピースを埋める**
方針で 3 点に絞る:

1. **qa-verification スキル** — 唯一スキルなしの qa フェーズを埋める
2. **エージェント skills preload 統一** — reviewer/security/qa にスキルを紐づけ
3. **MCP カタログ (extension)** — core 契約外で推奨構成を提供

`paths` 自動起動、MCP 検出、Preamble System、Agent Teams は、基盤が固まった後で
十分。薄さがこのフレームワークの差別化であり、ここを壊す拡張は後回しにすべきである。
