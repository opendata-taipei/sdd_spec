# CHG-2026-003 Design Addendum 003：Private Runtime Kit Exclusion

- Status：Accepted
- Date：2026-07-15
- Risk Level：L2
- Affected Design：DES-WORKFLOW-001、Starter Kit package allowlist
- Requirements：SEC-PRIVACY-002、OPS-REL-003
- Task：TASK-007
- Test：TEST-KIT-PRIVACY-001
- Finding：SEC-F-008

## Context

Mode A negative run `29388919217` 的 raw logs 依 Addendum 002 放在 ignored top-level `tmp/` 做離線 privacy scan。驗證發現 `.gitignore` 雖排除 `/tmp/`，`scripts/build_kit_manifest.py` 的 filesystem allowlist discovery 並不讀取 `.gitignore`，也未在 `IGNORED_TOP_LEVEL` 明確排除 `tmp`。當 raw logs 實際存在時，builder 會把它們加入公開 `KIT_MANIFEST.json`，違反 SEC-PRIVACY-002 與 Mode A runtime boundary。

## Design Decision

`scripts/build_kit_manifest.py` SHALL 將 exact top-level component `tmp` 加入 `IGNORED_TOP_LEVEL`。此控制：

- 適用 `tmp/` 下所有深度的檔案，包含 aggregate log、step logs、下載 artifact 與其他 runtime verification data。
- 只比對 repository-relative path 的第一個 component；不得以 substring 或 glob 排除 `attempt/`、`templates/` 等合法路徑。
- 不依賴 `.gitignore` parser、Git executable 或外部 dependency，維持 Python 3.12+ standard-library 與 deterministic package contract。
- 不改變 `KIT_MANIFEST.json` 作為唯一發布 allowlist、sorting、`--check` read-only 或 unmanaged public file fail-closed 行為。

`.gitignore` 仍保留 `/tmp/`，作為 Git staging boundary；builder exclusion 是獨立的 packaging defense in depth，兩者不得互相取代。

## Verification Contract

新增 `TEST-KIT-PRIVACY-001` regression coverage：

1. fixture 建立 `tmp/raw-job.log` 與 nested `tmp/create-approval/system.txt`。
2. manifest build 成功，兩個 runtime paths 均不在 `files`，且 `file_count` 一致。
3. `--check` 成功並保持 `KIT_MANIFEST.json` bytes 不變。
4. 原有 unmanaged public file test 持續 fail closed，證明 exclusion 未放寬至其他 top-level files。

完成後以目前含 raw logs 的 workspace 重建 `KIT_MANIFEST.json`，預期 0 個 `tmp/` entry，並執行完整 AGENTS.md baseline、package round-trip 與 CHG-2026-003 drift check。

## Impact Analysis

- Code：`scripts/build_kit_manifest.py`
- Tests：`tests/test_kit_manifest.py`
- Governance：Change manifest、Task、Test Plan、Kit Manifest、remediation Evidence
- Public contract：Kit entry set移除 private runtime files；無 schema 或 CLI breaking change
- ADR：不需要；本修正落實既有 allowlist／privacy boundary，沒有建立新的跨 Change architecture decision

## Migration and Rollback

- Migration：更新 builder 後重建 `KIT_MANIFEST.json`；既有 `tmp/` 內容不移動、不刪除、不讀入 Kit。
- Rollback：若 exclusion 造成非預期 entry-set regression，停止 package／release，回復 builder change 並只在已確認無 private runtime files 的 clean workspace 重建；不得以把 `tmp/` 加回公開 Manifest 作為 rollback。
- Forward-fix：修正 exact top-level classification 或補充 regression fixture，再重新 build／safe verify。

## Residual Risks

- 其他未命名 runtime directory 仍可能被 filesystem discovery 納入；維持 unmanaged-file fail-closed、Kit diff review 與 package privacy scan。
- 本 Addendum 不處理 branch protection／CODEOWNERS（SEC-F-006／007），不解除 Mode B fail-closed，也不授權 Approval merge 或 state transition。

## Human Decision

2026-07-15 Human Decision 已核准 Addendum 003：

- 修正 Kit builder 排除 top-level `tmp/`。
- 加入 regression test。
- 執行 SEC-F-008 remediation。

此決策是 bounded security remediation，不是 Gate approval、Release approval、Security Exception 或 residual risk acceptance。
