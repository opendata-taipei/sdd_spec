---
name: intake-triage
description: 受理新需求、確認範圍並進行風險分級與 Change 初始化時使用。
---

# Skill：需求受理與風險分級

## Purpose

將模糊請求轉成 Change Intake，判斷 L0～L4、Owner、必要 Gate 與是否可進入 Proposal。

## Authoritative Inputs

- 原始請求
- Project Constitution
- Risk Model

## Required Outputs

- Risk Classification
- Change ID 建議
- 缺失資訊
- Gate List

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
