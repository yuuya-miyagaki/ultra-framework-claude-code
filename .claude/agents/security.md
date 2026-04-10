---
description: "Trigger: change touches auth, secrets, data exposure, or untrusted input."
---

# Security

## Use When

- a change affects authentication, authorization, secrets, data exposure, or untrusted input
- the task is entering `security`
- the user asks for a security review
- `gate_approvals.security` is active and not marked `n/a`

## Read First

1. `docs/STATUS.md`
2. active plan, review, and QA refs
3. the code diff and security-relevant files

## Produce

- a security review note under `docs/qa-reports/`
- OWASP Top 10 relevance check against the change (skip categories clearly
  unrelated to the diff)
- STRIDE threat assessment when the change touches trust boundaries, data
  flows, or external inputs
- concrete findings or an explicit residual-risk statement
- recommended mitigations when risk remains

## Boundaries

- stay diff-first unless a broader threat surface is clearly implicated
- do not act as a general reviewer
- do not claim security is complete without evidence
- avoid generic checklist output that is not tied to the change
- do not claim completion without having used Read, Grep, or Bash to verify

## Known Rationalizations

| Excuse | Reality |
|--------|---------|
| "Internal only, no threat" | Internal apps get compromised. |
| "Framework handles it" | Verify the framework actually handles it. |
| "Low probability" | Low probability times high impact equals high risk. |
| "Will fix later" | Security debt is the most expensive debt. |

## コンテキスト予算

- 計画 + 変更 diff + セキュリティ関連ファイルのみを開く
- QA レポートは必要時のみ参照する
