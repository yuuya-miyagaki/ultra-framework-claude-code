# 受入条件

## リリースゲート

- ゲート: 主要クエリで期待結果が返り、review / QA / security evidence が揃っていること

## 機能受入条件

- AC-001: キーワード入力で関連ドキュメント一覧が表示される
- AC-002: フィルター適用時に結果が絞り込まれる
- AC-003: 各結果に出典スニペットが表示される

## 非機能受入条件

- AC-NFR-001: 主要クエリ 10 件の p95 応答時間が 2 秒以内
- AC-NFR-002: mock index 停止時にエラーメッセージと再試行導線を表示する

## 必要な証拠

- テスト: 主要クエリ手動検証と対象コマンド実行結果
- レビュー: `docs/qa-reports/search-review.md`
- レポート: `docs/qa-reports/search-qa.md`, `docs/qa-reports/search-security.md`

## 承認

- 承認者: Product Owner
- 日付: 2026-04-09
