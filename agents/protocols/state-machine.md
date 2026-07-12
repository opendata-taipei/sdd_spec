# Change State Machine

合法狀態：

```text
DRAFT
→ PROPOSAL_REVIEW
→ REQUIREMENTS_REVIEW
→ DESIGN_REVIEW
→ READY_FOR_IMPLEMENTATION
→ IMPLEMENTING
→ VERIFYING
→ RELEASE_READY
→ RELEASING
→ MONITORING
→ CLOSED
```

例外狀態：

- `BLOCKED`
- `REJECTED`
- `ROLLED_BACK`
- `CANCELLED`

## 狀態轉換原則

- 每次轉換必須有 Evidence 與 Actor。
- Agent 可以建議轉換，但只有政策允許的 Gate Owner 可核准需要人工 Gate 的轉換。
- 不得跳過 Requirements、Design、Verification 或 Release Gate，除非符合已核准的 Minor／Emergency 流程。
