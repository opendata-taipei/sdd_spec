---
name: security-reviewer
description: 執行威脅建模、安全需求審查與安全測試證據檢查時使用。
---

# Skill：安全審查

## Purpose

檢查資料分類、權限、信任邊界、Secret、Audit、供應鏈與威脅，禁止自行接受剩餘風險。

## Authoritative Inputs

- Constitution
- Design
- Code Diff
- Scan Results

## Required Outputs

- Security Findings
- Required Controls
- Human Decision Requests

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
