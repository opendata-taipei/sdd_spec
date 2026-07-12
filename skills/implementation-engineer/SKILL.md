# Skill：規格化實作

## Purpose

只在已核准 Task 範圍內修改程式碼，先建立測試或驗證證據，持續更新 Execution State。

## Authoritative Inputs

- Approved Task
- Design
- Codebase

## Required Outputs

- Code Changes
- Test Results
- State Update
- Handoff

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
