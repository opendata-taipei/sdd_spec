# CHG-2026-003 TASK-010 Synthetic CI Run 29762382847

- Change：CHG-2026-003
- Task：TASK-010 synthetic contract only
- Commit：`fb27bcbb0dc25ebe1b4c6c8272e58f7f347369fe`
- Pull Request：[#3](https://github.com/opendata-taipei/sdd_spec/pull/3)
- Workflow：[SDD Quality Gates run 29762382847](https://github.com/opendata-taipei/sdd_spec/actions/runs/29762382847)
- Event：pull_request
- Started：2026-07-20T17:06:21Z
- Completed：2026-07-20T17:07:21Z
- Conclusion：success

## Job Results

| Job | Result |
|---|---|
| validate-sdd | success |
| package-round-trip (ubuntu-latest) | success |
| package-round-trip (windows-latest) | success |
| compare-package-checksums | success |

## Artifact Metadata

| Artifact | GitHub artifact digest | Size |
|---|---|---:|
| starter-kit-Windows | `sha256:189f46d1ad838431b65ca185284efe95b8784ebedc5626461784d5a193299633` | 209159 bytes |
| starter-kit-Linux | `sha256:ef6dea5e389523a30cf221c4a5e2c3d0e421584091b642810eb1ec3218a4d4d4` | 209159 bytes |
| agent-runtime-audit-29762382847 | `sha256:1be8efad4a296bbfc79d6f8dddb38b0d832db7cb8ee09490050b272a37ccde2a` | 3002 bytes |

GitHub artifact digest是各artifact wrapper的完整性資訊，不等同Starter Kit ZIP內部hash。`compare-package-checksums` success是本run對Windows／Linux archive sidecar hash一致性的權威訊號。

## Security Boundary

本Evidence只證明TASK-010 provider-neutral synthetic contract及跨平台package baseline。它不證明真實GitHub App、device OAuth、dedicated managed host、private role mapping、credential custody、ruleset source pinning或TASK-011 independent verification。SEC-F-013、016～022保持Open，Mode B保持fail closed。
