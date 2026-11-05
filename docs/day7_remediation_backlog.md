# Day 7 — Remediation Backlog

**Account:** 671154999764, `eu-west-2` · **Benchmark:** `cis_4.0_aws` (pinned)
**Source of truth:** `evidence/tuning/rescan/` (Prowler 5.48.0, v2 flags plus mutelist) — 52 counted failures, 10 muted
**Full backlog (spreadsheet):** `backlog/remediation_backlog.csv` — one row per item with every field below
**Related:** `docs/day5_triage.md` (bands), `docs/day6_false_positive_register.md` (suppressions)

## Summary

| | Items | Prowler rows |
|---|---|---|
| P0 (fix now) | 4 | 8 |
| P1 (this sprint) | 6 | 27 |
| P2 (backlog or roadmap) | 8 | 17 |
| **Total** | **18** | **52** |

B01–B15 carry the Day 5 triage IDs (T1–T15) and scores. B16–B18 are new: they cover failing checks that Day 5 did not score because they are medium or low severity. Their score is shown as "n/s" (not scored) and they are banded P2.

## Backlog (sequenced by risk)

| ID | Band | Score | Item | Scope | Owner | Effort | Rows | Day 8 |
|---|---|---|---|---|---|---|---|---|
| B01 | P0 | 10 | Enable MFA on the root account | Account | Account Owner | L | 2 | Yes, owner action |
| B02 | P0 | 10 | MFA on `cloud-project-admin`; move its direct `AdministratorAccess` | Account | Account Owner | L | 2 | Yes |
| B03 | P0 | 10 | Replace wildcard IAM policies; delete the admin access key | Sandbox | Cloud Security Engineer | M | 3 | Yes |
| B04 | P0 | 9 | Block public access on the sandbox bucket; remove public policy and ACL | Sandbox | Cloud Security Engineer | L | 1 | Yes |
| B05 | P1 | 8 | Add MFA and external-ID conditions to the admin sandbox role | Sandbox | Cloud Security Engineer | M | 1 | If time |
| B06 | P1 | 8 | Enable account-level S3 Block Public Access | Account | Cloud Security Engineer | L | 1 | Yes |
| B07 | P1 | 7 | MFA (or remove console password) for `scanner-identity` | Account | Account Owner | L | 1 | No |
| B08 | P1 | 6 | MFA for `cloudproject`; move its policy to a group | Account | Account Owner | L | 2 | No |
| B09 | P1 | 6 | Close internet-open rules on `sg-021c7366dcb131981` | Sandbox | Cloud Security Engineer | L | 1 | Yes |
| B10 | P1 | 7 | Harden CloudTrail; CloudWatch alarms, Config, flow logs | Both | DevSecOps Engineer | M | 21 | No |
| B11 | P2 | 5 | Restrict custom sandbox NACL `acl-0f4b…` | Sandbox | Cloud Security Engineer | L | 3 | No |
| B12 | P2 | 5 | Enable Security Hub | Account | Cloud Security Engineer | M | 1 | No |
| B13 | P2 | 4 | Empty rules on sandbox default SG `sg-0e69…` | Sandbox | Cloud Security Engineer | L | 1 | Quick win |
| B14 | P2 | 4 | Encrypt the EBS volume; enable default encryption | Sandbox | DevSecOps Engineer | M | 1 | No |
| B15 | P2 | 4 | Enable KMS key rotation | Sandbox | DevSecOps Engineer | L | 1 | No |
| B16 | P2 | n/s | Strengthen the password policy | Account | Cloud Security Engineer | L | 2 | Yes |
| B17 | P2 | n/s | S3 hardening: deny HTTP, MFA delete, versioning | Sandbox | Cloud Security Engineer | L | 4 | No |
| B18 | P2 | n/s | Roadmap: Access Analyzer, S3 data events, support role | Account | GRC Analyst | L | 4 | No |

Remediation steps, affected resources, scanner checks, ScoutSuite corroboration, and the verification check for each item are in the CSV.

## Owners
The owners are roles from the brief, played by one analyst in this engagement. **Account Owner** is the person who controls the console and root credentials. Actions on real identities (B01, B02, B07, B08) sit with them, since an analyst should not change the client's real MFA. Terraform-managed fixes go to the **Cloud Security Engineer** or **DevSecOps Engineer**. The **GRC Analyst** holds roadmap items.

## Definition of done
An item is Done only when all of these hold:
1. The fix is applied, and recorded in the remediation change log (Day 8) with before and after values.
2. The Terraform in `aws-misconfig-sandbox/` matches the live state. A fix made only in the console counts as incomplete, because the next apply would undo it.
3. The Prowler check for the item PASSES in the identical re-run (`cis_4.0_aws`, `--scan-unused-services`, same region and mutelist).
4. Where ScoutSuite corroborated the finding, the matching rule also clears.
5. The change was checked by something other than the scanner where practical, for example an anonymous GET on the bucket returning 403.
6. The backlog status is updated to Fixed, Muted or Accepted. Accepted risks carry a written reason.

## Review for completeness and duplicates
- **Completeness:** all 52 counted failures map to exactly one backlog item, with none unmapped and none counted twice. The 10 muted rows are in the false-positive register.
- **Duplicates collapsed:** B10 merges 21 rows. The two direct-attachment rows for `cloud-project-admin` sit under B02, not B05, because they concern the user and not the policy.
- **Cross-item dependency:** B04 (bucket) and B06 (account guardrail) fix the same class of problem at two levels. Do B06 first and B04 will then be blocked from re-exposure. B03 and B05 both involve admin rights and should be done together.
- **Detection limits to carry forward:**
  - Neither tool flags the CloudTrail trail being single-region. Prowler passes `cloudtrail_multi_region_enabled`, saying the trail is not multi-region and is logging. B10 includes the fix, but no scanner result will confirm it.
  - Prowler's per-port security-group checks passed for B09, so verify each rule, not just the check ID.
- **Control mappings:** CIS AWS 4.0 and ISO 27001:2022 IDs come from Prowler's compliance data. NIST CSF 2.0 categories and CIS Controls v8 safeguards are analyst-assigned because Prowler does not carry them. ISO IDs marked † are analyst additions where Prowler gives none. The Day 4 shortlist was updated to the same numbering.

## Day 8 sprint plan
The brief's Day 8 tasks line up with these items:

| Day 8 task | Backlog items |
|---|---|
| Enable MFA on root and privileged accounts | B01, B02 |
| Close security-group rules exposing sensitive ports | B09 (plus B13 as a quick win) |
| Enable S3 Block Public Access, remove public policies | B06, then B04 |
| Tighten over-permissive IAM; rotate or remove stale keys | B03 (and B05 if time) |
| Strengthen the password policy | B16 |

B10, the largest reduction, is not in the Day 8 list. It is the biggest single reduction if time allows.

## Open points before Day 8
- **Account Owner actions:** B01 and B02 change real identities. The analyst cannot do them, and root MFA needs a physical or virtual device.
- **Terraform state:** B03 deletes the access key whose secret sits in local state. Run `terraform apply` with the `projectadmin` profile, never with `scanner`.
- **B10 scope:** confirm whether Day 8 should include it, since it is the biggest single reduction but also the most effort.
