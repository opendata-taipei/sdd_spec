# Generic CLI Agent Adapter

- 工作根目錄為 Repository Root。
- 寫入前先列出預計修改檔案並確認位於 Task Scope。
- 執行測試只能使用專案核准命令。
- 不得讀取 `.env`、Secret Store、Production Credential。
- 完成後執行 `python scripts/validate_sdd.py` 與 `python scripts/portability_check.py`。
- 若 Repository 已初始化 Git，執行對應 Change 的 Drift Check。
