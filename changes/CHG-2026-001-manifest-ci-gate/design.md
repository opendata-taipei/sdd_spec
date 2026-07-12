# CHG-2026-001 Technical Design

## Design Summary

在既有 `validate-sdd` job 中直接執行 Manifest 產生器的 `--check` 模式。檢查只比較記憶體中的預期資料與現有 JSON，不寫入檔案；失敗訊息指向相同腳本的重建模式。

Manifest 產生器以 repo root 為唯一掃描邊界，將排除規則分成 top-level directories、root files、runtime prefixes 與 runtime files 四類常數。受管路徑轉為 POSIX relative path，並以 `(path.casefold(), path)` 排序，確保大小寫相同鍵值仍有確定的 tie-breaker。

## Requirement Mapping

| Design ID | Requirement | 設計內容 |
|---|---|---|
| DES-001 | REQ-MANIFEST-001 | 在 `sdd-quality-gates.yml` 新增 `python scripts/build_kit_manifest.py --check` step |
| DES-002 | NFR-PERF-001, SEC-APP-001, OPS-REL-001 | 延用無網路的 Path 掃描，明確排除非發布與 Runtime 路徑，固定輸出 POSIX 相對路徑與穩定排序，加入 subprocess 回歸測試 |
| DES-003 | REQ-IDENTITY-PRIVACY-001 | 公開 role map 僅保留 placeholder；真實 mapping 由私有部署 Repository、受保護設定或企業 IAM 注入 |

## Invariants and Failure Modes

- `--check` 模式不得呼叫 `write_text` 或修改任何受管檔案。
- Manifest JSON 無法解析、缺少欄位或內容不一致時一律 fail closed，回傳非 0。
- 排除規則只適用於明確列出的非發布內容；未知的新檔案預設納入管理。
- Runtime／Eval／Test reports 可被忽略，但 `reports/README.md` 與正式 context evidence 仍屬受管檔案。
- CI 必須從 repository root 執行，避免工作目錄改變掃描邊界。
- 公開身分檢查只掃描部署範本與治理文件；測試 fixture 中的虛構 secret pattern 不得被誤判為真實憑證。

## Current / Target Architecture

`GitHub checkout → Python dependencies → SDD/Enterprise tests → Eval/Runtime Audit → Manifest check → Portability/compile checks`

## API／Event／Data Contract

CLI contract：`python scripts/build_kit_manifest.py --check`。成功回傳 0；無法解析或內容漂移回傳非 0。`KIT_MANIFEST.json` schema 維持 name、version、file_count、files，不新增欄位。重建模式是唯一允許寫入 Manifest 的模式。

## Security & Privacy

腳本只遍歷套件目錄並解析本地 JSON，不接受任意程式碼或遠端 URI。CI log 留存檢查結果，無敏感資料輸入。公開範本不得保存真實 GitHub login、Email、Token 或完整 OIDC claims；正式環境只保存授權判定所需的縮減 claims 與 commit SHA。

## Migration & Rollback

部署僅修改 workflow 與測試。若造成非預期阻擋，回復新增的 CI step 即可；Manifest 產生器本身保持可獨立使用。

## Alternatives

| Option | 優點 | 缺點 | 結論 |
|---|---|---|---|
| A：直接在既有 job 加 step | 變更小、沿用既有 Python 環境 | 與其他 Gate 共用 job | 採用 |
| B：建立獨立 workflow | 隔離清楚 | 重複 checkout/setup、維護成本較高 | 不採用 |
| C：依賴 Git tracked files 產生清單 | 自動排除未追蹤 runtime files | 發布壓縮檔可能沒有 `.git`，降低工具可攜性 | 不採用 |

## ADR

- N/A：不改變架構或長期技術選型。
