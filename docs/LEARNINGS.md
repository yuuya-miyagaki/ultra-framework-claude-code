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
- [confidence:9] `update-gate.sh` は `current_refs.<gate>` を "approved" 文字列で上書きする。ゲート承認後に手動で正しいファイルパスを復元する必要がある。将来のバージョンで修正すべきバグ。
- [confidence:8] contract validator のエージェント構造チェック（hallucination guard, turn limit）は大文字小文字を区別する。"Do not" ではなく "do not"、"Complete" ではなく "complete" で書く必要がある。
- [confidence:8] standard profile は Dev-lean に保つべき。Client 専用 artifact（docs/client/, docs/translation/）を standard に含めると、対応する skill/agent なしでは不整合になる。Client 機能は full profile に集約する。
- [confidence:7] 大規模変更（L サイズ）の実装は Phase 分割+並列サブエージェントが効果的。v0.8.0 では 18 タスクを 6 フェーズに分割し、各フェーズ内で最大 5 並列実行した。
