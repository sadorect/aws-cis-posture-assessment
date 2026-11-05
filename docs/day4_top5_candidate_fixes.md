# Day 4 — Top-Five Candidate Fixes

**Engagement:** Cloud Security Posture Assessment and CIS Benchmark Remediation on AWS (VaultBridge Financial, simulated)
**Account:** 671154999764, `eu-west-2` · **Benchmark:** CIS AWS Foundations v4.0 (`cis_4.0_aws`, pinned)
**Evidence:** `evidence/baseline-v2/` (Prowler 5.48.0, 62 failing of 109), `evidence/scoutsuite/` (ScoutSuite 5.14.0, 17 danger / 23 warning)
**Mappings:** aligned to the Day 7 backlog (ISO 27001:2022, NIST CSF 2.0).
**Status:** DRAFT shortlist. Candidates only. Final priority bands (P0–P2) are set on Day 5.

Ranked by real-world risk (exposure, exploitability, blast radius, data sensitivity), not by scanner severity or finding count. "Findings cleared" is the number of failing rows in the v2 baseline CSV that the fix should clear.

| # | Candidate fix | Findings cleared | Sandbox or account? | Corroborated by |
|---|---|---|---|---|
| 1 | Enable MFA on the root account | 2 (critical) | Account | Prowler + ScoutSuite |
| 2 | Enable S3 Block Public Access and remove the public policy and ACL | 3 of 6 S3 rows | Sandbox + account | Prowler + ScoutSuite |
| 3 | Close the internet-open security-group rules | 1 of 3 SG rows (+ rule-level findings) | Sandbox | ScoutSuite (Prowler partial) |
| 4 | Remove wildcard IAM policies and the standing admin access key | 2 (+ user and role findings) | Sandbox | Prowler + ScoutSuite |
| 5 | Harden CloudTrail and wire it to CloudWatch | up to 23 | Sandbox + account | Prowler + ScoutSuite |

## 1. Enable MFA on the root account
- **Why:** Root has no MFA and no hardware MFA (both critical). A compromised root bypasses every other control, so the blast radius is the whole account.
- **Exploitability:** Needs only a stolen or phished root password, which is a common attack path.
- **Fix:** Enable MFA, hardware key preferred, on root. Add MFA for the three console users (`cloudproject`, `cloud-project-admin`, `scanner-identity`), which are separate high findings.
- **Effort:** Low. Manual console action by the account owner, so it can't be scripted or done by the analyst.
- **Note:** This is a real account control, not a planted sandbox finding. Triage should record it as account-level.
- **Mapping:** CIS 1.5, 1.6 · CIS Controls v8 5.4, 6.5 · NIST CSF 2.0 PR.AA-03 · ISO 27001:2022 A.5.15, A.5.17, A.8.5

## 2. Enable S3 Block Public Access and remove the public policy and ACL
- **Why:** The bucket `misconfig-sandbox-public-data-*` allows anonymous `GetObject` and is public-read and world-listable. Account-level Block Public Access is also absent. The brief names public data exposure as the top fintech risk.
- **Exploitability:** Trivial. Anyone on the internet can read and list objects with no credentials.
- **Fix:** Turn on all four Block Public Access settings at account and bucket level, delete the `PublicRead` bucket policy, and reset the ACL to private. Follow up with default encryption, versioning, logging and a TLS-only policy.
- **Effort:** Low. A single Terraform change.
- **Note:** The bucket holds no real data and is write-protected, since `PutObject` was removed.
- **Mapping:** CIS 2.1.4 · CIS Controls v8 3.3 · NIST CSF 2.0 PR.DS-01 · ISO 27001:2022 A.8.3

## 3. Close the internet-open security-group rules
- **Why:** `sg-021c7366dcb131981` allows `0.0.0.0/0` on SSH, RDP, MySQL, PostgreSQL and all TCP ports. The default security groups also keep open rules.
- **Exploitability:** High if attached to an instance. Today the group is unattached, so real exposure is low. It is still a CIS-named problem area and the Day 5 worked example.
- **Fix:** Remove the world-open rules, or restrict them to an admin CIDR. Empty the default security groups' rules.
- **Effort:** Low.
- **Tool gap:** ScoutSuite flags SSH, RDP and the database ports for this group. Prowler passed its port-specific checks and caught only the all-ports rule, so the per-port rules should be scored as real findings. The Day 9 comparison should check each rule, not just the check ID.
- **Mapping:** CIS 5.3, 5.4, 5.5 · CIS Controls v8 4.4, 12.2 · NIST CSF 2.0 PR.IR-01 · ISO 27001:2022 A.8.20–A.8.22

## 4. Remove wildcard IAM policies and the standing admin access key
- **Why:** The sandbox has a `*:*` managed policy and an inline `*:*` policy on an IAM user with a long-lived access key. It also has an `AdministratorAccess` role trusted by the whole account with no MFA or external-ID condition. This is the largest blast radius among the sandbox IAM findings.
- **Exploitability:** Requires one leaked key or one compromised principal in the account. Access keys leak through code and logs, which makes this a leading cause of cloud breaches.
- **Fix:**
  - Delete the access key.
  - Replace the wildcard policies with scoped, least-privilege ones.
  - Attach policies to roles or groups, not users.
  - Add an MFA condition to the role trust policy.
- **Effort:** Medium. It needs a defined target permission set.
- **Mapping:** CIS 1.15, 1.16 · CIS Controls v8 5.4, 6.8 · NIST CSF 2.0 PR.AA-05 · ISO 27001:2022 A.5.15, A.5.18, A.8.2

## 5. Harden CloudTrail and wire it to CloudWatch
- **Why:** The trail is single-region, has no log validation or KMS encryption, and sends nothing to CloudWatch. Roughly 15 of the monitoring failures (CIS section 4) come from that one missing integration. Without it nothing else is detected.
- **Exploitability:** Not directly exploitable. It governs whether an attack is seen, which is why it ranks below the exposure fixes.
- **Fix:** Make the trail multi-region, enable log file validation and KMS encryption, send it to CloudWatch Logs, and add the CIS metric filters and alarms. Enable AWS Config and VPC flow logs.
- **Effort:** Medium to high, but the largest single reduction in failing checks (up to 23).
- **Mapping:** CIS 3.x, 4.x · CIS Controls v8 8.2, 8.5 · NIST CSF 2.0 DE.CM-01 · ISO 27001:2022 A.8.15, A.8.16

## Considered but not shortlisted
- **Password policy** (min length, reuse): quick win with 2 findings. Console users should adopt MFA first. A good candidate for the next sprint.
- **EBS encryption** and **KMS key rotation**: real, but the data at risk is empty.
- **Security Hub and Access Analyzer:** missing detection services, a roadmap item.
- **Default-VPC NACLs and flow logs:** account-level hygiene.

## Open points for Day 5
- Tag each finding as sandbox-planted or real account.
- Decide whether items 1 and 5 are in remediation scope. Both change real account configuration.
- Day 9 must re-run with the identical flags: Prowler `--compliance cis_4.0_aws --scan-unused-services`, plus the ScoutSuite wrapper command.
