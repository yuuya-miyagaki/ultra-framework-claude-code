---
name: qa-verification
description: "QA phase verification: reproduce reported behavior, run test suites, generate evidence."
disable-model-invocation: true
user-invocable: false
---

# QA 検証プロセス

> qa agent が QA フェーズで参照する。再現・テスト実行・エビデンス収集の
> 手順を標準化し、根拠なき完了を防止する。

## いつ使うか

- qa フェーズで検証を実施するとき
- テスト実行とエビデンス収集が必要なとき
- 再現手順を構造化する必要があるとき

## テストスイート実行手順

1. プロジェクトの `CLAUDE.md` または `README.md` からテストコマンドを読む
2. テストを実行し、結果を記録する
3. lint / type-check / build も実行する（該当する場合）
4. 全結果を QA レポートに記載する

```
確認事項:
- テストコマンドが明記されているか
- 全テストが PASS か（FAIL がある場合は原因を記録）
- lint / type-check エラーがないか
```

## 再現手順テンプレート

検証対象の振る舞いごとに以下を記録する:

```
### 検証項目: <項目名>
- 前提条件: <セットアップ手順>
- 操作: <実行した操作>
- 期待結果: <plan/spec の受入条件>
- 実際結果: <観測された結果>
- 判定: PASS / FAIL
```

## エビデンス収集チェックリスト

QA レポート完了前に以下を全て実施する:

- [ ] テストスイートを実行し結果を記録した
- [ ] lint / type-check / build を実行した（該当する場合）
- [ ] plan の受入条件と突合した
- [ ] 各検証項目に PASS / FAIL 判定を付与した
- [ ] FAIL 項目にはブロッカーとして原因を記録した

## 機能対照表（必須出力）

QA 開始前に以下を作成:

| # | 要件/plan の機能 | 検証対象 | 検証方法 | 判定 |
|---|----------------|---------|---------|------|

- requirements + plan の機能リストから全項目を列挙
- 「検証対象」が存在しない = 実装漏れ → implement へ差し戻し

## qa-browser 委譲ルール

`STATUS.md` の `ui_surface: true` の場合:

1. ブラウザ検証が必要な項目を特定する
2. qa-browser エージェントに委譲する（ページ、操作、期待動作を指定）
3. 返却されたエビデンスを QA レポートに統合する

qa-browser は browser-assist スキルを使用。
`$B` 利用可能時はブラウザ自動操作、未インストール時は Playwright MCP で検証。

## plan 事前チェックリスト

plan に `## QA チェックリスト` が定義されている場合:
1. そのリストを baseline として QA チェック項目に採用する
2. QA 実行中に発見した不足項目は追加で起票できる（plan に縛られない）
3. 追加項目には「plan 外追加」と明記する

## QA レポート出力

- `docs/qa-reports/` に `QA-REPORT.template.md` を使用して配置
- 全検証項目の判定一覧を含める
- ブロッカーがあれば STATUS.md に記録

## 禁止事項

- エビデンスなき PASS を出さない
- テストを実行せずに「前回と同じ」で省略しない
- FAIL 項目を隠さない
- 検証範囲を勝手に縮小しない
