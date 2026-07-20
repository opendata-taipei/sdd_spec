# CHG-2026-003 Design Addendum 005 Decision Packet

- Status：Accepted — 2026-07-17 Human Decision recorded
- Date：2026-07-17
- Mode B：Fail Closed

## Recommended Decision

接受Requirement Addendum 002、Design Addendum 005、ADR-003與Security Review Addendum 005 controls，只授權TASK-010 synthetic sandbox；採webhook-inactive GitHub App、private managed poller及per-decision device flow。TASK-011須獨立驗證，production Mode B、formal Approval merge、TASK-005與SEC-F-013／017 residual risk均不在授權範圍。

## Required Private Preconditions

- 指定dedicated managed host與private service account；一般interactive developer workstation不合格。
- 指定Security Owner／Secret Custodian、App Operator、Change Manager authorizer及independent Security Reviewer，角色不得重疊於policy禁止組合。
- host有OS／hardware-backed secret store、encrypted storage、patching、audit、rotation與revocation能力。
- App installation只含sandbox public repository；private repository保持empty／quarantined。

## Alternatives

- 若無法提供上述host與separation：停止Addendum 005，改採GitHub Team／Enterprise plan升級。
- 不接受unprotected private workflow、public reviewers、manual same-name status或public IAM mapping。

## Human Decision

> 核准CHG-2026-003 Requirement Addendum 002、Design Addendum 005、ADR-003與Security Review Addendum 005 required controls；只授權TASK-010 synthetic sandbox，以webhook-inactive GitHub App、private managed poller及per-decision device flow驗證privacy-preserving Human authorization。不授權production Mode B、formal Approval merge、TASK-005或TASK-011 sign-off；SEC-F-013、016～022維持Open，Mode B維持fail closed。

本決策已由Human於2026-07-17在對話中明確作成；它是TASK-010工作授權，不是正式Gate Approval、Risk Acceptance或SEC finding closure。
