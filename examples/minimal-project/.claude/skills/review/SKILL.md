---
name: review
description: "Evidence-based review process with severity classification and exit criteria."
disable-model-invocation: true
user-invocable: false
---

# レビュープロセス

> reviewer agent がレビューフェーズで参照する。severity 分類と evidence checklist
> により、根拠のない PASS/FAIL を防止する。

## いつ使うか

- review / qa フェーズで reviewer agent がレビューを実施するとき
- レビュー結果の severity 分類が必要なとき

## Severity 分類

| Severity | 定義 | 例 |
|----------|------|-----|
| Critical | 動作不正・データ破壊・セキュリティ穴 | 未処理例外、認証バイパス |
| Major | 品質劣化・保守性低下・仕様不整合 | テスト欠落、命名不統一、scope 超過 |
| Minor | 改善提案・コスメティック | コメント追加、リファクタ提案 |

全 finding にいずれかの severity を付与する。未分類の finding は報告しない。

## Evidence Checklist

レビュー完了前に以下を全て実施する:

- [ ] diff を Read/Grep で実読した（chat summary ではなく実ファイル）
- [ ] plan/spec の受入条件と突合した
- [ ] 未カバーのエッジケースを列挙した
- [ ] 全 finding に severity と confidence（1-10）を付与した

## Exit Criteria

- 全 finding に severity 付与済み
- PASS/FAIL 判定を明記（理由付き）
- `docs/qa-reports/` にレビューレポートが存在する
- confidence < 7 の finding には注意書きを付与済み

## 禁止事項

- evidence なき PASS 判定を出さない
- diff を読まずにレビュー結果を出さない
- severity 未付与の finding を報告しない
