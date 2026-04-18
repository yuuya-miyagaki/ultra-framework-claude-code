---
name: integration-assist
description: "外部サービス連携ガイド。gstack $B によるブラウザ自動操作+handoff でユーザー工数を最小化"
disable-model-invocation: true
user-invocable: false
---

# Integration Assist

> 外部サービス（Slack, Stripe, Firebase 等）の API 連携セットアップを
> Claude Code が主導し、ユーザーの操作を最小限（パスワード入力・承認クリック）に抑える。

## いつ使うか

- プロジェクトに外部サービスを接続する必要がある場合
- API キー・OAuth Token・Webhook URL の取得が必要な場合
- ユーザーが非エンジニアで、サービス設定ページの操作に不安がある場合

## 前提: $B バイナリ解決

gstack browse がインストールされている場合、ブラウザ自動操作が可能。
未インストール時はフォールバック（案内型）に切り替える。

```bash
# $B 解決ロジック（各 Bash ブロック冒頭で実行）
_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
B=""
[ -n "$_ROOT" ] && [ -x "$_ROOT/.claude/skills/gstack/browse/dist/browse" ] && \
  B="$_ROOT/.claude/skills/gstack/browse/dist/browse"
[ -z "$B" ] && [ -x ~/.claude/skills/gstack/browse/dist/browse ] && \
  B=~/.claude/skills/gstack/browse/dist/browse
```

- `$B` が見つかった場合 → **自動操作モード**（Step 3-4 でブラウザ操作）
- `$B` が見つからない場合 → **案内モード**（URL + 手順をテキストで提示）

## ワークフロー

### Step 1: サービス特定

ユーザーの要求から連携先サービスを特定する。
不明な場合はユーザーに確認。

### Step 2: ドキュメント調査

API ドキュメントを調査し、必要な情報を特定する。

- WebSearch / WebFetch で公式ドキュメントを検索・読解
- 必要な認証情報の種類を特定（API Key, OAuth Token, Webhook URL 等）
- セットアップ手順（設定ページ URL、必要なスコープ、コールバック URL）を把握
- プロジェクトで使う SDK / ライブラリを特定

### Step 3: ブラウザ自動操作（$B 利用時）

```bash
$B goto <サービスの設定ページ URL>
$B snapshot -i                        # フォーム要素を検出
$B fill @eN "<アプリ名>"              # アプリ名を自動入力
$B fill @eN "<コールバック URL>"       # URL を自動入力
$B fill @eN "<説明文>"                # 説明を自動入力
# 選択肢がある場合
$B select @eN "<オプション>"
$B click @eN                          # 次へ進む
```

**案内モードの場合**: 上記の代わりにテキストで手順を提示。
コピペ用のテキスト（アプリ名、URL、スコープ等）を提供する。

### Step 4: handoff（ユーザー最小介入）

```bash
$B handoff "パスワードを入力して「Allow」ボタンを押してください"
# → 可視ブラウザが開く（同じページ、同じ入力状態）
# ← ユーザー: パスワード入力 / 承認クリック / 2FA のみ
$B resume
# → AI に制御復帰（Cookie・セッション完全保持）
```

**案内モードの場合**: ユーザーに「○○の画面で承認してください。
完了したら教えてください」と伝え、待機する。

### Step 5: 結果取得 + 設定ファイル生成

```bash
$B snapshot                           # Token 表示ページを取得
$B text @eN                           # Token/Key のテキストを抽出
```

取得した認証情報で設定ファイルを生成:

1. `.gitignore` に `.env` が含まれていることを確認（なければ先に追加）
2. `.env` に Token/Key を書き込む
3. 接続コードを実装（SDK インストール含む）

**案内モードの場合**: ユーザーに Token を貼り付けてもらう。
受領後は即座に `.env` に書き込み、以後の出力で値を再掲しない。

### Step 6: 接続テスト + 最終承認

テストコードを実行して API 疎通を確認する。
結果をユーザーに提示し、最終承認を得る。

- テスト成功 → ユーザーに「接続成功」を報告、完了
- テスト失敗 → エラー内容を分析、修正して再テスト

## Credential Boundary

| 種別 | $B あり（自動操作モード） | $B なし（案内モード） |
|------|------------------------|---------------------|
| **パスワード / 2FA** | `$B handoff` 経由。chat 禁止 | ユーザーが自分のブラウザで入力。chat 禁止 |
| **Token / API Key** | `$B text` で自動取得→即 `.env` | ユーザーが chat に貼り付け→即 `.env`。以後再掲しない |

## セキュリティルール

| ルール | 理由 |
|--------|------|
| パスワード・2FA は chat に入力させない | 認証情報の永続的な漏洩リスクを排除 |
| Token/Key は受領後すぐ `.env` に書き、以後の出力で再掲しない | コンテキスト残留を最小化 |
| `.env` 作成前に `.gitignore` に `.env` があることを確認する | リポジトリへの漏洩を防ぐ |
| `.env` の値をレポートやログに含めない | 出力経由の漏洩を防ぐ |
| handoff 理由文にパスワード・Token を含めない | ログ経由の漏洩を防ぐ |
| `.env` の stage/commit は `check-secrets.sh` hook で防止される | PaC による強制 |

## コンテキスト予算

このファイルは **L2（タスクファイル）** として扱う。
外部サービス連携タスクを実行するセッションでのみ読み込む。
