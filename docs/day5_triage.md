# Day 5 — Severity vs Exploitability Triage

**Account:** 671154999764, `eu-west-2` · **Benchmark:** `cis_4.0_aws` (pinned)
**Source:** `evidence/baseline-v2/` (Prowler 5.48.0) cross-checked with `evidence/scoutsuite/` (ScoutSuite 5.14.0)
**Scope:** all 18 critical and high Prowler findings (3 critical, 15 high), plus one medium cluster promoted on risk (T10).
**Status:** PRELIMINARY bands. Owners, remediation steps and framework mappings go in the Day 7 backlog.

## Rubric
Each factor is scored 1–3. The total is out of 12.

| Factor | 1 | 2 | 3 |
|---|---|---|---|
| **Exposure** | Internal only, or a guardrail gap creating no exposure by itself | Reachable from the internet but needs credentials or a precondition | Open to anyone on the internet |
| **Exploitability** | Needs several steps or a workload that doesn't exist | Needs one credential leak or one in-account foothold | Trivial, no authentication needed |
| **Blast radius** | One resource | One VPC, service or single-purpose identity | Whole account or all data |
| **Data sensitivity** | None or empty | Metadata, configs, or customer data if the control were used for real | Regulated or customer financial data, or unlimited access to it |

**Bands:** P0 (fix now) ≥ 9 · P1 (this sprint) 6–8 · P2 (backlog or accept) ≤ 5.
Fix effort (L/M/H) is the tiebreaker inside a band and is not part of the score.

**Assumption to confirm:** the sandbox bucket holds no real data. T4 is scored as if it were the fintech's customer bucket, because that is the scenario the engagement simulates. With no data (D = 1) it would be P1 (8).

## Triaged findings

| ID | Finding (source rows) | Scope | E | X | B | D | Total | Effort | Band |
|---|---|---|---|---|---|---|---|---|---|
| T1 | Root account has no MFA or hardware MFA (2 critical) | Account | 2 | 2 | 3 | 3 | **10** | L | **P0** |
| T2 | `cloud-project-admin` has console access, no MFA, and holds admin rights (1 high) | Account | 2 | 2 | 3 | 3 | **10** | L | **P0** |
| T3 | `misconfig-sandbox-admin-wildcard` (`*:*`), inline wildcard policy and long-lived key on `misconfig-sandbox-admin-user` (1 high) | Sandbox | 2 | 2 | 3 | 3 | **10** | M | **P0** |
| T4 | Public bucket `misconfig-sandbox-public-data-*`: Block Public Access off, anonymous read, public ACL (1 high) | Sandbox | 3 | 3 | 1 | 2 | **9** | L | **P0** |
| T5 | `AdministratorAccess` on the sandbox role, trusted by the whole account with no MFA or external-ID condition (1 critical) | Sandbox | 1 | 1 | 3 | 3 | **8** | M | P1 |
| T6 | No account-level S3 Block Public Access (1 high) | Account | 1 | 2 | 3 | 2 | **8** | L | P1 |
| T7 | `scanner-identity` console user without MFA (1 high) | Account | 2 | 2 | 1 | 2 | **7** | L | P1 |
| T8 | `cloudproject` console user without MFA (1 high) | Account | 2 | 2 | 1 | 1 | **6** | L | P1 |
| T9 | Open security group `sg-021c7366dcb131981`: all ports, plus SSH, RDP, MySQL and PostgreSQL (1 high, plus ScoutSuite per-port) | Sandbox | 2 | 1 | 2 | 1 | **6** | L | P1 |
| T10 | CloudTrail hardening: single-region, no log validation or KMS, not sent to CloudWatch (medium, promoted) | Sandbox + account | 1 | 1 | 3 | 2 | **7** | M | P1 |
| T11 | Network ACLs allow ingress on any port (3 high) | 1 sandbox + 2 default VPC | 1 | 1 | 2 | 1 | **5** | L | P2 |
| T12 | Security Hub not enabled (1 high) | Account | 1 | 1 | 2 | 1 | **5** | M | P2 |
| T13 | Default security groups with rules (2 high) | Sandbox + default VPC | 1 | 1 | 1 | 1 | **4** | L | P2 |
| T14 | Unencrypted EBS volume `vol-03482f81499ede4f1` (1 high) | Sandbox | 1 | 1 | 1 | 1 | **4** | M | P2 |
| T15 | KMS key rotation disabled (1 high) | Sandbox | 1 | 1 | 1 | 1 | **4** | L | P2 |

All 18 critical and high Prowler findings are covered: T1 (2), T2–T3 and T5–T8 (1 each), T4 (1), T9 (1), T11 (3), T12 (1), T13 (2), T14 (1), T15 (1).

## Reasoning behind the main decisions

**T1, T2: MFA findings are P0 despite low effort.** Root compromise is total account loss, and MFA is a few minutes of console work. `cloud-project-admin` is held to the same standard because it's an unrestricted identity. T7 and T8 sit lower only because those users have far less power.

**T3: wildcard policies and a standing key.** One leaked key gives full control. The access key sits in the local Terraform state, which is gitignored but not encrypted.

**T4: public bucket.** Fully open to the internet and trivial to read, so exposure and exploitability both score 3. Blast radius is one bucket, which is why it isn't higher. `PutObject` was removed earlier, so there is no public write.

**T5: critical severity, P1 priority.** Prowler rates `AdministratorAccess` critical because it is context-free. In this account the role trusts only the account root, so no outside party can assume it. A foothold inside the account is needed first. It stays P1 because it has no MFA condition.

**T9: open security group.** It scores 6 because the group is not attached to any instance, so nothing listens on those ports. If an instance were attached, exposure and exploitability would both rise and it would move to P0. ScoutSuite flags the SSH, RDP and database ports. Prowler's port-specific checks passed, so those rules are scored here as real findings.

**T10: promoted from medium.** CloudTrail, validation and the CloudWatch integration aren't high severity on their own. They govern whether an attack is seen at all, and they drive about 15 monitoring failures, so they rank above several high findings.

**T11, T13: P2 and Day 6 candidates.** Default NACLs allow all traffic in every AWS account by default, and security groups are the working control. These are likely accepted-risk or false-positive entries for the default VPC, with a documented reason.

## Where severity and priority diverge
| Finding | Scanner severity | Band |
|---|---|---|
| `AdministratorAccess` on a restricted role (T5) | Critical | P1 |
| Network ACLs allow any port (T11) | High | P2 |
| Security Hub not enabled (T12) | High | P2 |
| KMS rotation off on an unused key (T15) | High | P2 |
| Default security groups with rules (T13) | High | P2 |
| CloudTrail and CloudWatch cluster (T10) | Medium | P1 |

## Open points
- **Real versus planted:** T1, T2, T6, T7, T8 and T12 concern real account configuration, not planted sandbox findings. Confirm which of these are in remediation scope.
- **Teardown:** `cloud-project-admin` keeps admin rights until the sandbox is destroyed. T2's MFA is the control that makes that period safe.
- **Day 6:** investigate T11 and T13 as suppression candidates, and record any justification in the false-positive register.
