# 設計ノート: 社内ナレッジ検索アシスタント

## 入力

- ブレインストーミング記録: `docs/specs/search-brainstorm-record.md`
- 要件: `docs/requirements/PRD.md`

## 問題整理

- 背景: 社内資料が複数の保存先に分かれ、目的の情報を探す負荷が高い
- 判断が必要な論点: 初期版で検索品質より運用フローを優先するか
- 制約条件: 社内ネットワーク内限定、mock index 使用

## 推奨アプローチ

- 採用方針: mock index を用いた薄い検索フローを先に構築する
- 採用理由: Claude Code 用の flow を固めつつ、実装・review・QA の証跡を早く整えられる
- 検討した代替案と不採用理由: 実検索基盤先行（インフラコスト高）、外部 SaaS（セキュリティポリシー違反）

## コンポーネント分解

- 分割方針: UI / API / index の 3 層に分離
- 各ユニットの責務:
  - SearchForm: 検索入力と送信
  - ResultList: 結果一覧・スニペット・フィルター表示
  - search API client: mock index 呼び出しとエラーハンドリング

## インターフェース定義

- ユニット間の契約:
  - SearchForm → search API: `query: string, filter?: string`
  - search API → ResultList: `SearchResult[]` (title, summary, snippet, type)
- 公開 API:
  - `searchDocuments(query, filter?)`: `Promise<SearchResult[]>`

## データフロー / 構造

- 入力: 検索キーワードとドキュメント種別
- 処理: UI から検索 API を呼び出し、mock index で関連文書を返す
- 出力: タイトル、概要、出典スニペット付きの検索結果

## 依存関係

- 依存方向: SearchForm → search API → mock index（循環なし）
- 外部依存: 社内ドキュメント一覧 CSV

## エラーハンドリング

- 想定失敗: index 応答失敗、空結果、フィルター指定ミス
- 対応: ユーザーへ再試行導線と空結果メッセージを表示する
- エラー伝播の方針: API client でキャッチし、UI にエラー状態を返す

## テスト戦略

- 単体: 入力整形と検索リクエストの組み立て
- 結合: フィルター適用時の結果変化
- エッジケース: 空クエリ、index 停止、結果 0 件
- 手動確認: 主要クエリと失敗時メッセージ

## 次のステップ

- [x] 実装計画を作成する → `docs/plans/search-implementation-plan.md`
- テンプレート名: `PLAN.template.md`
- 本設計ノートのパスを PLAN の「参照設計」に記載すること
