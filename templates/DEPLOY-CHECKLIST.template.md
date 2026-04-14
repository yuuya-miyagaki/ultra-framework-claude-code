# デプロイチェックリスト
<!-- 正本: deploy skill -->

## 対象

- プロジェクト: <記入>
- デプロイ先: <Vercel / Cloud Run / Docker / VPS>
- 日付: <記入>

## deploy-prep

- [ ] デプロイ先が PLAN の Deploy Target と一致している
- [ ] 環境変数の一覧と設定状態を確認した
- [ ] DB マイグレーションが準備されている
- [ ] インフラ（DNS、SSL 等）がセットアップ済み

## Security Blockers

- [ ] 認証が有効である（DEMO_MODE / auth bypass が無効）
- [ ] デフォルト管理者パスワードが変更済み
- [ ] HTTPS が設定済み
- [ ] 環境変数にシークレットのハードコードがない

**ブロッカー該当:** なし / あり → <記入>

## プラットフォーム別チェック

<該当プラットフォームのみ記入>

### Vercel

- [ ] next.config.js に `output: "standalone"` がないこと
- [ ] 環境変数を `printf '%s' | vercel env add` で設定（改行なし）
- [ ] Neon 連携は手動設定（`vercel integration add` は使わない）
- [ ] DEMO_MODE / 認証バイパスが無効
- [ ] `vercel --prod` でデプロイ後、ヘルスチェック URL を確認

### Cloud Run

- [ ] Dockerfile + `output: "standalone"` の整合性
- [ ] Cloud SQL 接続設定
- [ ] IAM 権限の最小設定

### 共通

- [ ] 認証が有効であること（DEMO_MODE = blocker）
- [ ] 環境変数の一覧と設定状態
- [ ] DB マイグレーション実行
- [ ] 外部連携（Slack / Stripe 等）の接続テスト
- [ ] ヘルスチェックエンドポイントの応答確認

## staging

- [ ] ステージング環境にデプロイ済み
- [ ] E2E テストまたは手動テスト完了
- 結果: <記入>

## uat

- [ ] ユーザー受入テスト完了
- [ ] ユーザーから本番投入の承認を取得
- 結果: <記入>

## production

- [ ] 本番デプロイ実行
- [ ] ヘルスチェック応答確認
- [ ] 主要画面のスモークテスト完了
- デプロイ URL: <記入>

## post-deploy

- [ ] 外部連携の動作確認
- [ ] モニタリング / アラート設定確認
- 結果: <記入>

## 総合判定

- 判定: completed / blocked
- 次のアクション: <記入>
<!-- exit-check: 全チェック完了・プロダクション稼働確認済み → ship へ -->
