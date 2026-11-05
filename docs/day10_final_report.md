# Cloud Security Posture Assessment and CIS Benchmark Remediation on AWS

**Client:** VaultBridge Financial (simulated fintech) · **Account:** 671154999764, `eu-west-2`
**Benchmark:** CIS AWS Foundations Benchmark v4.0 (`cis_4.0_aws`), pinned for the whole engagement
**Tools:** Prowler 5.48.0 (source of truth for the score), ScoutSuite 5.14.0 (corroboration), Terraform
**Status:** Final measurement complete (2026-11-05, 07:42 UTC credential-report refresh). Sandbox teardown is the remaining step.

## 1. Executive summary

VaultBridge's AWS account was built quickly and never assessed against a security baseline. We scanned it read-only against CIS AWS Foundations v4.0, triaged the results by real-world risk, fixed the highest-priority items in a controlled way, and re-scanned to prove the improvement.

- **Starting point:** 62 failing checks out of 109, including 3 critical and 15 high.
- **After remediation:** 38 failing checks counted out of 100 (48 raw, with 10 deliberately suppressed and documented). Critical findings fell from 3 to 1, high from 15 to 5, with no new failures. A first verification run read 41 because of a stale cached report; the final run after the refresh confirmed 38.
- **Biggest wins:** the sandbox data bucket is no longer publicly readable, the internet-open firewall rules are gone, the wildcard administrator user and its long-lived key are deleted, root and administrator logins now require MFA, and the account has a password policy.
- **What remains:** logging and monitoring (21 findings) is the largest block and is deferred to the roadmap, along with several smaller hardening items. The scanner identity still has a console password without MFA.
- **Decisions needed from leadership:** approve the logging and monitoring work (roadmap phase 1), and accept or fund the remaining risks in section 7.

## 2. Scope and method

**In scope:** IAM, logging and monitoring, networking, S3 storage, and encryption and key management, in one AWS account and one region. Assessment was read-only. Remediation was limited to a selected, highest-priority subset.

**Out of scope:** remediating every finding (accepting a risk with justification is a valid outcome), other regions, and workloads.

**Identity separation:** a read-only `scanner-identity` (`SecurityAudit`, `ViewOnlyAccess`) ran every scan. A separate administrative identity built and changed the environment and never scanned.

**Environment note:** the brief asks for a dedicated sandbox account. The sandbox was deployed into an account that also holds real identities. That shaped several decisions: the sandbox administrator role trusts only this account, the bucket was made write-protected, and findings are tagged as planted or real.

**Process:** Day 2 environment and access, Day 3 Prowler baseline, Day 4 ScoutSuite and cross-reference, Day 5 triage, Day 6 false-positive tuning, Day 7 backlog, Day 8 remediation, Day 9 verification, Day 10 reporting. The supporting documents are in `docs/`.

## 3. Baseline

The first Prowler run did not evaluate security groups, because Prowler skips unattached groups by default. It reported 57 failures out of 96. We re-ran with `--scan-unused-services`, which found 5 more failures, and adopted that as the official baseline: **62 failing of 109**. The first run is kept for the record. Both baselines are immutable and hashed.

| CIS section | Failing at baseline | Failing at final verification |
|---|---|---|
| 1 Identity and Access Management | 18 | 8 |
| 2 Storage | 6 | 4 |
| 3 Logging | 9 | 9 |
| 4 Monitoring | 16 | 16 |
| 5 Networking | 14 | 11 |
| **Total** | **63** | **48** |

These counts are raw (muted rows included) and by CIS requirement. One security-group check maps to two requirements, so the baseline reads 63 here against 62 findings elsewhere.

## 4. Triage

Findings were scored 1–3 on exposure, exploitability, blast radius and data sensitivity (maximum 12). P0 is 9 or more, P1 is 6–8, P2 is 5 or less. Scanner severity was not used as the priority. Examples where the two diverged:

| Finding | Scanner severity | Our priority | Why |
|---|---|---|---|
| `AdministratorAccess` on a role trusting only this account | Critical | P1 | No outside party can assume it |
| Default-VPC network ACLs allow all traffic | High | Accepted risk | AWS default; security groups are the working control; nothing attached |
| CloudTrail and CloudWatch gaps | Medium | P1 | They decide whether an attack is seen at all |

Assumption: the sandbox bucket holds no real data. It was scored as if it held customer data, because the engagement simulates a fintech.

## 5. Remediation and results

| Backlog | Fix | Result |
|---|---|---|
| B03 | Deleted the wildcard administrator user, its access key and both wildcard policies | Verified |
| B04 | Public bucket: Block Public Access on, public policy deleted, ACL private | Verified. Anonymous requests return 403. |
| B06 | Account-level S3 Block Public Access | Verified |
| B09 | Removed 5 internet-open rules from the sandbox security group | Verified by both tools |
| B13 | Emptied the sandbox default security group | Verified |
| B16 | Password policy: 14+ characters, 24-password history | Verified |
| B01 | Root MFA (hardware) | Verified: both root MFA checks pass |
| B02 | MFA on `cloud-project-admin`; administrator rights moved to a group | Verified |
| B08 | MFA on `cloudproject` | MFA verified. Direct policy attachment remains open |

Every infrastructure change went through Terraform, and Terraform reports no drift from the live account. The full record, with before and after values, is `docs/day8_change_log.md`.

**A stale credential report hid three fixes:** Prowler reads the IAM credential report, which AWS caches for four hours. The first verification run read a report generated before the MFA devices were registered, so three MFA rows still failed (41 counted). After the report refreshed at 07:42 UTC the final run cleared all three (38 counted), matching the direct API evidence. Five PASS rows for the deleted admin user, kept alive by the stale report, also disappeared.

## 6. Framework mapping

Every backlog item is mapped in `backlog/remediation_backlog.csv`. CIS AWS 4.0 and ISO 27001:2022 IDs come from Prowler's compliance data. NIST CSF 2.0 categories and CIS Controls v8 safeguards were assigned by the analyst, since Prowler does not carry them.

| Theme | Items | CIS AWS 4.0 | CIS Controls v8 | NIST CSF 2.0 | ISO 27001:2022 |
|---|---|---|---|---|---|
| Root and user MFA | B01, B02, B07, B08 | 1.5, 1.6, 1.10 | 5.4, 6.5 | PR.AA-03 | A.5.15, A.5.17, A.8.5 |
| Over-privileged identities | B03, B05 | 1.15, 1.16 | 5.4, 6.8 | PR.AA-05 | A.5.15, A.5.18, A.8.2 |
| Public data exposure | B04, B06 | 2.1.4 | 3.3 | PR.DS-01 | A.8.1, A.8.3 |
| Network exposure | B09, B11, B13 | 5.2–5.5 | 4.4, 12.2 | PR.IR-01 | A.8.20–A.8.22 |
| Logging and monitoring | B10, B12 | 3.x, 4.x | 8.2, 8.5, 8.9 | DE.CM-01, DE.AE-02 | A.8.15, A.8.16 |
| Encryption and keys | B14, B15, B17 | 3.6, 5.1.1, 2.1.1 | 3.10, 3.11 | PR.DS-01, PR.DS-02 | A.8.11, A.8.24 |
| Credential hygiene | B16 | 1.8, 1.9 | 5.2 | PR.AA-01 | A.5.15, A.5.17 |

## 7. Accepted and deferred risks

**Accepted (suppressed with a compensating control)**, from `docs/day6_false_positive_register.md`:
- **FP-01:** the default VPC's default network ACL allows all traffic. This is the AWS default, no network interface is attached, and security groups are the working control.
- **FP-03:** the default VPC's default security group has only the self-reference rule and nothing attached.
- **FP-02, FP-04, FP-05:** not accepted risks but false positive, not applicable and by design (an unassociated ACL, no SAML or Organization, and the scanner's own read-only policies).

**Deferred to the roadmap (open, with a reason):**
- **B10, logging and monitoring (21 rows):** the largest reduction, but it needs a design decision on log retention and alerting. It is not in the Day 8 sprint.
- **B05, B07, B11, B12, B14, B15, B17, B18:** lower priority or low real exposure in the sandbox.

**Residual and temporary risks:**
- **Build access:** `cloud-project-admin` holds administrator rights through the `sandbox-builders` group until teardown.
- **Password expiry:** no forced expiry, following NIST SP 800-63B guidance. ScoutSuite's expiry rules still flag it, and that is a rule disagreement, not a defect.

## 8. Limitations and lessons

- **Prowler false negative:** its per-port security-group checks passed for a group open on SSH, RDP, MySQL and PostgreSQL. ScoutSuite caught all of them. Run both tools, and verify rules, not just check IDs.
- **Single-region trail:** neither tool flags it. Prowler passes the multi-region check for a regional trail in a regional scan.
- **Unused resources:** Prowler skips unattached security groups unless told otherwise. Pin the flags as well as the benchmark.
- **Stale credential report:** identity checks lag up to four hours behind a change. Allow for it before a verification run.
- **Python 3.14:** ScoutSuite needs an event-loop wrapper to run.
- **Terraform:** omitted `ingress` and `egress` blocks leave existing rules in place. Empty lists are required. The plan caught this before the apply.

## 9. Retest scope and cadence

- **Pinned version:** stay on `cis_4.0_aws` for comparability. Prowler also supports newer CIS versions. Move to one with a fresh baseline, not mid-series.
- **Identical flags:** `--compliance cis_4.0_aws --scan-unused-services --region eu-west-2`, the mutelist, and the ScoutSuite wrapper with the exceptions file.
- **Cadence:** a full scan quarterly, an identity-only scan monthly, and a re-scan after any significant change.
- **Retest scope:** all open backlog items, the muted entries (re-justify each), and any new region or account.
- **Automation:** run Prowler in CI against Terraform changes (DevSecOps), so regressions fail before they ship.

## 10. Evidence index

| Artefact | Location |
|---|---|
| Baseline (first run) and v2 baseline | `evidence/baseline/`, `evidence/baseline-v2/` |
| Security-group addendum | `evidence/baseline-addendum/` |
| ScoutSuite baseline | `evidence/scoutsuite/` |
| Mutelist, exceptions, tuned re-scan | `evidence/tuning/` |
| Verification runs | `evidence/verification/` (first, stale credential report), `evidence/verification-final/` (final) |
| Pre-remediation Terraform | `evidence/terraform-baseline/` |
| Triage, register, backlog, change log, verification | `docs/day5_triage.md` through `docs/day9_verification.md`, `backlog/remediation_backlog.csv` |
