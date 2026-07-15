# SEC-F-008 Kit Runtime Exclusion Remediation

- Change：CHG-2026-003
- Feature：FEAT-002
- Requirements：SEC-PRIVACY-002、OPS-REL-003
- Design：Design Addendum 003
- Task：TASK-007
- Test：TEST-KIT-PRIVACY-001
- Produced：2026-07-15T05:02:39Z
- Result：local pass；cross-platform CI pending

## Finding Reproduction

Mode A negative-run raw logs 位於 Git-ignored top-level `tmp/` 時，修正前 `scripts/build_kit_manifest.py` 會將 10 個 runtime files 加入 `KIT_MANIFEST.json`，造成 `python scripts/build_kit_manifest.py --check` fail closed。未將含 `tmp/` entries 的 Manifest 保留或用於發布。

## Implemented Control

- `scripts/build_kit_manifest.py` 的 exact `IGNORED_TOP_LEVEL` 加入 `tmp`。
- `tests/test_kit_manifest.py` 新增 nested raw-log fixture，驗證 build 與 read-only `--check` 都排除所有 `tmp/` descendants。
- 原 unmanaged public file failure-path test 保持通過；控制沒有放寬其他 repository paths。
- Raw logs 未移動、未刪除、未加入 Git；`git status --ignored` 將其識別為 `!! tmp/`。

## Verification

| Check | Result |
|---|---|
| Targeted Kit Manifest tests | 9/9 pass |
| Full unittest discovery | 43 tests pass |
| `validate_sdd.py` | 0 errors、0 warnings |
| `validate_enterprise.py` | 0 errors、0 warnings |
| Evals／Agent evals | 4 cases pass／4 of 4 pass |
| Runtime audit | 14 runs、0 errors |
| Portability／compileall／drift | pass／pass／PASS，0 unspeced drift |
| Manifest with raw logs present | valid，262 files；0 `tmp/` entry |
| Local package build／safe verify with governance | pass；262 entries、0 `tmp/` entry |
| Verified ZIP SHA-256 | `291c920794197446be212c4e7f0aea58260032d27623b7895e4bdaf78cdb4a46` |
| Verified uncompressed size | 449,340 bytes |

Package runtime output僅位於 ignored `dist/sec-f-008-build` 與 `dist/sec-f-008-verified`，不納入 Repository Evidence 或 Kit。

## Security Disposition

SEC-F-008 required control 已實作並由 regression、current-workspace Manifest 與 local package round-trip 驗證。依 package contract，必須再觀察 GitHub Actions Windows／Linux package jobs 與 checksum comparison 成功，才可將 finding 記為完整 remediation。此 disposition 不接受新的 residual risk，也不改變 SEC-F-006／007 或 Addendum 002 的 Mode B fail-closed boundary。

## Rollback and Remaining Work

- Rollback／forward-fix 依 Addendum 003；不得把 `tmp/` 加回公開 allowlist。
- Cross-platform Quality Gates 與 checksum comparison 尚待目前 branch push 後執行／觀察。
- TEST-WORKFLOW-002 cancellation run 與其 cleanup／privacy Evidence 仍待執行。
- 正式 Approval merge、state transition、G5 submission 與 Release readiness仍未授權。
