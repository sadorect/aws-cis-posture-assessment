# Day 9 — Verification and Improvement Measurement

**Account:** 671154999764, `eu-west-2` · **Benchmark:** `cis_4.0_aws` (pinned, Prowler 5.48.0)
**Identical to baseline:** same flags (`--scan-unused-services`, region), same mutelist, same `scanner` profile. ScoutSuite 5.14.0 with the same wrapper and exceptions file.
**Evidence:** `evidence/verification/` (first run, read the stale credential report) and `evidence/verification-final/` (final run, after the IAM credential report refreshed at 07:42 UTC). SHA-256 in each `SHA256SUMS`. Compared against `evidence/baseline-v2/` (raw) and `evidence/tuning/rescan/` (tuned).
**Backlog:** statuses updated in `backlog/remediation_backlog.csv`.

## Headline result

| Measure | Baseline v2 | Tuned (Day 6) | First verification | **Final verification** |
|---|---|---|---|---|
| **Failing, counted** | 62 | 52 | 41 | **38** |
| Failing, muted | 0 | 10 | 10 | 10 |
| Failing, raw total | 62 | 62 | 51 | **48** |
| PASS | 44 | 44 | 51 | 49 |
| Critical | 3 | 3 | 2 | **1** |
| High | 15 | 12 | 7 | **5** |

**Measured improvement:** 14 fewer counted failures against the tuned baseline (52 to 38, 27%) and 14 fewer raw failures against the original (62 to 48, 23%). No new failures appeared in either run: every finding still failing was already failing in the tuned baseline.

The check count fell from 109 to 100 because deleting the admin user and its policies removed their resource-level rows, including five PASS rows for the deleted user.

## What cleared (14 counted rows, measured)

| Backlog | Prowler check | Result |
|---|---|---|
| B01 | `iam_root_hardware_mfa_enabled` | PASS |
| B01 | `iam_root_mfa_enabled` | PASS (final run) |
| B02 | `iam_user_mfa_enabled_console_access` for `cloud-project-admin` | PASS (final run) |
| B02 | `iam_policy_attached_only_to_group_or_roles` for `cloud-project-admin` | PASS |
| B03 | `iam_customer_attached_policy_no_administrative_privileges` | Resource gone |
| B03 | `iam_policy_attached_only_to_group_or_roles` for the sandbox admin user (2 rows) | Resource gone |
| B04 | `s3_bucket_level_public_access_block` | PASS |
| B06 | `s3_account_level_public_access_blocks` | PASS |
| B08 | `iam_user_mfa_enabled_console_access` for `cloudproject` | PASS (final run) |
| B09 | `ec2_securitygroup_allow_ingress_from_internet_to_all_ports` | PASS |
| B13 | `ec2_securitygroup_default_restrict_traffic` (`sg-0e69…`) | PASS |
| B16 | `iam_password_policy_minimum_length_14`, `iam_password_policy_reuse_24` | PASS (2 rows) |

ScoutSuite (first run) agrees on the security-group and bucket items: all five security-group port rules clear, both public-bucket rules clear, and the wildcard policy rule drops from 2 to 1. Flagged rules fell from 40 to 27, with 17 to 9 at danger level. The per-port ScoutSuite result confirms B09 properly, where Prowler's port-specific checks had passed before the fix. ScoutSuite was not re-run after the credential report refreshed, so its root MFA rules still show the stale result.

## The stale credential report, resolved
The first verification run (41 failing) still showed three MFA rows failing although the devices were registered. Prowler reads the IAM credential report, which AWS caches for four hours. The report was generated at 03:41:55 UTC, before registration, and still listed the deleted admin user.

| Prowler check | First run | Final run | Direct evidence |
|---|---|---|---|
| `iam_root_mfa_enabled` | FAIL | **PASS** | Account summary `AccountMFAEnabled = 1` |
| MFA for `cloud-project-admin` | FAIL | **PASS** | Security key registered |
| MFA for `cloudproject` | FAIL | **PASS** | Security key registered |

The report refreshed at 07:42:03 UTC and showed MFA active for root and both users. The final run read it and cleared all three rows, exactly as the direct evidence predicted. The estimate of 38 given on the first run was confirmed by the measurement.

The five rows that disappeared between the two runs were all PASS rows for the deleted admin user, which the stale report had kept alive. That corroborates the diagnosis.

## By CIS section (raw counts, including muted rows)

| Section | Baseline | Final |
|---|---|---|
| 1 Identity and Access Management | 18 | 8 |
| 2 Storage | 6 | 4 |
| 3 Logging | 9 | 9 |
| 4 Monitoring | 16 | 16 |
| 5 Networking | 14 | 11 |
| **Total** | **63** | **48** |

The baseline total reads 63 here against 62 findings elsewhere because one security-group check maps to two CIS requirements.

## What still fails, and why

| Backlog | Still failing | Status |
|---|---|---|
| B05 | `AdministratorAccess` still attached (critical) | Open. Attached to the sandbox role, and through the `sandbox-builders` group by design until teardown. |
| B07 | `scanner-identity` console user without MFA (high) | Open, P1 |
| B08 | `cloudproject` direct policy attachment (1 row) | Open. The MFA part is verified; the direct attachment was not part of the Day 8 plan. |
| B10 | CloudTrail, CloudWatch, Config, flow logs (21 rows) | Deferred to the hardening roadmap, as the backlog set out |
| B11 | Custom NACL `acl-0f4b…` | Open, P2 |
| B12 | Security Hub | Open, P2 |
| B14, B15 | Unencrypted EBS volume, KMS rotation | Open, P2 |
| B17, B18 | S3 hardening, roadmap items | Open, P2 |

Day 8's expectation of "up to 15 rows" was off by one: the `cloudproject` direct-attachment row was never part of the work done, so it correctly did not clear.

## ScoutSuite items that remain by design
- **Password policy expiry:** `iam-password-policy-no-expiration` and `iam-password-policy-expiration-threshold` still fire. I set no forced expiry on purpose, following NIST guidance. This is a rule disagreement, not a failed fix.
- **Root MFA rules:** flagged in the first-run ScoutSuite result for the stale-report reason above.

## Backlog status after verification

| Outcome | Items |
|---|---|
| **Fixed, verified** | B01, B02, B03, B04, B06, B09, B13, B16 |
| **Partially fixed** | B08 (MFA verified; direct policy attachment open) |
| **Open** | B05, B07, B10, B11, B12, B14, B15, B17, B18 |
| **Muted or accepted** | 10 rows, in `docs/day6_false_positive_register.md` |

## Conclusion
The measurable target was a demonstrable reduction in CIS failures on the same account and benchmark version, through read-only assessment and controlled remediation. All eight Day 8 sprint items are verified fixed, 14 counted failures cleared (27%), critical findings fell from 3 to 1, high from 15 to 5, and no new failures appeared. The remaining reduction is mostly B10, which is the client's roadmap decision.

## Before teardown
1. Decide on the leftover quick wins: B07 (remove the scanner's console password) and the `cloudproject` direct attachment.
2. Take the Terraform precaution below, then destroy the sandbox. The account-level S3 block and the password policy share the sandbox's Terraform state, and must be removed from state first so the destroy does not undo two real fixes.
