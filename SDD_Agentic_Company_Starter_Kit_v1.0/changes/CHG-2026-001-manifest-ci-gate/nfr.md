# CHG-2026-001 Non-functional Requirements

| ID | 類型 | Requirement | 驗證方式 | Threshold |
|---|---|---|---|---|
| NFR-PERF-001 | Performance | Manifest check SHALL 在一般 GitHub runner 上快速完成 | CI timing | 5 秒內（不含 Python setup） |
| SEC-APP-001 | Security | Check SHALL 僅讀取 repository 檔案且不得執行 Manifest 內容 | Code review | 無動態程式執行、無網路存取 |
| OPS-REL-001 | Reliability | Check SHALL 在 Windows 與 Linux 產生相同的 POSIX 相對路徑清單 | Automated test | 相同 fixture 得到相同結果 |
