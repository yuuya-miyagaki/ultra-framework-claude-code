# QA レポート

## 対象

- 変更内容: 検索フロー MVP
- 環境: 社内 staging

## 実施した確認

- [x] 主要クエリ 10 件で結果表示を確認
- [x] ドキュメント種別フィルターで結果が変化することを確認
- [x] index 停止時に再試行導線が表示されることを確認

## 実行コマンド

```bash
pnpm lint
pnpm test
```

## 結果

- Pass: lint, unit test, manual query scenarios
- Fail: なし
- Skip: E2E 自動化は次フェーズ

## Blockers

- なし
