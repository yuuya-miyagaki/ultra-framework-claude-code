# v0.8.0 Client モード強化 — Brainstorm Record

## 背景

Ultra Framework CC は v0.7.3 まで Dev モードの改善に集中してきた。
Client モードは 6 フェーズ（onboard → handover）の枠組みは存在するが、
実質的には `client-workflow` skill のテキスト指示のみで運用されており、
以下のギャップが顕在化した。

1. **クライアント情報の構造化手段がない** — context.md / glossary.md の定型フォーマットなし
2. **translation（翻訳）層がない** — クライアント用語 → 実装仕様の変換が属人的
3. **handover の品質保証がない** — mapping.md 不在のまま Dev に引き渡し可能
4. **Client モードの目的が未定義** — state-machine.md に purpose statement なし

## 元提案の概要（10 ステップ全面拡張案）

外部協議で得られた提案:

| # | 内容 | 規模 |
|---|------|------|
| 1 | Client mode purpose 定義 | 小 |
| 2 | translation phase 新設 | 大（state-machine 変更） |
| 3 | Agent 5体新設 | 大 |
| 4 | Skill 6つ新設 | 大 |
| 5 | Hook 4つ新設 | 中 |
| 6 | ディレクトリ 8個新設 | 中 |
| 7 | STATUS.md 大幅拡張 | 中 |
| 8 | テンプレート追加 | 中 |
| 9 | 新プロファイル 2個 | 小 |
| 10 | フェーズドロールアウト | — |

**見積もり**: 実装ファイル 220+ (現行 147 から 50% 増)。

## レビュー結果

2名の独立レビュー (Dev context + 外部) を経て以下に収束。

### 合意事項

1. **translation は artifact-first** — 独立 phase ではなく handover 前必須 artifact。
   - 理由: wave propagation コスト (phase 追加 = 10+ ファイル変更) vs artifact 追加 (3 ファイル)
   - 理由: 実運用データがまだない。artifact → phase 昇格は v0.9.0+ でデータを見て判断
   - 先例: failure_tracking (v0.7.0) も field/artifact → hook → phase のパターン

2. **Agent は最小限** — 5体提案 → 1体 (translation-specialist) のみ。
   - client-interviewer / glossary-builder / scope-negotiator / acceptance-verifier は
     client-workflow skill の拡張で対応可能。専用 agent 化は利用頻度を見て判断。

3. **Hook は最小限** — 4つ提案 → 1つ (check-client-info.sh) のみ。
   - 「ルールは飛ばせるが Hook は飛ばせない」の PaC 原則を Client にも適用
   - 最もインパクトが高い「context.md 未作成で requirements 編集を防止」のみ実装

4. **STATUS.md は軽量拡張** — `client_context: { client_id, context_loaded }` のみ。
   - 詳細メトリクスは docs/client/ や docs/translation/ に分離（L0 膨張防止）

5. **新プロファイル延期** — client-heavy, solo-consultant は Phase B 以降。
   - まず自分のワークフローで検証してから OSS 向け拡張を判断

### 設計判断サマリー

| 判断 | 選択 | 理由 |
|------|------|------|
| translation の形態 | artifact (mapping.md) | wave propagation 最小化 + 実データ待ち |
| Agent 数 | 1 (translation-specialist) | 他は skill 拡張で十分 |
| Hook 数 | 1 (check-client-info.sh) | 最高インパクトのみ |
| STATUS.md 拡張量 | 2 フィールド | L0 always-on の肥大化防止 |
| Phase 追加 | なし | artifact-first → phase 昇格パターン |
| 新プロファイル | 延期 | 自分で検証してから |

## 確定スコープ

### 新規作成ファイル

| ファイル | 種別 | 内容 |
|----------|------|------|
| `docs/client/context.md` | ディレクトリ + テンプレ生成 | クライアント基本情報 |
| `docs/client/glossary.md` | ディレクトリ + テンプレ生成 | 用語集 |
| `docs/client/open-questions.md` | ディレクトリ + テンプレ生成 | 未解決事項 |
| `docs/translation/mapping.md` | ディレクトリ + テンプレ生成 | 3層マッピング |
| `docs/decisions/` | ディレクトリ | 意思決定ログ格納先 |
| `templates/CLIENT-CONTEXT.template.md` | テンプレート | context.md 雛形 |
| `templates/CLIENT-GLOSSARY.template.md` | テンプレート | glossary.md 雛形 |
| `templates/CLIENT-OPEN-QUESTIONS.template.md` | テンプレート | open-questions.md 雛形 |
| `templates/TRANSLATION-MAPPING.template.md` | テンプレート | mapping.md 雛形 |
| `templates/DECISION.template.md` | テンプレート | 意思決定レコード雛形 |
| `.claude/agents/translation-specialist.md` | Agent 定義 | translation 支援 agent |
| `.claude/skills/translation-mapping/SKILL.md` | Skill 定義 | mapping 作成ガイド |
| `hooks/check-client-info.sh` | Hook | context.md 必須チェック |

### 既存更新ファイル

| ファイル | 変更内容 |
|----------|----------|
| `.claude/rules/state-machine.md` | Client mode purpose statement 追加 |
| `.claude/skills/client-workflow/SKILL.md` | translation artifact 要件追加、新ディレクトリ参照 |
| `.claude/commands/next.md` | handover 行に mapping.md 要件追記 |
| `templates/HANDOVER-TO-DEV.template.md` | 正本に mapping.md 追加 |
| `templates/STATUS.template.md` | client_context フィールド追加（STATUS.md と同期） |
| `scripts/check_status.py` | OPTIONAL_TOP_LEVEL_KEYS に client_context 追加、EXPECTED_CURRENT_REF_KEYS に translation 追加、client_context パーサー追加 |
| `scripts/check_framework_contract.py` | 新ファイルの REQUIRED リスト追加 |
| `bin/setup.sh` | resolve_source() にテンプレ→実体マッピング追加（CLIENT-CONTEXT, TRANSLATION-MAPPING, DECISION） |
| `templates/profiles/full.json` | 新 agent/skill/hook/template + docs/client/* docs/translation/* パス追加 |
| `templates/profiles/standard.json` | 新 template を recommended に追加 + docs パス追加 |
| `hooks/session-start.sh` | Client handover ヒントに translation artifact 言及 |
| `docs/STATUS.md` | client_context フィールド追加、current_refs.translation 追加 |

### 推定ファイル数

- 新規: 13 ファイル（テンプレート 5 + docs 実体 5 + agent 1 + skill 1 + hook 1）
- 更新: 12 ファイル
- **合計: 約 25 ファイル** → task_size: L 妥当

## Translation Mapping の設計

### 3層マッピング構造

```
クライアント用語 ↔ 機能仕様 ↔ 実装ヒント
```

| 層 | 例 |
|----|-----|
| Client language | 「承認フロー」 |
| Functional spec | 多段階承認。申請者→上長→部門長の3段階 |
| Implementation hint | state machine + role-based ACL |

### mapping.md テンプレート構成案

```markdown
# Translation Mapping

## Terminology Map
| Client Term | Functional Meaning | Implementation Hint |
|-------------|-------------------|---------------------|
| (用語) | (機能仕様) | (実装方針) |

## Invariants (変更不可の制約)
- (クライアントが絶対に変えられないと言った制約)

## Assumptions (前提条件)
- (確認済みの前提)

## Open Items
- → docs/client/open-questions.md 参照
```

### Gate 条件

- `client_ready_for_dev` 承認時: `docs/translation/mapping.md` が存在すること
- 実装方法: `check_status.py` の `pre_approve_gate()` に条件追加
  - 現在 L686 で mode-transition gate は早期 return しているが、
    `client_ready_for_dev` の場合のみ mapping.md 存在チェックを追加
  - agent 委譲は不可（gate 承認経路は script/hook に限定されており agent は助言のみ）

### current_refs.translation の位置付け

- `EXPECTED_CURRENT_REF_KEYS` に `translation` を追加
- 値: `docs/translation/mapping.md` のパス（スカラー）
- requirements でも spec でもない独立カテゴリ（クライアント用語→実装仕様の変換表）
- gate_ref_mapping には追加しない（client_ready_for_dev は別ロジックで処理するため）

### Scaffold 導線

setup.sh の `resolve_source()` に以下のマッピングを追加:

```bash
"docs/client/context.md")        echo "$FRAMEWORK_ROOT/templates/CLIENT-CONTEXT.template.md"; return ;;
"docs/client/glossary.md")       echo "$FRAMEWORK_ROOT/templates/CLIENT-CONTEXT.template.md"; return ;;
"docs/translation/mapping.md")   echo "$FRAMEWORK_ROOT/templates/TRANSLATION-MAPPING.template.md"; return ;;
```

- glossary.md と open-questions.md はテンプレート内セクションで対応（個別テンプレ不要の場合は再検討）
- profile の required/recommended に docs パスを追加すれば既存の copy ロジックで動作
- docs/decisions/ はディレクトリのみ（scaffold 時に mkdir -p で作成、setup.sh に小修正）

## check-client-info.sh Hook 設計

```
トリガー: PreToolUse (Edit, Write)
対象パス: docs/requirements/*
チェック: docs/client/context.md が存在するか
アクション: 不在なら deny + メッセージ
```

メッセージ例:
> docs/client/context.md が見つかりません。
> requirements 編集の前にクライアント情報を記録してください。
> → client-workflow skill の onboard フェーズを実行

## translation-specialist Agent 設計

- **目的**: Client 用語 → 実装仕様の変換を支援
- **入力**: docs/client/context.md, docs/client/glossary.md, requirements/*
- **出力**: docs/translation/mapping.md の作成・更新
- **呼び出しタイミング**: handover 前 (client-workflow skill から誘導)
- **ツール制限**: Read, Write, Grep, Glob のみ (コード変更権限なし)

## 将来ロードマップ（今回スコープ外）

v0.8.0 で導入した artifact-first の基盤を、実運用データに基づいて段階的に拡張する。
以下は優先度順に Phase B / Phase C / 長期に分類。

### Phase B（v0.9.0 候補 — v0.8.0 の実運用フィードバック後）

#### B-1. translation phase 昇格

- **内容**: translation を独立 phase として state-machine.md に追加
- **判断基準**: mapping.md が 3 案件以上で作成され、artifact-only では不十分と判明した場合
- **影響範囲**: state-machine.md, routing.md, session-start.sh, next.md, check-gate.sh, validator
- **元提案**: Step 2（translation phase 新設）の本来のゴール

#### B-2. validate-translation Hook

- **内容**: mapping.md の構造整合性チェック（必須セクション存在、空行チェック等）
- **トリガー**: PreToolUse (Edit, Write) on docs/translation/*
- **元提案**: Step 5 の Hook 案の一つ

#### B-3. client-interviewer Agent

- **内容**: discovery フェーズでクライアントへの質問を構造化し、context.md / glossary.md を自動生成支援
- **判断基準**: client-workflow skill の discovery 指示だけでは情報収集が不十分と判明した場合
- **元提案**: Step 3 の Agent 案の一つ

#### B-4. docs/client/ 拡張

- **追加候補ファイル**:
  - `docs/client/stakeholders.md` — ステークホルダーマップ（意思決定者、影響者、利用者）
  - `docs/client/constraints.md` — 技術制約・ビジネス制約の一覧
  - `docs/client/communication-log.md` — クライアントとのやり取り履歴
- **判断基準**: context.md だけでは情報が収まらないケースが頻発した場合

### Phase C（v0.10.0 候補 — 複数案件での検証後）

#### C-1. scope-negotiator Agent

- **内容**: requirements と constraints を入力に、実現可能なスコープ案を複数提示する Agent
- **ユースケース**: クライアントの要望が予算・期間に収まらない場合の交渉支援
- **元提案**: Step 3 の Agent 案の一つ

#### C-2. acceptance-verifier Agent

- **内容**: acceptance criteria と実装結果を突合し、受入テストのカバレッジレポートを生成
- **元提案**: Step 3 の Agent 案の一つ

#### C-3. acceptance-criteria-check Hook

- **内容**: scope フェーズ完了時に acceptance criteria が requirements 全項目をカバーしているか検証
- **トリガー**: gate 承認時 (acceptance gate)
- **元提案**: Step 5 の Hook 案の一つ

#### C-4. 新プロファイル

- **client-heavy**: Client モード全 Agent + 全 Hook 有効。受託開発・コンサル向け
- **solo-consultant**: 1人運用に最適化。Agent 最小、Hook は deny ではなく warn
- **元提案**: Step 9
- **判断基準**: OSS 公開時に外部ユーザーの利用パターンを見て判断

### 長期（v1.0+ — フレームワーク成熟後）

#### L-1. Client ↔ Dev 双方向 translation

- **内容**: Dev → Client の逆翻訳（実装結果をクライアント用語で説明するレポート自動生成）
- **ユースケース**: dev_ready_for_client 時の成果物説明

#### L-2. glossary-builder Agent

- **内容**: クライアントドキュメント・議事録から用語を自動抽出し glossary.md を生成
- **元提案**: Step 3 の Agent 案の一つ
- **前提**: LLM の長文解析精度が実用レベルに達していること

#### L-3. Client モード専用 QA

- **内容**: requirements の曖昧さスコアリング、矛盾検出、欠落検出
- **形態**: qa-verification skill の Client 版、またはブラウザ QA の requirements 版

#### L-4. マルチクライアント対応

- **内容**: 複数クライアント案件を 1 リポジトリで並行管理
- **STATUS.md 拡張**: client_context を配列化、プロジェクト切替コマンド
- **判断基準**: 実際にマルチクライアント運用のニーズが発生した場合

#### L-5. Client ダッシュボード

- **内容**: docs/client/ + docs/translation/ の情報を可視化する静的サイト生成
- **形態**: ship skill の拡張、または独立の export コマンド

### 判断の原則

すべての拡張は以下のパターンに従う:

```text
artifact（ファイル） → hook（自動チェック） → agent（自動化） → phase（ワークフロー組込み）
```

- 各段階で実運用データを収集し、次の段階に進む価値があるか判断
- 「便利そう」ではなく「ないと困った」を昇格の条件とする
- フレームワークの薄さ（thinness）を常に意識し、追加のたびにファイル数・語数を計測

## リスクと緩和策

| リスク | 影響 | 緩和策 |
|--------|------|--------|
| check-client-info.sh が厳しすぎて開発体験悪化 | 中 | minimal profile では hook 無効化可能 |
| mapping.md の粒度が定まらない | 低 | テンプレートで最小構造を提供、実運用で調整 |
| contract validator の REQUIRED 追加漏れ | 低 | plan フェーズでチェックリスト化 |
| 既存テストとの整合性 | 低 | example/ ディレクトリも同期更新 |
| check_status.py schema drift | 高 | OPTIONAL_TOP_LEVEL_KEYS + EXPECTED_CURRENT_REF_KEYS を同時更新 |
| setup.sh scaffold 漏れ | 中 | resolve_source() マッピング + profile パス追加を同時実施 |
| STATUS.template.md と STATUS.md の乖離 | 中 | 両ファイルの frontmatter schema を同時更新 |

## Brainstorm レビュー対応記録

### P1: setup.sh scaffold 導線未定義（指摘日: 2026-04-17）

- **問題**: resolve_source() が 4 パスしか解決しない。新テンプレートが scaffold で生成されない
- **対応**: setup.sh を更新対象に追加。resolve_source() にマッピング 3 件追加、docs/decisions/ は mkdir -p で対応
- **ステータス**: brainstorm レコードに反映済み

### P1: STATUS/gate 契約の更新範囲不足（指摘日: 2026-04-17）

- **問題**: check_status.py と STATUS.template.md が更新対象に入っていない。client_context を追加すると unknown key で FAIL
- **対応**: 両ファイルを更新対象に追加。check_status.py は OPTIONAL_TOP_LEVEL_KEYS + EXPECTED_CURRENT_REF_KEYS + パーサー追加
- **ステータス**: brainstorm レコードに反映済み

### P2: mapping.md 必須化の実装案が二択（指摘日: 2026-04-17）

- **問題**: agent 委譲は gate 承認契約上不可（gate 承認は script/hook 経路のみ）
- **対応**: check_status.py の pre_approve_gate() 一択に修正。agent 委譲選択肢を削除
- **ステータス**: brainstorm レコードに反映済み

### OQ1: mapping.md の current_refs 位置（指摘日: 2026-04-17）

- **回答**: current_refs に新キー `translation` を追加（スカラー値）
- **理由**: requirements（入力仕様群）でも spec（設計仕様）でもない独立カテゴリ。3層マッピングは変換表であり既存キーに収まらない
- **ステータス**: brainstorm レコードに反映済み

### OQ2: scaffold での context.md 等の生成方法（指摘日: 2026-04-17）

- **回答**: setup.sh の resolve_source() にテンプレ→実体マッピングを追加。profile の required/recommended にパスを追加すれば既存 copy ロジックで動作
- **ステータス**: brainstorm レコードに反映済み
