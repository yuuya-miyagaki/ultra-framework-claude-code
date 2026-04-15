# プラットフォーム別デプロイ情報

> deploy スキルの従属ドキュメント。該当プラットフォームのセクションのみ参照する。

## Vercel

- [ ] next.config.js に `output: "standalone"` がないこと
- [ ] 環境変数を `printf '%s' | vercel env add` で設定（改行なし）
- [ ] Neon 連携は手動設定（`vercel integration add` は使わない）
- [ ] DEMO_MODE / 認証バイパスが無効であること
- [ ] `vercel --prod` でデプロイ後、ヘルスチェック URL を確認

## Cloud Run

- [ ] Dockerfile + `output: "standalone"` の整合性
- [ ] Cloud SQL 接続設定
- [ ] IAM 権限の最小設定
- [ ] コンテナイメージのビルドとプッシュ

## 共通

- [ ] 認証が有効であること（DEMO_MODE = blocker）
- [ ] 環境変数の一覧と設定状態
- [ ] DB マイグレーション実行
- [ ] 外部連携（Slack / Stripe 等）の接続テスト
- [ ] ヘルスチェックエンドポイントの応答確認

## トラブルシューティング

### 共通パターン

| 症状 | 原因候補 | 対処 |
|------|---------|------|
| デプロイ成功だが機能しない | 環境変数未設定 | プラットフォームの環境変数管理で設定、再デプロイ |
| 認証コールバック失敗 | OAuth App の URL 設定不備 | Homepage URL + Callback URL の両方を確認 |
| ビルド成功だがランタイムエラー | ローカルと本番の環境差異 | .env.local はプラットフォームで読まれない場合あり |

### Vercel 固有

| 症状 | 原因 | 対処 |
|------|------|------|
| `vercel deploy --prod` が "Unexpected error" | CLI の AbortController race condition (v51+) | `vercel redeploy <deployment-id>` で回避 |
| 環境変数が undefined | `.env.local` はランタイムで読まれない | `vercel env add` でプロジェクトレベル設定 + redeploy |
| middleware 非推奨警告 | Next.js 16 の仕様変更 | 機能影響なし。Auth.js の proxy 対応待ち |

### 外部サービス設定の網羅性ルール

外部サービス（OAuth App, Stripe, Slack 等）の設定変更を案内する場合:

- 関連する全フィールドを一括で案内すること
- 部分的な案内（例: Callback URL のみ）は二度手間を生む
- 設定項目のチェックリストを作成してから案内する
