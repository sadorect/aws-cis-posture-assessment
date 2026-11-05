# Hardening Roadmap — Deferred Items

**Account:** 671154999764 · **Source:** open items in `backlog/remediation_backlog.csv` after Day 9
**Principle:** sequenced by risk, not by finding count. Each phase names an owner role and the Prowler check that proves it done.

## Phase 1 — next 30 days (close the detection gap and the remaining P1s)

| Backlog | Action | Owner | Done when |
|---|---|---|---|
| **B10** | Harden CloudTrail (validation, KMS, multi-region), send it to CloudWatch, add the CIS section 4 metric filters and alarms, enable AWS Config and VPC flow logs | DevSecOps Engineer | 21 Prowler rows pass. It is the largest single reduction and the only way an attack in this account would be seen. |
| **B05** | Add an MFA condition to the administrator role's trust policy, or replace `AdministratorAccess` with a scoped policy | Cloud Security Engineer | `iam_aws_attached_policy_no_administrative_privileges` passes |
| **B07** | Remove the scanner identity's console password (CLI only) or enable MFA | Account Owner | `iam_user_mfa_enabled_console_access` passes |
| **B08** | Move `cloudproject`'s policy to a group | Cloud Security Engineer | The direct-attachment row passes |

Decision needed: B10 needs agreement on log retention and who receives alarms.

## Phase 2 — 30 to 90 days (platform hardening)

| Backlog | Action | Owner |
|---|---|---|
| B12 | Enable Security Hub with the CIS standard (consider cost) | Cloud Security Engineer |
| B18 | Enable IAM Access Analyzer, S3 data-event logging and an AWS Support role | GRC Analyst |
| B14, B15 | Encrypt EBS volumes and enable default encryption; enable KMS key rotation | DevSecOps Engineer |
| B17 | Deny HTTP on buckets, enable versioning and MFA delete | Cloud Security Engineer |
| B11 | Restrict the custom network ACL | Cloud Security Engineer |

## Phase 3 — beyond 90 days (sustain it)

- **Prowler in CI** against Terraform changes, so misconfigurations fail the pipeline.
- **Federated access** (IAM Identity Center or SAML) to remove long-lived users, which would make FP-04 applicable.
- **Account structure:** a dedicated sandbox account and an AWS Organization with service control policies.
- **Quarterly retest** against the pinned benchmark, then a planned move to a newer CIS version with a new baseline.

## Measures of success
- Failing checks, counted: 41 now (38 **[pending]**), target below 10 after Phases 1 and 2.
- Critical and high findings: 2 and 7 now (1 and 5 **[pending]**), target zero critical and none open without an owner.
- Every accepted risk has a written reason, a compensating control and a review date.
