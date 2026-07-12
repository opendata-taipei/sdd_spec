# SDD-TPL-010 Release & Rollback Plan／上線與回滾計畫

- Release ID／Version：
- Change IDs：
- Artifact／Digest：
- Window／Timezone：
- Release Owner／Rollback Decision Owner：

## Scope／Strategy
- Included／Excluded：
- Affected Services／Customers：
- Rolling／Canary／Blue-Green／Feature Flag：
- Migration Mode：

## Pre-Release
- Approved Specs／Tests／Scans
- Signed Artifact／SBOM
- Backup／Restore Verified
- Dashboards／Alerts／On-call
- Rollback Script／Permission／Decision Owner
- Communication Ready

## Deployment Runbook
| Step | Time | Action／Command | Owner | Success Criteria | Failure Action／Evidence |
|---|---|---|---|---|---|
| 0 | | | | | |

## Validation
- Health／Smoke／Data／Security／SLO／Business KPI：

## Rollback Triggers
| Trigger ID | Metric／Event | Threshold／Window | Action | Decision Owner |
|---|---|---|---|---|
| RB-001 | | | | |

## Rollback Runbook
1. 停止推進、保存證據、啟動事件流程。
2. 關閉 Feature／切回流量／部署舊版本。
3. 回復資料或執行核准的 Forward Fix。
4. 驗證服務、資料、安全與客戶影響。
5. 通知、監控、建立後續 Task 與 PIR。

## AI Control
AI 不得自主 Go／No-Go、接受風險、修改回滾門檻、存取未核准 Secret 或執行不可逆生產操作。
