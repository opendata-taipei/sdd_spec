# CHG-2026-001 Technical Design

## Design Summary

在既有 `validate-sdd` job 中直接執行 Manifest 產生器的 `--check` 模式。檢查只比較記憶體中的預期資料與現有 JSON，不寫入檔案；失敗訊息指向相同腳本的重建模式。

## Requirement Mapping

| Design ID | Requirement | 設計內容 |
|---|---|---|
| DES-001 | REQ-MANIFEST-001 | 在 `sdd-quality-gates.yml` 新增 `python scripts/build_kit_manifest.py --check` step |
| DES-002 | NFR-PERF-001, SEC-APP-001, OPS-REL-001 | 延用無網路的 Path 掃描，固定輸出 POSIX 相對路徑，加入 subprocess 回歸測試 |

## Current / Target Architecture

`GitHub checkout → Python dependencies → SDD/Enterprise tests → Manifest check → Portability/compile checks`

## API／Event／Data Contract

CLI contract：`python scripts/build_kit_manifest.py --check`。成功回傳 0；內容漂移回傳 1。`KIT_MANIFEST.json` schema 維持 name、version、file_count、files，不新增欄位。

## Security & Privacy

腳本只遍歷套件目錄並解析本地 JSON，不接受任意程式碼或遠端 URI。CI log 留存檢查結果，無敏感資料輸入。

## Migration & Rollback

部署僅修改 workflow 與測試。若造成非預期阻擋，回復新增的 CI step 即可；Manifest 產生器本身保持可獨立使用。

## Alternatives

| Option | 優點 | 缺點 | 結論 |
|---|---|---|---|
| A：直接在既有 job 加 step | 變更小、沿用既有 Python 環境 | 與其他 Gate 共用 job | 採用 |
| B：建立獨立 workflow | 隔離清楚 | 重複 checkout/setup、維護成本較高 | 不採用 |

## ADR

- N/A：不改變架構或長期技術選型。
