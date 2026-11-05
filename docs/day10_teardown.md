# Day 10 — Sandbox Teardown Record

**Account:** 671154999764, `eu-west-2` · **Run with:** Terraform, `projectadmin` profile (`cloud-project-admin`, via the `sandbox-builders` group)
**Result:** `Apply complete! Resources: 0 added, 0 changed, 20 destroyed.` Verified afterwards from the read-only `scanner` profile.

## Sequence
1. **Precaution:** the S3 account-level Block Public Access and the account password policy shared the sandbox's Terraform state. Both were removed from state (`terraform state rm`, a local edit with no AWS calls) so the destroy could not undo two real fixes.
2. **Blocked once:** the first attempt failed because the build group's `AdministratorAccess` had been removed before the destroy. A destroy needs the same admin rights as the build. Nothing was changed in AWS. The policy was re-attached for the teardown window.
3. **Plan reviewed:** `terraform plan -destroy` listed exactly 20 resources to destroy and neither account-level resource.
4. **Destroy applied:** all 20 destroyed.
5. **Verified from the scanner profile** (below).

## Verification (read-only, from the scanner profile)

| Check | Expected | Result |
|---|---|---|
| Sandbox VPC | Only the default VPC remains | Default VPC only |
| Security groups named `misconfig-*` | None | 0 |
| EBS volume `vol-03482f81499ede4f1` | Not found | `InvalidVolume.NotFound` |
| `misconfig-*` S3 buckets | None | 0 |
| CloudTrail trails | None | 0 |
| Non-service IAM roles | None | None |
| KMS key | Scheduled for deletion | `PendingDeletion`, deletes 2026-12-05 |
| Account S3 Block Public Access | Still on (kept) | All four settings on |
| Password policy | Still set (kept) | Minimum length 14, reuse prevention 24 |
| IAM users | Real identities only | `cloud-project-admin`, `cloudproject`, `scanner-identity` |

## Deliberately kept
Two fixes were real changes to the real account, not sandbox resources, and remain in place: the account-level S3 Block Public Access (B06) and the password policy (B16). They are no longer managed by this Terraform state.

## Follow-ups
- **Remove the elevated access:** `sandbox-builders` still carries `AdministratorAccess`. Remove the policy from the group, or remove `cloud-project-admin` from it, now that the build is finished. This is an IAM change in your account, so it is yours to make.
- **KMS key:** it stays in "pending deletion" until 2026-12-05. That is expected and costs almost nothing.
- **Terraform config:** `aws-misconfig-sandbox/` still declares the two kept resources. The state no longer tracks them, so applying that config would conflict with what already exists. Do not re-apply it as-is. The pre-remediation code is preserved in `evidence/terraform-baseline/` and in git history.
- **Open items:** B05, B07, B08 (direct attachment), B10 to B12, B14, B15, B17 and B18 stay on the hardening roadmap.
