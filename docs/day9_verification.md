# Day 9 — Verification and Improvement Measurement

**Account:** 671154999764, `eu-west-2` · **Benchmark:** `cis_4.0_aws` (pinned, Prowler 5.48.0)
**Identical to baseline:** same flags (`--scan-unused-services`, region), same mutelist, same `scanner` profile. ScoutSuite 5.14.0 with the same wrapper and exceptions file.
**Evidence:** `evidence/verification/` (SHA-256 in `SHA256SUMS`). Compared against `evidence/baseline-v2/` (raw) and `evidence/tuning/rescan/` (tuned).
**Backlog:** statuses updated in `backlog/remediation_backlog.csv`.

## Headline result

| Measure | Baseline v2 | Tuned (Day 6) | Verification (measured) | After pending fix* |
|---|---|---|---|---|
| **Failing, counted** | 62 | 52 | **41** | 38 |
| Failing, muted | 0 | 10 | 10 | 10 |
| Failing, raw total | 62 | 62 | 51 | 48 |
| PASS | 44 | 44 | 51 | 51 |
| Critical | 3 | 3 | 2 | 1 |
| High | 15 | 12 | 7 | 5 |

*See "Three rows measured against a stale credential report" below. The last column is an estimate based on direct evidence, not a scanner result. The measured result is 41.

**Measured improvement:** 11 fewer counted failures against the tuned baseline (52 to 41, 21%) and 11 fewer raw failures against the original (62 to 51, 18%). With the pending rows it would be 14 (27% tuned, 23% raw).

The check count fell from 109 to 105 because deleting the admin user and its policies removed their resource-level rows.

No new failures appeared: every finding that is still failing was already failing in the tuned baseline.

## What cleared (11 counted rows, measured)

| Backlog | Prowler check | Result |
|---|---|---|
| B01 | `iam_root_hardware_mfa_enabled` | PASS: "Root account has a hardware MFA device enabled" |
| B02 | `iam_policy_attached_only_to_group_or_roles` for `cloud-project-admin` | PASS: "no inline or attached policies" |
| B03 | `iam_customer_attached_policy_no_administrative_privileges` | Resource gone |
| B03 | `iam_policy_attached_only_to_group_or_roles` for the sandbox admin user (2 rows) | Resource gone |
| B04 | `s3_bucket_level_public_access_block` | PASS |
| B06 | `s3_account_level_public_access_blocks` | PASS |
| B09 | `ec2_securitygroup_allow_ingress_from_internet_to_all_ports` | PASS |
| B13 | `ec2_securitygroup_default_restrict_traffic` (`sg-0e69…`) | PASS |
| B16 | `iam_password_policy_minimum_length_14`, `iam_password_policy_reuse_24` | PASS (2 rows) |

ScoutSuite agrees: all five security-group port rules (SSH, RDP, MySQL, PostgreSQL, all-ports) clear, both public-bucket rules clear, and the wildcard policy rule drops from 2 to 1. Flagged rules fell from 40 to 27, with 17 to 9 at danger level. The per-port ScoutSuite result confirms B09 properly, where Prowler's port-specific checks had passed before the fix.

## Three rows measured against a stale credential report
Three rows still fail, though the underlying fix is in place:

| Prowler check | Reported | Direct evidence |
|---|---|---|
| `iam_root_mfa_enabled` | "MFA is not enabled for root" | `AccountMFAEnabled = 1`. Prowler's own hardware check passes in the same run. |
| `iam_user_mfa_enabled_console_access` for `cloud-project-admin` | MFA disabled | A U2F key is registered for the user. |
| `iam_user_mfa_enabled_console_access` for `cloudproject` | MFA disabled | A U2F key is registered for the user. |

**Cause:** the IAM credential report these checks read was generated at 03:41 UTC, before the MFA devices were registered. AWS reuses a report for four hours. It still lists the deleted `misconfig-sandbox-admin-user`, which confirms it is stale. ScoutSuite reads the same report for root, and flags root MFA for the same reason.

**What I have not done:** I have not counted these rows as cleared. The measured figure is 41. The 38 figure rests on the direct API evidence above. The credential report refreshes after about 07:41 UTC, at which point the same command should show them passing. **Re-run before the final report, and replace this table with the measured result.**

## What still fails, and why

| Backlog | Still failing | Status |
|---|---|---|
| B05 | `AdministratorAccess` still attached (critical) | Open. Attached to the sandbox role. It now also appears through the `sandbox-builders` group, by design until teardown. |
| B07 | `scanner-identity` console user without MFA (high) | Open, P1 |
| B08 | `cloudproject` direct policy attachment (1 row) | Open. The MFA part is applied; the direct attachment was not part of the Day 8 plan. |
| B10 | CloudTrail, CloudWatch, Config, flow logs (21 rows) | Deferred to the hardening roadmap, as the backlog set out |
| B11 | Custom NACL `acl-0f4b…` | Open, P2 |
| B12 | Security Hub | Open, P2 |
| B14, B15 | Unencrypted EBS volume, KMS rotation | Open, P2 |
| B17, B18 | S3 hardening, roadmap items | Open, P2 |

Day 8's expectation of "up to 15 rows" was off for one row: the `cloudproject` direct-attachment row was never part of the work done, so it correctly did not clear.

## ScoutSuite items that remain by design
- **Password policy expiry:** `iam-password-policy-no-expiration` and `iam-password-policy-expiration-threshold` still fire. I set no forced expiry on purpose, following NIST guidance. This is a rule disagreement, not a failed fix.
- **Root MFA:** the two root rules, for the stale-report reason above.

## Backlog status after verification

| Outcome | Items |
|---|---|
| **Fixed, verified** | B03, B04, B06, B09, B13, B16 |
| **Applied, pending credential-report refresh** | B01, B02, B08 (MFA part) |
| **Open** | B05, B07, B10, B11, B12, B14, B15, B17, B18 |
| **Muted or accepted** | 10 rows, in `docs/day6_false_positive_register.md` |

## Conclusion
The measurable target was a demonstrable reduction in CIS failures on the same account and benchmark version, through read-only assessment and controlled remediation. Six of the eight Day 8 sprint items (B01, B02, B03, B04, B06, B09, B13, B16) are verified fixed, the other two (B01, B02) are applied and waiting on a credential-report refresh, and no new failures appeared. The remaining reduction is mostly B10, which is the client's roadmap decision.

## Before Day 10
1. After 07:41 UTC, re-run the identical Prowler scan, confirm the three MFA rows pass, and update this report.
2. Decide on the leftover quick wins before teardown: B07 (remove the scanner's console password) and the `cloudproject` direct attachment.
