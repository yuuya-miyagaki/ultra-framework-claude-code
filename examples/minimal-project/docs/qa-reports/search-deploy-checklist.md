# デプロイチェックリスト — 社内ナレッジ検索アシスタント

## 対象

- プロジェクト: 社内ナレッジ検索アシスタント
- デプロイ先: Vercel
- 日付: 2026-04-10

## deploy-prep

- [x] デプロイ先が PLAN の Deploy Target と一致している
- [x] 環境変数の一覧と設定状態を確認した
- [x] DB マイグレーションが準備されている
- [x] インフラ（DNS、SSL 等）がセットアップ済み

## Security Blockers

- [x] 認証が有効である（DEMO_MODE / auth bypass が無効）
- [x] デフォルト管理者パスワードが変更済み
- [x] HTTPS が設定済み
- [x] 環境変数にシークレットのハードコードがない

**ブロッカー該当:** なし

## プラットフォーム別チェック

### Vercel

- [x] next.config.js に `output: "standalone"` がないこと
- [x] 環境変数を `printf '%s' | vercel env add` で設定（改行なし）
- [x] Neon 連携は手動設定（`vercel integration add` は使わない）
- [x] DEMO_MODE / 認証バイパスが無効
- [x] `vercel --prod` でデプロイ後、ヘルスチェック URL を確認

### 共通

- [x] 認証が有効であること（DEMO_MODE = blocker）
- [x] 環境変数の一覧と設定状態
- [x] DB マイグレーション実行
- [x] 外部連携（Slack / Stripe 等）の接続テスト
- [x] ヘルスチェックエンドポイントの応答確認

## staging

- [x] ステージング環境にデプロイ済み
- [x] E2E テストまたは手動テスト完了
- 結果: 全テストパス

## uat

- [x] ユーザー受入テスト完了
- [x] ユーザーから本番投入の承認を取得
- 結果: 承認済み

## production

- [x] 本番デプロイ実行
- [x] ヘルスチェック応答確認
- [x] 主要画面のスモークテスト完了
- デプロイ URL: https://knowledge-search.example.vercel.app

## post-deploy

- [x] 外部連携の動作確認
- [x] モニタリング / アラート設定確認
- 結果: 正常稼働

## 総合判定

- 判定: completed
- 次のアクション: ship フェーズへ移行
