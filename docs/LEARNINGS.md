# 蓄積された教訓

> このファイルは Claude Code 向け運用から得た durable learning を残すための場所です。
> 一時的な作業メモや会話の要約ではなく、次回以降に再利用できる学びだけを残します。

## 技術

<!-- category: tech -->

- [confidence:8] `CLAUDE.md` は薄く保ち、詳細ルールは pull-based にした方が Claude Code では安定しやすい。

## プロセス

<!-- category: process -->

- [confidence:9] `docs/STATUS.md` を短い状態ファイルとして維持すると、再開時の迷いが減る。

## コミュニケーション

<!-- category: communication -->

- [confidence:8] gate 承認は会話中で曖昧にせず、明示的に記録した方が後続の判断がぶれない。

## フレームワーク改善

<!-- category: framework -->

- [confidence:7] specialist を増やす前に、token と routing の実利があるかを確認する。
- [confidence:8] agent の skills preload を追加する際は profile 定義（templates/profiles/*.json）も同時に更新しないと scaffold drift が起きる。
- [confidence:8] MCP テンプレートは npx に `-y` フラグを付けないと初回起動時の対話プロンプトで止まる。ワークスペース内の既存例に合わせること。
- [confidence:7] extensions/ に配置する設定テンプレートは、実サーバー接続検証まではスコープに含めにくい。構造検証と実接続検証を明示的に分けて記録すべき。
