# Skill：技術與架構設計

## Purpose

建立可實作、可回滾、符合 Constitution 的 Technical Design，並識別需要 ADR 的決策。

## Authoritative Inputs

- Requirements
- Living Architecture
- Security Baseline

## Required Outputs

- design.md
- ADR proposal
- Impact Analysis

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
