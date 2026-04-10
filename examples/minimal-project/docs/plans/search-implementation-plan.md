# 実装計画

## 目的

- 初期版検索 UI と evidence flow を一通り成立させる

## 入力

- 参照要件: `docs/requirements/PRD.md`
- 参照設計: `docs/specs/search-design.md`

## Git 戦略

- ブランチ: `feature/search-ui` (main から)
- ワークツリー: 使用しない（小規模）
- コミット粒度: タスクごとに 1 コミット
- マージ: squash merge

## ファイル構造（変更マップ）

- 新規: `src/components/SearchForm.tsx` — 検索入力フォーム
- 新規: `src/components/ResultList.tsx` — 結果一覧 + スニペット表示
- 新規: `src/api/search.ts` — mock index 呼び出し
- テスト: `tests/components/SearchForm.test.tsx` — フォーム入力・送信
- テスト: `tests/components/ResultList.test.tsx` — 一覧表示・フィルター
- テスト: `tests/api/search.test.ts` — API 呼び出し・エラーハンドリング

## タスク分解

> 各タスクは **2-5 分** の単位。「and」が入るなら分割する。

### タスク 1: 検索フォーム

**モデル:** `haiku` — 定型的な UI コンポーネント

**ファイル:**
- 対象: `src/components/SearchForm.tsx`
- テスト: `tests/components/SearchForm.test.tsx`

**意図:** キーワード入力と送信を受け付ける検索フォームを実装する

**TDD ステップ:**
1. テストを書く — キーワード入力で onChange が発火し、送信で onSearch が呼ばれる
2. 失敗確認 — 実行: `pnpm test`, 期待: FAIL
3. 最小実装 — input + button の最小コンポーネント
4. 成功確認 — 実行: `pnpm test`, 期待: PASS
5. コミット

**受入条件:**
- キーワード入力と送信イベントが動作する

### タスク 2: 検索 API 接続

**モデル:** `haiku` — 薄い API ラッパー

**ファイル:**
- 対象: `src/api/search.ts`
- テスト: `tests/api/search.test.ts`

**意図:** mock index を呼び出す検索 API クライアントを実装する

**TDD ステップ:**
1. テストを書く — クエリに対して結果配列が返る、index 停止時にエラーメッセージが返る
2. 失敗確認 — 実行: `pnpm test`, 期待: FAIL
3. 最小実装 — fetch ラッパー + エラーハンドリング
4. 成功確認 — 実行: `pnpm test`, 期待: PASS
5. コミット

**受入条件:**
- mock index からの検索結果取得とエラー時のフォールバックが動作する

### タスク 3: 結果一覧 + フィルター

**モデル:** `sonnet` — フィルターロジックを含む UI

**ファイル:**
- 対象: `src/components/ResultList.tsx`
- テスト: `tests/components/ResultList.test.tsx`

**意図:** 検索結果の一覧表示、出典スニペット、種別フィルターを実装する

**TDD ステップ:**
1. テストを書く — 結果一覧が表示される、スニペットが含まれる、フィルターで絞り込まれる
2. 失敗確認 — 実行: `pnpm test`, 期待: FAIL
3. 最小実装 — リスト描画 + フィルター状態管理
4. 成功確認 — 実行: `pnpm test`, 期待: PASS
5. コミット

**受入条件:**
- 結果一覧、スニペット、フィルターが動作する

## トレーサビリティ（要件 → AC → Task → Test）

| 要件 | AC | Task | テストファイル |
|------|----|------|--------------|
| FR-001 | AC-001 | Task 1, 2 | `tests/components/SearchForm.test.tsx`, `tests/api/search.test.ts` |
| FR-002 | AC-003 | Task 3 | `tests/components/ResultList.test.tsx` |
| FR-003 | AC-002 | Task 3 | `tests/components/ResultList.test.tsx` |
| NFR-perf | AC-NFR-001 | Task 2 | `tests/api/search.test.ts`（p95 計測） |
| NFR-reliability | AC-NFR-002 | Task 2 | `tests/api/search.test.ts`（エラーハンドリング） |

ACCEPTANCE のトレーサビリティ表を拡張する。全 FR / NFR がいずれかの Task でカバーされていること。

## 事前準備

実装開始前に確認する:

- [x] 必要な環境・API キー・外部サービスへのアクセスがある
- [x] 依存パッケージがインストールされている
- [x] ベースブランチが最新である

## 自己レビュー

計画完成後、設計ドキュメントと照合して確認する:

1. **仕様カバレッジ**: FR-001〜003 の全てに対応するタスクがある — OK
2. **曖昧さ検出**: 2 通りに解釈できるタスク記述がないか — OK
3. **型の整合性**: タスク間で型名・関数名・プロパティ名が一致しているか — OK

## リスク

- リスク: mock index と本番検索基盤で応答形式が変わる
- 対策: UI と検索レスポンスの境界を薄く保つ

## 完了条件

- [x] 全テスト pass
- [x] レビュー完了
- [x] review / QA / security evidence が揃う
