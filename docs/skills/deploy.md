# Deploy Skill

## Overview

deploy フェーズはセキュリティレビュー完了後、ship の前に実行する。
デプロイ先の確認、環境構築、ステージング検証、本番投入、事後確認を
構造的に行うことで、場当たり的なデプロイ試行を防止する。

## Deploy Substeps

```
deploy-prep   → デプロイ先確認、環境変数リスト、インフラセットアップ
staging       → ステージング環境での検証
uat           → ユーザー受入テスト
production    → 本番デプロイ + ヘルスチェック
post-deploy   → 外部連携テスト、モニタリング設定
```

## deploy-prep チェックリスト

PLAN の Deploy Target セクションを再読し、以下を確認する:

- [ ] デプロイ先プラットフォームが Plan と一致している
- [ ] 環境変数の一覧と設定状態を確認
- [ ] DB マイグレーションが準備されている
- [ ] インフラ（DNS、SSL 等）がセットアップ済み

## Mandatory Security Blockers

以下のいずれかが true の場合、production デプロイをブロック:

- [ ] 認証が無効（DEMO_MODE, auth bypass 等）
- [ ] デフォルト管理者パスワードが変更されていない
- [ ] HTTPS が未設定
- [ ] 環境変数にシークレットのハードコードがある

該当する場合:
1. STATUS.md に blocker として記録
2. ユーザーに明示的にリスクを説明
3. ユーザーが「リスクを受容する」と明言した場合のみ続行可能

## プラットフォーム別チェックリスト

### Vercel

- [ ] next.config.js に `output: "standalone"` がないこと
- [ ] 環境変数を `printf '%s' | vercel env add` で設定（改行なし）
- [ ] Neon 連携は手動設定（`vercel integration add` は使わない）
- [ ] DEMO_MODE / 認証バイパスが無効であること
- [ ] `vercel --prod` でデプロイ後、ヘルスチェック URL を確認

### Cloud Run

- [ ] Dockerfile + `output: "standalone"` の整合性
- [ ] Cloud SQL 接続設定
- [ ] IAM 権限の最小設定
- [ ] コンテナイメージのビルドとプッシュ

### 共通

- [ ] 認証が有効であること（DEMO_MODE = blocker）
- [ ] 環境変数の一覧と設定状態
- [ ] DB マイグレーション実行
- [ ] 外部連携（Slack / Stripe 等）の接続テスト
- [ ] ヘルスチェックエンドポイントの応答確認

## staging / uat

- ステージング環境で E2E テスト（または手動テスト）を実行する
- PLAN の External Integrations セクションがある場合、外部連携テストを実施する
- UAT の結果をユーザーに報告し、本番投入の承認を得る

## production

- 本番デプロイを実行する
- ヘルスチェックエンドポイントの応答を確認する
- 主要画面のスモークテストを実施する

## post-deploy

- 外部連携（Slack 通知、Webhook 等）の動作確認
- モニタリング / アラート設定の確認
- デプロイ完了を STATUS.md に記録する

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

## Deploy と Failure Rule の関係

deploy フェーズのゴール単位:

- deploy-prep → staging → uat → production → post-deploy は別ゴール
- 同一サブステップ内の再試行が3回失敗 → second-opinion 発動
- サブステップ間の移動はカウントをリセット

例:
- production デプロイが3回失敗 → second-opinion（ゴール = "production デプロイ成功"）
- staging 成功 → production 失敗1回 → staging に戻って修正 → production 再挑戦
  → これは production の2回目（staging の修正はカウント外）

## Completion

deploy フェーズ完了時に `DEPLOY-CHECKLIST.template.md` をベースにした
チェックリストを `docs/qa-reports/` に保存し、STATUS.md の deploy ゲートを
更新する。
