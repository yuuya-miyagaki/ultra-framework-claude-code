# 出荷と文書化

> security 完了後の最終フェーズ。成果物を引き渡し文書にまとめ、プロジェクト知見を
> 記録して Dev サイクルを閉じる。

## いつ使うか

- `security` フェーズが完了し、`gate_approvals.security` が `approved` または
  `n/a` になったとき
- Dev サイクルの最終段階に入るとき

## 前提条件

以下がすべて満たされていること:

- `gate_approvals.review`: `approved`
- `gate_approvals.qa`: `approved` または `n/a`（理由付き）
- `gate_approvals.security`: `approved` または `n/a`（理由付き）
- `current_refs` に review / qa / security の成果物パスが記録されている

前提が満たされていなければ、ship に入らず不足を報告する。

## ship フェーズ

### Step 1: 証拠収集

以下の証拠を `current_refs` から収集し、存在と内容を確認する:

- 実装計画: `current_refs.plan`
- レビュー記録: `current_refs.review`
- QA レポート: `current_refs.qa`
- セキュリティレビュー: `current_refs.security`

いずれかが欠落・不完全であれば ship を中断し、ユーザーに報告する。

### Step 2: TO-CLIENT 作成

テンプレート `HANDOVER-TO-CLIENT.template.md` を使用して
`docs/handover/TO-CLIENT.md` を作成する。

記載内容:
- 実装サマリ（何を作ったか、主要な設計判断）
- 変更ファイル一覧
- テスト結果・QA 結果の要約
- 残留リスク・既知の制限事項
- 運用上の注意点

**証拠への参照を必ず含める。** 主張だけの記述は禁止。

### Step 3: ユーザー確認

TO-CLIENT の内容をユーザーに提示し、承認を得る。
承認後、`docs/STATUS.md` の `phase` を `docs` に更新する。

## docs フェーズ

### Step 4: LEARNINGS 更新

`docs/LEARNINGS.md` に以下を追記する:

- このタスクで得た技術的知見
- うまくいったパターン・避けるべきパターン
- フレームワーク改善の提案（あれば）

既存エントリと重複しないこと。該当なしなら「該当なし」と明記する。

### Step 5: STATUS 最終更新

`docs/STATUS.md` を更新する:

- `phase`: `docs`
- `next_action`: `dev_ready_for_client ゲートの申請`
- `session_history` に ship/docs の完了エントリを追加

### Step 6: ゲート申請

ユーザーに `dev_ready_for_client` ゲートの承認を申請する。

承認後:
- `gate_approvals.dev_ready_for_client` を `approved` に更新
- `mode` を `Client` に切り替える（次の Client フェーズに戻る場合）
- または、タスクが完全に完了していればその旨を記録する

## Red Flags（禁止事項）

- 証拠が揃っていない状態で TO-CLIENT を作成しない
- レビュー・QA・セキュリティの結果を要約せず省略しない
- LEARNINGS を「特になし」で済ませない（最低限の振り返りは必須）
- ユーザー承認なしに `dev_ready_for_client` を `approved` にしない
- ship/docs の作業を 1 ステップに圧縮しない（証拠収集 → 文書作成 → 承認の順序を守る）

## コンテキスト予算

- ship: `current_refs` の全成果物 + TO-CLIENT テンプレート
- docs: LEARNINGS + STATUS のみ
- 過去のチャット履歴は参照しない（成果物が唯一のソース）
