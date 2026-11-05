# Day 6 — False-Positive Register and Tuning Record

**Account:** 671154999764, `eu-west-2` · **Benchmark:** `cis_4.0_aws` (pinned)
**Baseline:** `evidence/baseline-v2/` — Prowler 5.48.0, 62 failing of 109 (immutable, not modified by tuning)
**Tuned re-scan:** `evidence/tuning/rescan/` — same flags plus `--mutelist-file`
**Mutelist:** `evidence/tuning/mutelist.yaml` · **ScoutSuite exceptions:** `evidence/tuning/scoutsuite_exceptions.json`

Principle: suppress deliberately, never silently. Each entry below was investigated against the live account before it was muted. A muted finding is either a **false positive** (does not apply), **not applicable**, **by design**, or an **accepted risk** with a named compensating control. Accepted risks are not the same as false positives and are reported separately.

## Register

| ID | Finding | Resource | Type | Evidence gathered | Compensating control | Rows muted |
|---|---|---|---|---|---|---|
| FP-01 | NACL allows ingress on any port, SSH, RDP | `acl-09b888c3ebaf97154` (default VPC, default NACL) | Accepted risk | Allow-all is the AWS default. 4 subnets, 0 network interfaces, 0 instances in the region. | Security groups are the working control, and none is attached to any interface | 3 |
| FP-02 | NACL allows ingress on any port, SSH, RDP | `acl-0100a9fc704bbef7f` (sandbox VPC, default NACL) | False positive | 0 subnet associations, so it is in no traffic path. The sandbox subnet uses the custom `acl-0f4b…` | Not in the traffic path | 3 |
| FP-03 | Default security group has rules | `sg-0a6efd621216a4c60` (default VPC) | Accepted risk | Only rule is the AWS-default self-reference. No `0.0.0.0/0`. 0 network interfaces. Cannot be deleted. | Self-reference only, nothing attached | 1 |
| FP-04 | SAML identity provider not configured | account | Not applicable | 0 SAML providers. Account is not in an AWS Organization. Single-account engagement. | n/a | 1 |
| FP-05 | Policy attached directly to a user | `scanner-identity` (SecurityAudit, ViewOnlyAccess) | By design | The brief tells you to attach both policies to the scanner identity | Both are AWS read-only managed policies | 2 |
| | | | | | **Total rows muted** | **10** |

## Deliberately not muted
These looked like suppression candidates but are real or planted findings, and they stay visible for the Day 9 delta.

| Resource | Finding | Why it stays |
|---|---|---|
| `acl-0f4b13a4091768a56` | Custom NACL, allow-all, attached to the sandbox subnet | Planted. In the traffic path. |
| `sg-0e69af95c695f533e` | Sandbox default security group with rules | Planted finding, in remediation scope. Same low real risk as FP-03, but muting it would hide the Day 8 fix. |
| `cloud-project-admin`, `cloudproject`, `misconfig-sandbox-admin-user` | Direct policy attachments | Real. Only the scanner identity is by design. |
| `iam_support_role_created`, CloudTrail data events | Low-severity gaps | Real gaps, no compensating control. |
| Root and user MFA, public bucket, wildcard IAM, open security group | All P0 and P1 items | Real findings, not noise |

## Verification: tuned re-scan
Prowler re-run with the v2 flags plus the mutelist:

| | Baseline v2 | Tuned re-scan |
|---|---|---|
| FAIL (counted) | 62 | **52** |
| FAIL (muted) | 0 | 10 |
| PASS | 44 | 44 |
| MANUAL | 3 | 3 |

- Exactly 10 rows were muted, matching the expected count.
- Every muted finding was a failing row in the baseline.
- Zero unintended changes: no other finding changed status.

ScoutSuite re-run with the equivalent exceptions file. All 40 rules still flag something, because the planted items remain, but four rules lose items:

| Rule | Before | After |
|---|---|---|
| `ec2-default-security-group-with-rules` | 4 | 2 |
| `ec2-security-group-opens-all-ports-to-self` | 2 | 1 |
| `vpc-default-network-acls-allow-all-ingress` | 3 | 1 |
| `vpc-default-network-acls-allow-all-egress` | 3 | 1 |

The remaining items are the planted `acl-0f4b…` and `sg-0e69…`.

## Tool behaviour notes
- **Prowler false negative:** the port-specific security-group checks (SSH, RDP, MySQL, PostgreSQL) passed for the sandbox's open group, while ScoutSuite flagged all four. Only the all-ports rule was caught. This is a missed detection, not a false positive, and it is not suppressed. It is scored as a real finding in the Day 5 triage (T9).
- **Unused resources:** Prowler skips security groups that are not attached to an instance unless `--scan-unused-services` is set. The baseline, the tuned re-scan and the Day 9 verification all use that flag.
- **Mutelist syntax:** Prowler 5.48.0 has no field for a written reason. Justifications live in the YAML comments and in this register.
- **ScoutSuite on Python 3.14:** it needs an event-loop wrapper to run. The same wrapper is used for the exceptions run.

## For the Day 9 re-run
Keep these identical: Prowler `--compliance cis_4.0_aws --scan-unused-services --region eu-west-2`, the mutelist, the ScoutSuite wrapper with `--exceptions`. Compare against both the raw baseline (62) and the tuned baseline (52), and report fixed, muted and accepted items separately.
