# CHG-2026-003 TASK-010 Synthetic Sandbox Implementation Report

- Status：Implemented locally — external host／App verification pending
- Date：2026-07-17
- Requirements：REQ-DEVICE-AUTH-001、OPS-POLL-AUTHZ-005、SEC-CONTROLLER-CUSTODY-004
- Design／ADR：Design Addendum 005、ADR-003
- Authorization：TASK-010 synthetic sandbox only
- Mode B：Fail Closed

## Implemented Scope

- 新增provider-neutral device authorization primitives；只接受fresh numeric GitHub user ID，不接受login、Email、device code或token。
- 定義獨立`merge-authorization/v1`營運角色namespace；`change_manager`不擴增`enterprise-policy.allowed_roles`，並與App Operator、Secret Custodian、Security Reviewer fail-closed分離。
- 對PR author與Approval actor執行numeric／repository-pseudonym separation。
- device session採private atomic single-use claim；重用一律拒絕。
- 新增attestation v2，綁定request、device session、identity decision、controller artifact、configuration、App及installation scope digest。
- 寫public success前重新驗證head、base、policy、installation與controller context；public output維持v1 allowlist。
- public policy明定webhook-inactive polling bounds、private mapping boundary及不保存refresh token。

## Explicitly Not Implemented／Not Authorized

- 未建立或安裝GitHub App，未產生／下載App private key，未執行真實device OAuth。
- 未在目前interactive workstation存放private mapping、pepper、token或credential。
- 未提供dedicated managed host、secret store、service account、private audit或custody Evidence。
- 未啟用public ruleset、production Mode B、formal Approval merge或TASK-005。
- 未執行TASK-011 independent validation或sign-off。

## Security Status

SEC-F-013、016～022保持Open。local tests只證明synthetic contract failure paths，不關閉controller／App compromise、device phishing、host custody或platform enforcement findings。

## Local Verification

- `python -m unittest discover -s tests -v`：64 tests passed（含8個TASK-010 synthetic regressions）。
- SDD／Enterprise validation：0 errors、0 warnings。
- eval baseline：4 cases；agent evals：4／4 passed。
- runtime audit：20 runs、0 errors。
- Kit Manifest：288 files，唯讀`--check`通過。
- portability、compileall與CHG-2026-003 drift check：通過，0 unspeced drift。
- Starter Kit build／safe verify／governance round trip：通過；final archive digest由handoff另行回報，避免把package自身hash寫回package造成循環。
- Pull Request [#3](https://github.com/opendata-taipei/sdd_spec/pull/3) 的 Quality Gates run [29762382847](https://github.com/opendata-taipei/sdd_spec/actions/runs/29762382847) 綁定commit `fb27bcbb0dc25ebe1b4c6c8272e58f7f347369fe`；validate、Windows／Linux package round trip及checksum comparison均success。

## Rollback

移除Addendum 005新增的provider-neutral module、v2 schema、tests與public placeholder policy欄位即可回到TASK-008 blocked baseline。沒有外部App、credential、ruleset或production side effect需要撤銷；Mode B在前後都維持fail closed。

## Handoff

下一個合法工作是由dedicated host owner／Secret Custodian提供private deployment前置條件，再完成TASK-010 external sandbox部分。完成後才能由不同人員執行TASK-011；任何production activation或formal Approval merge都需新的Human Decision。
