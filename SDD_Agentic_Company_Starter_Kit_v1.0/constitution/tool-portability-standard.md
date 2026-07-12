# AI／工具可攜性標準

## 目標

更換 AI 模型、供應商、IDE、CLI Agent 或人員時，應能在不存取原聊天紀錄的條件下繼續工作。

## 必須外部化的資訊

- Requirement、NFR、Acceptance Criteria。
- Design、ADR、API／Data Contract。
- Tasks、Dependency、Owner、Status。
- 修改檔案清單與 Git Commit／PR。
- 測試、掃描、部署與觀測證據。
- 假設、限制、風險、未解決問題與下一步。

## 禁止作法

- 在正式 Requirement 中引用未保存於 Repository 的過往對話。
- 只有某個 Agent 私有 Memory 知道的商業規則。
- 以工具專用 Slash Command 取代正式 Change State。
- 只保存 AI 結論，不保存證據與決策依據。

## Portability Test

另一名未參與原對話的人員或不同 AI，在只讀取 Repository 後，必須能：

1. 說明 Change 目的、範圍、非範圍及風險。
2. 找到目前階段、下一項 Task 及阻塞事項。
3. 產生與原 Requirement 一致的測試計畫。
4. 執行或審查下一步而不依賴聊天記錄。
