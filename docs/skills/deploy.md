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

## 3回失敗ルール

デプロイ試行は「本番デプロイ成功」というゴールに対してカウントする。
手法を変えてもカウントはリセットしない。3回失敗時:

1. 現状のサマリーを STATUS.md に記録
2. 試行した手法と結果の一覧を提示
3. 代替案（別アプローチ or 手動対応 or スキップ）を提案
4. ユーザーに判断を委ねる

## Completion

deploy フェーズ完了時に `DEPLOY-CHECKLIST.template.md` をベースにした
チェックリストを `docs/qa-reports/` に保存し、STATUS.md の deploy ゲートを
更新する。
