# 翻訳マッピング

<!-- exit-check: 主要用語マッピング完了・不変条件明示・未解決は open-questions に転記済み → handover へ -->

クライアント用語を機能的意味と実装ヒントに変換する 3 層マッピング。

## 用語マップ

| クライアント用語 | 機能的意味 | 実装ヒント |
|----------------|----------|-----------|
| gate | フェーズ間の必須承認チェックポイント。ユーザー承認なしでは次フェーズに進めない | hooks/check-gate.sh + scripts/update-gate.sh で STATUS.md のゲート状態を管理 |
| PaC | ドキュメントの記述ではなく hook スクリプトで強制するルール体系 | .claude/hooks/*.sh で PreToolUse deny を実装。違反時はツール実行をブロック |
| translation mapping | クライアント用語を機能仕様と実装方針に変換する 3 層テーブル | docs/translation/mapping.md（このファイル自体がサンプル実体） |
| thin framework | CLAUDE.md を最小限に保ち、詳細をルールファイル・スキルに分散する設計原則 | CLAUDE.md 700 語上限。check_framework_contract.py で語数を自動検証 |
| scaffold | プロファイルに基づくプロジェクト初期構築 | bin/setup.sh --profile で テンプレートから docs/ 配下にファイルを生成 |
| artifact | フェーズ完了に必要な成果物。evidence-based completion の根拠 | 各フェーズの exit-check コメントで必要 artifact を定義 |
| hook | Claude Code のツール実行前後に走る shell スクリプト | .claude/hooks/preToolUse/*.sh, .claude/hooks/postToolUse/*.sh |
| contract validator | フレームワーク構造・内容の自動検証ツール | scripts/check_framework_contract.py でプレースホルダ残存・ファイル欠損を検出 |

## 不変条件

クライアントが変更不可と明言した制約。

- CLAUDE.md の語数は 700 語を超えてはならない（thin framework 原則）
- ハードゲートはユーザーの明示的承認なしにスキップできない
- 完了判定は artifact の存在を証拠とする（チャット上の自信度は不可）
- hook による PaC 強制は設計原則であり、ドキュメント記述のみの代替は不可

## 前提条件

検証済みの前提。

- Claude Code CLI が PreToolUse / PostToolUse フック機構を提供している
- STATUS.md がセッション間の唯一の状態管理手段である
- フレームワーク利用者は 1 リポジトリ = 1 プロジェクトの構成で運用する
- テンプレートファイルは templates/ に大文字命名で配置し、scaffold 時に docs/ へ小文字で展開する

## 未解決事項

→ `docs/client/open-questions.md` を参照
