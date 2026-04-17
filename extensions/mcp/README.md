# MCP サーバーカタログ

> Ultra Framework CC 推奨 MCP サーバー設定テンプレート集。
> **extensions/ は core 契約外。manual opt-in で利用する。**

## 使い方

1. 必要な `.json` ファイルを選ぶ
2. プロジェクトルートの `.mcp.json` の `mcpServers` にマージする
3. 必要に応じて環境変数やパスを調整する

## 推奨サーバー一覧

| サーバー | ファイル | 用途 | 推奨フェーズ |
| -------- | -------- | ---- | ------------ |
| Playwright | `playwright.json` | ブラウザ QA・UI 検証 | qa |
| GitHub | `github.json` | PR/Issue 操作 | deploy, review |
| Context7 | `context7.json` | ライブラリドキュメント検索 | implement, brainstorm |
| Vercel | `vercel.json` | デプロイ管理 | deploy |
| Figma | `figma.json` | デザイン参照 | brainstorm, implement |

## フェーズ別推奨マッピング

| フェーズ | 推奨 MCP |
| -------- | -------- |
| brainstorm | Context7, Figma |
| plan | — |
| implement | Context7, Figma |
| review | GitHub |
| qa | Playwright |
| security | — |
| deploy | GitHub, Vercel |

## 注意事項

- MCP サーバーはセッション全体で有効になる。フェーズ単位の自動切替は行わない。
- 不要なサーバーを有効にするとコンテキスト消費が増える。必要なものだけ有効にする。
- 各 JSON ファイルの `env` セクションに必要な環境変数を設定すること。
- JSON 内の `description` と `recommended_phase` はメタデータフィールド。Claude Code は無視するため、マージ時に残しても削除しても動作に影響しない。
- `.mcp.json` に実トークンを設定した場合、**必ず `.gitignore` に追加すること**。トークン漏洩を防ぐため、`.mcp.json` をコミットしない運用を推奨する。
