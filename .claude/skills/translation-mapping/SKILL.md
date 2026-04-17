---
name: translation-mapping
description: "Client用語から実装仕様への3層マッピング作成ガイド"
disable-model-invocation: true
user-invocable: false
---

# Translation Mapping

> Client フェーズで収集したビジネス用語を、Dev フェーズが直接利用できる
> 実装仕様へ変換するための3層マッピングを作成・管理するガイド。

## いつ使うか

- handover フェーズに入る前に `docs/translation/mapping.md` を作成する必要がある場合
- Client 用語と実装用語の間に乖離が生じており、引き渡し文書の品質に影響する恐れがある場合
- Dev エージェントがビジネス用語を誤解するリスクを事前に排除したい場合

## 作成手順

1. `docs/client/context.md` と `docs/client/glossary.md` を読み、プロジェクトのドメイン背景と定義済み用語を把握する
2. `docs/requirements/*`（PRD.md・SCOPE.md・ACCEPTANCE.md）を走査し、クライアント固有の用語・フレーズを抽出する
3. 抽出した各用語を以下の3層で変換し、`docs/translation/mapping.md` に記録する

   | 層 | 項目 | 記述内容 |
   |----|------|---------|
   | L1 | **Client Term** | クライアントが使用する原文用語 |
   | L2 | **Functional Meaning** | その用語が指す業務上の意味・ふるまい |
   | L3 | **Implementation Hint** | 実装時に対応するモデル・API・コンポーネント候補 |

4. **Invariants（不変条件）** を記録する — ビジネスルール上、いかなる実装でも変更できない制約を列挙する
5. **Assumptions（前提条件）** を記録する — マッピング作成時点でユーザーと合意済みの仮定を列挙する
6. **Open Items（未解決事項）** を記録する — 情報不足または解釈が分かれる用語を列挙し、ユーザー確認待ちとしてマークする

## テンプレート参照

マッピングファイルの構造は以下のテンプレートに従うこと。

```
templates/TRANSLATION-MAPPING.template.md
```

## Agent 連携

mapping 作成を `translation-specialist` エージェントに委任可能。Task ツールで以下のように呼び出す。

```
Task: translation-specialist
Instruction: docs/requirements/* を読み、docs/translation/mapping.md を3層マッピング形式で作成してください。
```

委任する場合は、事前に `docs/client/glossary.md` が存在することを確認すること。
存在しない場合は先に glossary を作成するか、Open Items として記録する。

## コンテキスト予算

このファイルは **L2（タスクファイル）** として扱う。常時読み込みではなく、
mapping 作成タスクを実行するセッションでのみ読み込む。
