# Day 8 — Remediation Change Log

**Account:** 671154999764, `eu-west-2` · **Applied with:** Terraform, `projectadmin` profile (`cloud-project-admin`, via the `sandbox-builders` group)
**Result:** `Apply complete! Resources: 2 added, 4 changed, 6 destroyed.` Terraform then reported no drift against the live account.
**Before-state:** `evidence/terraform-baseline/` (code) and the before-values below, captured from the live account immediately before the apply.
**Not yet verified by scanner:** the Prowler and ScoutSuite re-run is Day 9. Items stay **Applied** in the backlog until their check passes.

## Changes

| # | Backlog | Change | Before | After | Applied by |
|---|---|---|---|---|---|
| 1 | B01 | MFA on the root account | No root MFA | Root MFA enabled (account summary), non-virtual device | Account Owner (console) |
| 2 | B02 | MFA on `cloud-project-admin`; `AdministratorAccess` moved off the user | No MFA, policy attached directly | U2F key registered. Policy now comes through the `sandbox-builders` group | Account Owner (console) |
| 3 | B08 | MFA on `cloudproject` (not in the Day 8 plan) | No MFA | U2F key registered | Account Owner (console) |
| 4 | B06 | Account-level S3 Block Public Access | Not configured | All four settings on | Terraform |
| 5 | B04 | Sandbox bucket Block Public Access | All four off | All four on | Terraform |
| 6 | B04 | Bucket policy | Anonymous `GetObject` for `*` | Deleted | Terraform |
| 7 | B04 | Bucket ACL | `public-read` (AllUsers grant) | `private` (no AllUsers grant) | Terraform |
| 8 | B09 | Security group `sg-021c7366dcb131981` | 5 ingress rules open to `0.0.0.0/0` | 0 ingress rules | Terraform |
| 9 | B13 | Default security group `sg-0e69af95c695f533e` | 1 ingress, 1 egress rule | 0 and 0 | Terraform |
| 10 | B03 | `misconfig-sandbox-admin-user` | User with active access key, `*:*` managed policy and `*:*` inline policy | User, key, both policies and the attachment deleted | Terraform |
| 11 | B16 | Account password policy | None | 14+ characters, 24-password history, all character classes, no forced expiry | Terraform |

## Independent verification (not scanner-based)
- **Anonymous bucket access:** an unauthenticated list and an unauthenticated GET both return HTTP 403.
- **Live state:** every "after" value in the table was read back from the account after the apply.
- **Terraform drift:** `terraform plan` shows no differences, so the code and the account agree.

## Deviations and lessons
- **Terraform ignores omitted rule blocks.** The first version of the security-group edits removed the `ingress` and `egress` blocks. The plan showed no change for either group, and the state confirmed the rules would have stayed open. Both resources need an explicit `ingress = []` and `egress = []`. The fix was caught at the plan stage, before any apply.
- **The build identity lost all access mid-sprint.** Removing `AdministratorAccess` from `cloud-project-admin` left it with no permissions and blocked the apply. A group carrying the policy restored it. This is the designed state for the build identity: elevated only through a group that can be removed on Day 10.
- **B03 chose deletion over scoping.** The user had no consumer, so deleting it removes the finding and the credential at once. The access key's secret no longer exists in Terraform state going forward.
- **B16 left expiry off** on purpose, following NIST SP 800-63B. ScoutSuite's "password expiration disabled" rule will still flag it, so Day 9 should record that as a rule disagreement and not a failed fix.

## Expected Day 9 outcome
These should clear in the identical Prowler re-run (`cis_4.0_aws`, `--scan-unused-services`, region `eu-west-2`, mutelist):

| Item | Prowler check |
|---|---|
| B01 | `iam_root_mfa_enabled` (and `iam_root_hardware_mfa_enabled` if the device is a hardware key) |
| B02, B08 | `iam_user_mfa_enabled_console_access` for the two users, plus their direct-attachment rows |
| B03 | `iam_customer_attached_policy_no_administrative_privileges` and two direct-attachment rows |
| B04 | `s3_bucket_level_public_access_block` |
| B06 | `s3_account_level_public_access_blocks` |
| B09 | `ec2_securitygroup_allow_ingress_from_internet_to_all_ports` |
| B13 | `ec2_securitygroup_default_restrict_traffic` for `sg-0e69…` |
| B16 | `iam_password_policy_minimum_length_14`, `iam_password_policy_reuse_24` |

That is up to 15 rows, which would take the counted failures from 52 to about 37. Still open: B07 (scanner MFA), B05, B10–B12, B14, B15, B17 and B18. The `AdministratorAccess` policy row (B05) may change because the user no longer holds it directly.

## Follow-ups
- **Day 10 teardown:** remove `cloud-project-admin` from `sandbox-builders` or delete the group once the sandbox is destroyed.
- **B10** is deferred to the hardening roadmap, as the backlog sets out.
