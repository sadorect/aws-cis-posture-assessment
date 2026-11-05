# AWS Misconfiguration Sandbox

Deliberately vulnerable Terraform for exercising security scanners
(Prowler, Checkov, tfsec, ScoutSuite, custom IAM/network auditors, etc.)
against a realistic but low-cost set of findings. **Do not reuse any of
these patterns in production. Do not point this at a shared/production
AWS account.**

## What gets created

| File | Resources |
|---|---|
| `networking.tf` | VPC, IGW, public subnet, wide-open SG, allow-all NACL, open default SG |
| `iam.tf` | Wildcard-admin managed + inline policy, IAM user with static access key, account-trusted role with AdministratorAccess and no MFA condition |
| `storage.tf` | Public-read S3 bucket (BPA disabled, no encryption, no versioning, no logging), unencrypted EBS volume |
| `logging.tf` | Single-region CloudTrail (no log validation, no KMS/CloudWatch), unhardened trail bucket, KMS key with rotation disabled |

## Expected findings by domain

**IAM**
- I1/I2: Managed + inline policy both grant `Action:"*" Resource:"*"` on an IAM user (should be least-privilege, ideally role-based not user-based).
- I3: Static IAM access key with no rotation policy — scanners should flag key age / human user holding programmatic creds.
- I4: No account password policy resource — defaults apply (no enforced length/rotation/MFA).
- I5/I6: IAM role trust policy allows `Principal: "*"` to assume a role carrying `AdministratorAccess`, with no `Condition` (no ExternalId, no source account restriction).

**Networking**
- N1: No VPC Flow Logs — no network visibility/forensics trail.
- N2: Default security group left with open ingress (self) / open egress, instead of being emptied per CIS benchmark.
- N3: Custom SG opens 22, 3389, 3306, 5432, and 0-65535/tcp to `0.0.0.0/0`.
- N4: Network ACL allows all traffic both directions, undermining any SG hardening.
- N5: Public subnet auto-assigns public IPs to anything launched into it.
- N6: Internet Gateway attached with no compensating edge controls.

**Storage**
- S1: S3 Block Public Access fully disabled (all four settings `false`).
- S2: Bucket policy grants anonymous `s3:GetObject`.
- S3: Bucket ACL set to `public-read`.
- S4: No default encryption (SSE-S3/KMS) configured.
- S5: No versioning — no protection against accidental/malicious deletion.
- S6: No access logging configured.
- S7: EBS volume created with `encrypted = false`, no KMS key.

## Usage

```bash
cd aws-misconfig-sandbox
terraform init
terraform plan    # review before applying — creates public-facing resources
terraform apply
```

Run your scanner of choice against the account/region afterward, e.g.:

```bash
prowler aws
checkov -d .          # static analysis against the Terraform itself
```

## Teardown

```bash
terraform destroy
```

`force_destroy = true` is set on the S3 bucket so destroy works even if a
scanner or test writes objects into it via the public write policy.

## Cost / safety notes

- All resources are low-cost (no EC2 instances are launched; the EBS volume
  is unattached and 8 GiB). Expect only trivial S3/EBS storage charges.
- The IAM user's access key and the wide-open SG/bucket are real, live
  credentials and real public exposure for as long as this stack is
  applied — destroy it promptly after the scan/training session.
- Treat `terraform.tfstate` as sensitive: it contains the IAM user's
  secret access key in plaintext.

## Remediation status (Day 8)

The Terraform in this directory now carries the Day 8 fixes. The pre-remediation
code is preserved in `../evidence/terraform-baseline/`.

| Backlog | Change |
|---|---|
| B03 | Wildcard managed and inline policies, the admin IAM user and its access key deleted |
| B04 | Bucket Block Public Access on, public-read policy deleted, ACL private |
| B06 | Account-level S3 Block Public Access added |
| B09 | Internet-open ingress rules removed from `wide_open` security group |
| B13 | Sandbox default security group emptied |
| B16 | Account password policy added (14+ characters, 24-password history) |

Not done this sprint, by the backlog: B05, B10-B15, B17, B18 (see `../docs/day7_remediation_backlog.md`).

## Teardown (Day 10)

The sandbox was destroyed on 2026-11-05 and verified from the read-only scanner
profile (see `../docs/day10_teardown.md`). Two resources in this configuration,
`aws_s3_account_public_access_block.account` and
`aws_iam_account_password_policy.strict`, were removed from Terraform state on
purpose and still exist in the account as real hardening. Do not re-apply this
configuration as-is: it would conflict with them. The pre-remediation code is in
`../evidence/terraform-baseline/`.
