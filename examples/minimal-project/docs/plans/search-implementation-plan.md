# 実装計画

## 目的

- 初期版検索 UI と evidence flow を一通り成立させる

## 入力

- 参照要件: `docs/requirements/PRD.md`
- 参照設計: `docs/specs/search-design.md`

## 作業分解

1. 検索入力と結果一覧の UI を実装する
2. mock index を使った検索 API 呼び出しを接続する
3. review, QA, security evidence を作成する

## リスク

- リスク: mock index と本番検索基盤で応答形式が変わる
- 対策: UI と検索レスポンスの境界を薄く保つ

## 検証

- 実行コマンド: `pnpm test`, `pnpm lint`
- 確認観点: 主要クエリ、フィルター、失敗時導線

## 完了条件

- 主要機能が動作し、review / QA / security evidence が揃う
