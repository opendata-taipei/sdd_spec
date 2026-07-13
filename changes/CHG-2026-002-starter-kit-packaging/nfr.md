# CHG-2026-002 Non-functional Requirements

| ID | 類型 | Requirement | 驗證方式 | Threshold |
|---|---|---|---|---|
| NFR-PERF-002 | Performance | 192 個檔案規模的 package build／verify SHALL 快速完成 | CI timing | 各 10 秒內（不含依賴安裝） |
| SEC-PACKAGE-001 | Security | 封裝與驗證 SHALL 防止 path traversal、symlink escape、duplicate entry 與敏感資料混入 | Adversarial tests | 所有攻擊 fixture 被拒絕 |
| OPS-REL-002 | Reliability | 相同輸入 SHALL 產生可重現 ZIP bytes 與 checksum | Windows/Linux CI | SHA-256 完全一致 |
