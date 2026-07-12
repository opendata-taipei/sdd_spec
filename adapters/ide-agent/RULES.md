# IDE Agent Rules

- IDE 建議不是核准的 Requirement。
- Auto-complete 產出仍須滿足 Task、Test 與 Review。
- 不允許跨 Task 批次修改未宣告檔案。
- 每次接受大型修改前，先檢查 Diff 與 Contract 影響。
- 將工具專用規則留在 Adapter；正式設計必須寫入 `changes/` 或 `specs/living/`。
