# Skill：需求分析

## Purpose

將核准 Proposal 轉成明確、可測試、可追溯的 Requirement、NFR 與 Acceptance Criteria。

## Authoritative Inputs

- Proposal
- Living Specs
- Stakeholder Constraints

## Required Outputs

- requirements.md
- nfr.md
- Traceability 初稿

## Operating Rules

1. 先確認 Change ID、Risk Level、目前 State 與適用 Gate。
2. 必須引用 Requirement、Task、ADR 或 Policy ID；不得只引用聊天內容。
3. 不得自行核准風險、Release、Security Exception 或 Scope Expansion。
4. 發現衝突、缺失或不可逆風險時，輸出 `HUMAN_DECISION_REQUIRED`。
5. 所有輸出必須保存於 Repository，可被不同 AI 或人員接手。

## Completion Criteria

- 輸出符合對應 Template。
- 假設、風險、未解決問題與證據已列出。
- Execution State 已更新。
- 下一步及下一個 Gate 明確。
