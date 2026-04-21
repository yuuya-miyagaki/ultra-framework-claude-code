---
name: security-review
description: "OWASP-based security review process with evidence checklist and exit criteria."
disable-model-invocation: true
user-invocable: false
---

# セキュリティレビュープロセス

> security agent がセキュリティフェーズで参照する。OWASP Top 10 ベースの
> チェックリストと evidence 要件により、スキャンなき PASS を防止する。

## いつ使うか

- security フェーズで security agent がレビューを実施するとき
- 変更が認証・秘密情報・外部入力・データ露出に関わるとき

## OWASP Top 10 チェックリスト（簡略版）

変更に該当する項目のみ実施する。全項目を機械的に埋めない。

- [ ] **Injection**: SQL, Command, XSS の入力パスを確認
- [ ] **Broken Authentication**: 認証フロー・セッション管理の変更を確認
- [ ] **Sensitive Data Exposure**: secrets in code, logs, 環境変数を確認
  - 暗号化カラムを返す API: decrypt() / masking 処理が適用されているか確認
  - API レスポンスに暗号文（Base64 / hex 等の非可読文字列）が含まれていないか確認
- [ ] **Security Misconfiguration**: デフォルト設定・CORS・ヘッダーを確認
- [ ] **Vulnerable Dependencies**: 依存パッケージの既知脆弱性を確認

## Evidence Checklist

レビュー完了前に以下を全て実施する:

- [ ] Grep で secrets/credentials パターンを検索した
- [ ] 外部入力のサニタイゼーションを確認した
- [ ] dependency audit を実行した（該当する場合）
- [ ] 全 finding に severity と remediation を付与した

## Exit Criteria

- OWASP 該当項目の確認完了（非該当は理由付きでスキップ）
- 全 finding に severity 付与済み
- `docs/qa-reports/` にセキュリティレポートが存在する
- deploy blocker があれば STATUS.md に記録済み

## 禁止事項

- スキャンなき PASS を出さない
- 「内部用だから安全」で省略しない
- severity 未付与の finding を報告しない
