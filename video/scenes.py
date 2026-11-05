"""Storyboard: 28 scenes. Each scene is a visual (HTML, reveals by beat) plus one narration string per beat.

The account ID is deliberately never shown or spoken, so the video can be shared safely.
"""
from lib import (scene, row, col, card, stat, chip, call, arrow, term, table, hbars, vbars, steps, raw, disc, ic, esc, COL)

SCENES = []


def S(kicker, title, body, beats):
    SCENES.append(dict(id=len(SCENES) + 1, title=title, html=scene(kicker, title, body), beats=beats))


# ---------------------------------------------------------------- 1 title
rings = "".join(
    f'<div style="position:absolute;left:{300 - r}px;top:{300 - r}px;width:{2 * r}px;height:{2 * r}px;border-radius:50%;'
    f'border:3px solid rgba(25,181,196,{a});background:rgba(25,181,196,{a / 6})"></div>'
    for r, a in ((290, .35), (210, .5), (130, .7)))
title_html = f"""<div class="scene" style="display:flex;align-items:center;gap:60px">
<div style="flex:1"><div class="kick" style="font-size:30px">Video tutorial</div>
<div class="serif bigtitle" style="margin:22px 0 34px">Cloud Security Posture Assessment on AWS</div>
<div class="sub" style="font-size:40px">From the first requirement to the last cleanup command</div>
<div style="margin-top:56px">{chip('Find', 'teal', 2)}{chip('Fix', 'amber', 2)}{chip('Prove', 'green', 2)}</div>
<div style="margin-top:20px">{chip('Requirements', 'purple', 3)}{chip('Challenges', 'red', 3)}{chip('Solution', 'teal', 3)}{chip('Lessons', 'amber', 3)}</div></div>
<div style="position:relative;width:600px;height:600px;flex:none">{rings}
<div style="position:absolute;left:200px;top:200px">{disc('FaShieldAlt', 'teal', 200)}</div></div></div>"""
SCENES.append(dict(id=1, title="Introduction", html=title_html, beats=[
    "This is a complete walkthrough of a cloud security engagement, from the first requirement to the last cleanup command.",
    "We assess an AWS account against the CIS Foundations Benchmark, find what is wrong, fix what matters most, and prove the improvement with numbers.",
    "Along the way you will see the requirements, the tools, the challenges that went wrong, how each was solved, and the lessons worth keeping.",
]))

# ---------------------------------------------------------------- 2 client
S("The situation", "A fintech built in a hurry",
  col(
      card("VaultBridge Financial", "A simulated fintech running digital wallets and payments on Amazon Web Services.", "teal", "FaMoneyBillWave", b=1),
      row(card("Built fast", "Deadlines came before security reviews.", "amber", b=2, cls="grow"),
          card("Broad permissions", "Developers hold far more access than they need.", "amber", b=2, cls="grow"),
          card("No baseline", "Nobody ever checked it against a standard.", "amber", b=2, cls="grow")),
      row(card("No MFA on root", "", "red", "FaLock", b=3, cls="grow"),
          card("Public storage", "", "red", "FaDatabase", b=3, cls="grow"),
          card("Open ports", "", "red", "FaNetworkWired", b=3, cls="grow"),
          card("Logging gaps", "", "red", "FaEyeSlash", b=3, cls="grow")),
      call("Any one of these can become a data breach, so the client needs evidence, a priority list and measured improvement.", "teal", b=4)),
  ["The client is VaultBridge Financial, a simulated fintech that runs digital wallets and payments on Amazon Web Services.",
   "The account was built fast, by developers holding broad permissions, and nobody ever checked it against a security standard.",
   "That leaves four classic problems: a root account without multi-factor authentication, storage that can be public, firewall rules open to the whole internet, and logging with gaps.",
   "In a fintech, any one of these can become a data breach, so the client needs evidence, a priority list, and measured improvement."])

# ---------------------------------------------------------------- 3 requirements
S("The requirements", "What the brief demands",
  col(
      row(card("Four objectives", "", "teal", "FaBullseye", b=1, cls="grow", items=[
          "Baseline against the CIS AWS benchmark", "Triage by real-world risk", "Remediate the top priorities",
          "Prove it by re-running the benchmark"]),
          card("Six deliverables", "", "purple", "FaClipboardCheck", b=2, cls="grow", items=[
              "Baseline assessment", "Triaged backlog", "False-positive register", "Remediation change log",
              "Before and after comparison", "Final report"])),
      raw(chip("Read-only assessment", "amber", 3) + chip("One pinned benchmark", "amber", 3) +
          chip("Separate builder and scanner", "amber", 3) + chip("Ten working days", "amber", 3), b=3)),
  ["The brief sets four objectives: establish a baseline against the CIS AWS Foundations Benchmark, triage findings by real risk, remediate the highest priorities, and prove improvement by re-running the benchmark.",
   "Six deliverables are expected: a baseline assessment, a triaged backlog, a false positive register, a remediation change log, a before and after comparison, and a final report.",
   "The rules are strict. Assessment is read only. One benchmark version is pinned for the whole engagement. The scanner and the builder must be separate identities. And the whole thing fits in two weeks."])

# ---------------------------------------------------------------- 4 frameworks
S("The yardstick", "What is a CIS Benchmark?",
  col(
      card("Prescriptive and testable", "A consensus set of numbered security settings. A scanner can say pass or fail for each one.", "teal", "FaBalanceScale", b=1),
      row(card("Level 1", "Baseline hardening with low friction.", "green", b=2, cls="grow"),
          card("Level 2", "Stronger defence in depth. May affect cost or usability.", "amber", b=2, cls="grow")),
      row(card("CIS AWS 4.0", "The benchmark itself", "teal", b=3, cls="grow"), card("CIS Controls v8", "Prioritised safeguards", "teal", b=3, cls="grow"),
          card("NIST CSF", "Cybersecurity Framework", "teal", b=3, cls="grow"), card("ISO 27001", "Annex A controls", "teal", b=3, cls="grow")),
      call("Pinning one version, CIS AWS 4.0, makes every later comparison fair.", "amber", b=4)),
  ["A CIS Benchmark is a consensus set of prescriptive, testable security settings. Each recommendation is numbered, so a scanner can say pass or fail.",
   "Level one is baseline hardening with low friction. Level two is stronger defence in depth that may affect cost or usability.",
   "We map every finding to four frameworks: the benchmark itself, CIS Controls version eight, the NIST Cybersecurity Framework, and ISO twenty seven thousand and one.",
   "Pinning one version, CIS AWS four point zero, makes every later comparison fair."])

# ---------------------------------------------------------------- 5 architecture
S("The setup", "Two identities, never mixed",
  col(
      row(raw(card("Builder", "", "amber", "FaTools", style="height:100%", items=[
          "cloud-project-admin", "Terraform only", "Never scans"]), b=1, cls="grow"),
          arrow(1, "→"),
          raw(card("AWS account", "", "teal", "FaCloud", style="height:100%", items=[
              "London region", "Sandbox with planted weaknesses", "Beside a few real identities"]), b=4, cls="grow"),
          arrow(2, "←"),
          raw(card("Scanner", "", "green", "FaSearch", style="height:100%", items=[
              "scanner-identity", "SecurityAudit + ViewOnlyAccess", "Read-only"]), b=2, cls="grow"), gap=20),
      raw(chip("Terraform", "amber", 1) + chip("Prowler: the scorekeeper", "green", 3) + chip("ScoutSuite: the second opinion", "green", 3) + chip("Docker", "slate", 3), b=0)),
  ["Two identities, never mixed. The builder creates and changes things with Terraform, and never scans.",
   "The scanner holds only two AWS read only policies, Security Audit and View Only Access. It can look at everything and change nothing.",
   "Prowler is the scorekeeper, because its checks map directly to benchmark control numbers. ScoutSuite is the second opinion.",
   "The target is one AWS account in the London region, with a deliberately misconfigured sandbox planted beside a few real identities."])

# ---------------------------------------------------------------- 6 plan
def grp(color, name, days, b):
    items = "".join(f'<li><b>{d}</b> {t}</li>' for d, t in days)
    return card(name, "", color, b=b, cls="grow", style="min-height:560px",
                items=[f'<b class="t-{color}">{d}</b> {t}' for d, t in days])


S("The plan", "Ten days, one artefact per day",
  row(grp("teal", "Set up", [("Day 1", "Pin the benchmark"), ("Day 2", "Scanner and sandbox")], 2),
      grp("green", "Measure", [("Day 3", "Prowler baseline"), ("Day 4", "ScoutSuite")], 2),
      grp("amber", "Decide", [("Day 5", "Triage"), ("Day 6", "Tune false positives"), ("Day 7", "Backlog")], 3),
      grp("purple", "Act and prove", [("Day 8", "Remediate"), ("Day 9", "Re-scan"), ("Day 10", "Report and tear down")], 4)),
  ["The work is organised as ten days, and every day ends with an artefact you can point to.",
   "Days one and two set up access and build the sandbox. Days three and four measure, with Prowler and then ScoutSuite.",
   "Days five to seven decide: triage, tune out false positives, and build the backlog.",
   "Days eight and nine act and prove: remediate, then re-scan. Day ten reports and tears everything down."])

# ---------------------------------------------------------------- 7 setup
S("Days 1 and 2", "Pin the version, create the scanner",
  col(
      steps([("1", "Pin the benchmark", "CIS AWS 4.0", "teal"), ("2", "Create the scanner", "Console user, two read-only policies", "green"),
             ("3", "Prove who it is", "Caller identity check", "amber")], b0=1),
      term([("$ aws sts get-caller-identity --profile scanner", "p", 3),
            ('  "Arn": "arn:aws:iam::<account>:user/scanner-identity"', "ok", 3),
            ("$ aws sts get-caller-identity          # the machine's default profile", "p", 4),
            ('  "Arn": "arn:aws:iam::<account>:user/cloudproject"      <- a different user!', "bad", 4)], b0=3),
      call("Challenge: the default profile was an unrelated user with no IAM read access. Always verify the identity before you scan.", "amber", b=4)),
  ["Day one is a decision: pin CIS AWS four point zero. Day two creates the scanner identity.",
   "The user is created in the console, given the two read only policies, and an access key goes into a dedicated command line profile.",
   "Then we prove it works with a caller identity check, which shows exactly which account and which user a scan will run as.",
   "A first challenge appeared here: the default profile on the machine belonged to a different, unrelated user with no I A M read access. Always verify the identity before you scan."])

# ---------------------------------------------------------------- 8 sandbox
S("Day 2", "Building the sandbox on purpose",
  col(
      raw(chip("Terraform", "amber", 1) + chip("Infrastructure as code", "amber", 1) + chip("Disposable", "amber", 1), b=1),
      table(["Area", "Planted weakness", "Expected finding"], [
          (["Identity", "Admin user with full-access policies and a live key. An admin role.", "Wildcard policies, long-lived key"], 2),
          (["Network", "Security group open to the internet on SSH, RDP and database ports. Allow-all network ACL.", "Open ports, no flow logs"], 3),
          (["Storage", "Public bucket with block public access off. Unencrypted disk.", "Public data, no encryption"], 4)],
            widths=["200px", "900px", "560px"]),
      call("Everything is tagged as a training range, and each weakness is documented in the code.", "green", b=5)),
  ["The sandbox is built with Terraform, and every weakness is planted on purpose so the scanners have realistic findings.",
   "In identity and access: a user with full administrator policies and a long lived access key, and a role with administrator rights.",
   "In networking: a security group open to the internet on S S H, R D P, and database ports, a wide open network ACL, and no flow logs.",
   "In storage: a public bucket with block public access switched off, plus an unencrypted disk volume.",
   "Everything is tagged as a training range, and the code documents each finding, so the lab can never be mistaken for production."])

# ---------------------------------------------------------------- 9 plan review
S("Before applying", "Review the plan against the brief",
  col(
      card("terraform plan", "22 resources to add. Compared line by line with the brief.", "teal", "FaSearch", b=1),
      row(raw(card("Gap", "The brief says logging is partial. The plan had none, and no keys to rotate.", "red", b=2), cls="grow"), arrow(4),
          raw(card("Fix", "A weak CloudTrail and a KMS key with rotation off.", "green", b=4), cls="grow")),
      row(raw(card("Risk", "A role any principal could assume, and a bucket anyone could write to.", "red", b=3), cls="grow"), arrow(4),
          raw(card("Fix", "Role trusts this account only. Public write removed. Weaknesses stay, real danger goes.", "green", b=4), cls="grow"))),
  ["Before applying, we ran a Terraform plan and compared it with the brief, line by line.",
   "That found gaps. The brief mentions partial logging, but the plan had no logging at all, and no encryption keys to rotate.",
   "The sandbox also sat inside an account that holds real identities, so a role trusting any principal on the internet would be a genuine takeover risk, and a world writable bucket would let anyone upload at your cost.",
   "The fixes: add a weak CloudTrail and a key with rotation off, restrict the role to this account, and remove public write from the bucket. The weaknesses stay, the real danger goes."])

# ---------------------------------------------------------------- 10 challenge: builder perms
S("Challenge", "The first apply failed",
  col(
      term([("$ terraform apply", "p", 1),
            ("Error: creating EC2 VPC: UnauthorizedOperation", "bad", 1),
            ("Error: creating S3 Bucket: AccessDenied", "bad", 1),
            ("", "", 3),
            ("$ AWS_PROFILE=projectadmin terraform apply", "p", 3),
            ("Apply complete! Resources: 25 added, 0 changed, 0 destroyed.", "ok", 3)], b0=1),
      row(card("Why", "The only profile had IAM read-only access.", "red", b=2, cls="grow"),
          card("Design", "Building needs its own admin identity, used once, never to scan.", "amber", b=2, cls="grow"),
          card("Result", "Scanner identity stays untouched.", "green", b=3, cls="grow"))),
  ["The first apply failed. Every create call returned access denied, because the only profile on the machine had read only I A M access.",
   "The brief anticipates this: building needs its own administrative identity, used once to build and never to scan.",
   "A second user with administrator rights solved it, and the scan identity stayed untouched."])

# ---------------------------------------------------------------- 11 baseline
S("Day 3", "The baseline, and a hidden gap",
  col(
      row(raw(term([("$ docker run --rm toniblyx/prowler aws \\", "p", 1),
                    ("    --compliance cis_4.0_aws --region eu-west-2 \\", "p", 1),
                    ("    --output-formats csv json-ocsf html", "p", 1),
                    ("", "", 5), ("# add the missing flag:", "c", 5),
                    ("    --scan-unused-services", "hi", 5)]), cls="grow"),
          col(stat("57 of 96", "failing checks, first run", "amber", b=2),
              stat("62 of 109", "failing checks, official baseline", "teal", b=5), gap=30, style="width:620px")),
      call("No security group results at all, not even for the default groups.", "red", b=3),
      call("Cause: Prowler skips security groups attached to nothing, unless told otherwise.", "amber", b=4),
      call("Lesson: pin the flags, not just the benchmark version.", "teal", b=6)),
  ["Day three is the baseline. Prowler runs in Docker with the scanner's credentials, against the pinned benchmark, and exports C S V, J S O N and H T M L.",
   "The first run reported fifty seven failures out of ninety six checks.",
   "But something was missing. There were no security group results at all, not even for the default groups.",
   "The cause: Prowler skips security groups that are not attached to anything, unless you add the scan unused services flag.",
   "Re-running with that flag gave sixty two failures out of one hundred and nine. That became the official baseline, and the first run is kept as a record.",
   "The lesson: pin the flags, not just the benchmark version. A baseline without the same flags cannot be compared."])

# ---------------------------------------------------------------- 12 baseline results
S("Day 3", "62 failing checks",
  row(col(hbars([("Critical", 3, "red", 1, "3"), ("High", 15, "amber", 1, "15"), ("Medium", 33, "purple", 1, "33"), ("Low", 11, "slate", 1, "11")], 33),
          call("Some findings are planted by us. Others are real: the console users lack MFA too. The analysis must tell them apart.", "amber", b=3), gap=40, cls="grow"),
      card("The criticals", "", "red", b=2, style="width:640px", items=[
          "Root account without MFA", "Hardware MFA missing on root", "AdministratorAccess attached"])),
  ["Sixty two failing checks: three critical, fifteen high, thirty three medium, and eleven low.",
   "The criticals are the root account without M F A, and administrator access attached.",
   "Some findings are planted by us, but others are real: the console users in the account also lack M F A. The analysis has to tell them apart."])

# ---------------------------------------------------------------- 13 ScoutSuite
S("Day 4", "A second opinion with ScoutSuite",
  row(raw(term([("RuntimeError: There is no current event loop", "bad", 1),
                ("", "", 2), ("# wrapper: create the loop, then call ScoutSuite", "c", 2),
                ("asyncio.set_event_loop(asyncio.new_event_loop())", "ok", 2),
                ("from ScoutSuite.__main__ import run_from_cli", "ok", 2),
                ("sys.exit(run_from_cli())", "ok", 2)], style="height:100%"), cls="grow"),
      col(stat("40 rules", "flagged, 17 at danger level", "teal", b=3),
          call("Four rules Prowler missed: " + chip("SSH", "red", 4) + chip("RDP", "red", 4) + chip("MySQL", "red", 4) + chip("PostgreSQL", "red", 4) + " open to the world", "red", b=4),
          call("Run two tools. A passing check is not proof a control exists.", "teal", b=5), gap=26, style="width:760px")),
  ["Day four runs ScoutSuite as a second opinion. It crashed immediately on Python three point fourteen, with an error about no current event loop.",
   "The fix was a tiny wrapper that creates the event loop first, then calls ScoutSuite's own entry point. The package itself is untouched.",
   "ScoutSuite flagged forty rules, seventeen at danger level, and most agreed with Prowler.",
   "But it caught four rules Prowler missed: S S H, R D P, My S Q L and Postgres open to the world on the security group. Prowler's per port checks had passed.",
   "That is why you run two tools, and why a passing check is not proof that a control exists."])

# ---------------------------------------------------------------- 14 triage rubric
S("Day 5", "Severity is not priority",
  col(
      card("The tool's severity label", "Context-free. It knows nothing about this account.", "red", "FaTimesCircle", b=1),
      row(card("Exposure", "Who can reach it?", "teal", "FaGlobe", b=2, cls="grow"), card("Exploitability", "How easy is it?", "teal", "FaBolt", b=2, cls="grow"),
          card("Blast radius", "How far does it spread?", "teal", "FaBomb", b=2, cls="grow"), card("Data sensitivity", "What is at stake?", "teal", "FaMoneyBillWave", b=2, cls="grow")),
      row(raw(stat("P0", "9 or more: fix now", "red"), b=3, cls="grow"), raw(stat("P1", "6 to 8: this sprint", "amber"), b=3, cls="grow"),
          raw(stat("P2", "5 or less: backlog or accept", "green"), b=3, cls="grow"))),
  ["Day five turns a long list into a priority order. Severity labels come from the tool and know nothing about this account.",
   "So each finding is scored from one to three on four factors: exposure, exploitability, blast radius, and data sensitivity.",
   "The total, out of twelve, sets the band. Nine or more is P zero, fix now. Six to eight is P one, this sprint. Five or less is P two, backlog or accept."])

# ---------------------------------------------------------------- 15 triage results
S("Day 5", "Where the scanner label misled",
  col(
      raw(hbars([("Root account MFA", 10, "red", 2, "10"), ("Admin user MFA", 10, "red", 2, "10"),
                 ("Wildcard admin user", 10, "red", 2, "10"), ("Public bucket", 9, "red", 2, "9")], 12, labw=360), b=2),
      row(card("Critical → P1", "AdministratorAccess on a role only this account can assume. No outsider can use it.", "amber", b=3, cls="grow"),
          card("High → accepted", "A default network ACL that allows all. It is the AWS default and nothing is attached.", "green", b=4, cls="grow"),
          card("Medium → P1", "CloudTrail gaps. Without logging you would never see an attack.", "amber", b=5, cls="grow"))),
  ["Four items landed in P zero: root M F A, the administrator user's M F A, the wildcard administrator user with its access key, and the public bucket.",
   "Where the scanner label and our priority disagree is the interesting part.",
   "Administrator Access on a role that only this account can assume is critical to the scanner, but only P one to us, because no outsider can use it.",
   "A default network ACL that allows all traffic is high severity, but it is the AWS default and nothing is attached, so it is an accepted risk.",
   "And a medium finding, the CloudTrail gaps, becomes P one, because without logging you would never see an attack."])

# ---------------------------------------------------------------- 16 false positives
S("Day 6", "Suppress deliberately, never silently",
  col(
      row(col(call("Every muted finding needs an investigation and a written reason.", "teal", b=1),
              term([("$ aws ec2 describe-network-acls", "p", 2), ("   acl-0100…  subnets: 0     <- in no traffic path", "ok", 2),
                    ("   acl-09b8…  subnets: 4  AWS default", "hi", 2), ("   acl-0f4b…  subnets: 1  planted, wide open", "bad", 2)]), cls="grow"),
          col(card("False positive", "Attached to no subnet.", "green", b=3), card("Accepted risk", "AWS default, nothing attached.", "amber", b=3),
              card("Stays visible", "The planted ACL on the sandbox subnet.", "red", b=3), gap=18, style="width:640px")),
      row(raw(term([("Mutelist:", "c", 4), ("  Checks:", "c", 4), ('    "ec2_networkacl_allow_ingress_any_port":', "", 4),
                    ('      Resources: ["acl-09b8…", "acl-0100…"]', "ok", 4)]), cls="grow"),
          raw(stat("62 → 52", "counted", "teal", size=64), b=5), raw(stat("10", "muted", "amber", size=64), b=5),
          raw(stat("0", "unintended", "green", size=64), b=5), gap=36)),
  ["Day six is tuning. The rule: suppress deliberately, never silently. Every muted finding needs an investigation and a written reason.",
   "We checked each candidate against the live account: how many subnets use this ACL, what rules does this group have, is anything attached.",
   "Three network ACLs looked the same, but one was in no traffic path, one was an AWS default, and one was the planted open ACL on the sandbox subnet, which must stay visible.",
   "Ten rows were muted, with a justification in the mutelist, and a matching exceptions file for ScoutSuite.",
   "The re scan confirmed it: sixty two became fifty two, exactly ten muted, and nothing else changed."])

# ---------------------------------------------------------------- 17 backlog
S("Day 7", "An 18-item backlog",
  col(
      row(raw(stat("18", "backlog items", "teal"), b=1), raw(stat("52 of 52", "counted failures mapped", "green"), b=1), cls="", gap=120),
      raw(chip("Owner", "teal", 2) + chip("Priority band", "teal", 2) + chip("Affected resources", "teal", 2) + chip("Remediation steps", "teal", 2) + chip("Proof of done", "teal", 2), b=2),
      row(card("Who does what", "Real identities, like root MFA, go to the account owner. An analyst should not alter a client's login security.", "amber", b=3, cls="grow"),
          card("Definition of done", "", "green", b=4, cls="grow", items=["Fix applied and logged", "Terraform matches live state", "Scanner check passes", "Second tool agrees"])),
      raw(chip("CIS AWS 4.0", "purple", 5) + chip("CIS Controls v8", "purple", 5) + chip("NIST CSF 2.0", "purple", 5) + chip("ISO 27001:2022", "purple", 5), b=5)),
  ["Day seven builds the remediation backlog, eighteen items, and every one of the fifty two counted failures maps to exactly one item.",
   "Each item has an owner role, a priority band, the affected resources, concrete steps, and the check that proves it is done.",
   "Changes to real identities, like root M F A, belong to the account owner, because an analyst should not alter a client's real login security.",
   "The definition of done is strict: fixed, in code, scanner passes, second tool agrees, and logged.",
   "Each item is also mapped to the four frameworks, taking the CIS and ISO numbers from Prowler's own data rather than guessing."])

# ---------------------------------------------------------------- 18 remediation
S("Day 8", "Six fixes, all through Terraform",
  col(
      call("Everything infrastructure related goes through Terraform, then is checked against the live account.", "teal", b=1),
      row(card("Public bucket", "Block public access on. Policy deleted. ACL private. Anonymous request: 403.", "teal", "FaDatabase", b=2, cls="grow"),
          card("Wildcard admin user", "User, key and policies deleted. Nothing used them.", "teal", "FaUserShield", b=3, cls="grow"),
          card("Open security group", "All five internet rules removed.", "teal", "FaNetworkWired", b=4, cls="grow")),
      row(card("Default group", "Rules emptied.", "teal", "FaLayerGroup", b=4, cls="grow"),
          card("Account guardrail", "S3 block public access, account wide.", "teal", "FaShieldAlt", b=4, cls="grow"),
          card("Password policy", "14+ characters, 24 history.", "teal", "FaKey", b=4, cls="grow"))),
  ["Day eight is the remediation sprint, and everything infrastructure related goes through Terraform.",
   "The public bucket gets block public access, no public policy, and a private A C L. An anonymous request now returns four oh three.",
   "The wildcard administrator user, its policies and its access key are deleted outright, since nothing used them.",
   "The open security group loses all five internet rules, the default group is emptied, an account wide S three block is added, and a password policy of fourteen characters is set."])

# ---------------------------------------------------------------- 19 challenges in remediation
S("Challenge", "Two traps in the sprint",
  row(raw(term([("$ terraform plan", "p", 1), ("  # security group:  no changes", "bad", 1), ("", "", 3),
                ("resource \"aws_security_group\" \"wide_open\" {", "", 3), ("-  ingress { cidr = 0.0.0.0/0  port = 22 }", "bad", 3),
                ("+  ingress = []", "ok", 3), ("}", "", 3)], style="height:100%"), cls="grow"),
      col(call("Terraform treats an omitted rule block as unmanaged, not removed. The rules would have stayed open.", "red", b=2),
          card("Second trap", "Moving admin rights off the build user left it with no permissions. The apply was blocked until a group carried the policy.", "amber", b=4),
          call("Both caught before any damage: plan first, verify after.", "green", b=5), gap=24, style="width:800px")),
  ["Two real challenges showed up here. First: the plan for the security groups showed no change at all.",
   "Terraform treats omitted rule blocks as unmanaged, not as removed. The rules would have stayed open.",
   "The fix is explicit empty lists, ingress equals empty, and the plan then showed the removals.",
   "Second: after we moved administrator rights off the build user, it had no permissions at all, and the apply was blocked until a group carried the policy.",
   "Both were caught before any damage, because plan came first and every change was verified against the live account."])

# ---------------------------------------------------------------- 20 owner actions
S("Day 8", "Fixes only the owner can make",
  row(card("Root account", "A hardware security key on the account with the largest blast radius.", "green", "FaFingerprint", b=1, cls="grow"),
      card("Console users", "MFA registered for the two real console users.", "green", "FaUserLock", b=2, cls="grow"),
      card("Real, not sandbox", "The S3 block and password policy are real hardening of the real account. Remember them for teardown.", "amber", "FaFlag", b=3, cls="grow")),
  ["Some fixes are not Terraform. Multi-factor authentication for the root account and the two console users was done by the account owner in the console.",
   "A hardware security key on root protects the account with the highest blast radius.",
   "Two account level settings, the S three block and the password policy, are real hardening of the real account, not sandbox resources, and we remember that for teardown."])

# ---------------------------------------------------------------- 21 verification
S("Day 9", "Prove it: same scan, same account",
  row(col(vbars([("Baseline", 62, "slate", 1), ("After tuning", 52, "teal", 1), ("First re-run", 41, "amber", 2), ("Final re-run", 38, "green", 6)], 62), cls="grow"),
      col(call("Three MFA rows still failed, though the devices were registered.", "red", b=3),
          card("Why", "Prowler reads the IAM credential report. AWS caches it for four hours. Ours predated the MFA devices.", "amber", b=4),
          call("Proof: it still listed a user we had deleted. We did not count those rows. We waited.", "amber", b=5),
          call("After the refresh: 38. All three pass, as predicted.", "green", b=6), gap=22, style="width:880px")),
  ["Day nine re-runs the identical scan, same flags, same mute list, same profile, and compares the numbers.",
   "Fifty two became forty one, with eleven rows cleared and no new failures.",
   "But three M F A rows still failed, even though the devices were registered.",
   "Prowler reads the I A M credential report, and AWS caches that report for four hours. Ours was generated before the M F A devices existed.",
   "The proof: it still listed the user we had deleted. We did not count those rows as fixed, and we waited.",
   "After the refresh the final run read thirty eight. The three rows passed, exactly as the direct evidence predicted."])

# ---------------------------------------------------------------- 22 results
S("Result", "62 down to 38",
  col(
      row(raw(stat("62 → 38", "failing checks", "teal"), b=1), raw(stat("3 → 1", "critical", "red"), b=1), raw(stat("15 → 5", "high", "amber"), b=1), gap=90),
      row(raw(hbars([("Identity and access", 18, "slate", 2, "18"), ("", 8, "teal", 2, "8"), ("Storage", 6, "slate", 2, "6"), ("", 4, "teal", 2, "4"),
                     ("Logging", 9, "slate", 2, "9"), ("", 9, "teal", 2, "9"), ("Monitoring", 16, "slate", 2, "16"), ("", 16, "teal", 2, "16"),
                     ("Networking", 14, "slate", 2, "14"), ("", 11, "teal", 2, "11")], 18, labw=330), cls="grow", style="font-size:26px"),
          col(call("Logging and monitoring did not move: it leads the roadmap.", "amber", b=3),
              call("All eight sprint items verified. No new failures.", "green", b=4), gap=24, style="width:620px"))),
  ["The final picture: sixty two failures down to thirty eight. Critical fell from three to one, and high from fifteen to five.",
   "Identity and access fell from eighteen to eight, storage from six to four, and networking from fourteen to eleven.",
   "Logging and monitoring did not move, twenty five findings, which is why it leads the roadmap.",
   "All eight sprint items are verified fixed, and the scanner reports no new failures."])

# ---------------------------------------------------------------- 23 reporting
S("Day 10", "Report, risks and roadmap",
  col(
      raw(chip("Final report", "teal", 1) + chip("Hardening roadmap", "teal", 1) + chip("Slide deck", "teal", 1) + chip("Framework mapping", "teal", 1), b=1),
      row(card("Accepted", "Suppressed with a compensating control.", "green", "FaCheckCircle", b=2, cls="grow"),
          card("Deferred", "Open, with an owner and a reason.", "amber", "FaClock", b=2, cls="grow"),
          card("Temporary", "Ends at teardown or by choice.", "red", "FaHourglassHalf", b=2, cls="grow")),
      steps([("1", "Next 30 days", "Close the logging gap", "red"), ("2", "30 to 90 days", "Harden the platform", "amber"), ("3", "Beyond", "Scan in the pipeline", "green")], b0=3, each=0)),
  ["Day ten is communication. The final report covers method, results, framework mapping, and what was learned.",
   "Accepted risks are suppressed with a compensating control. Deferred items stay open with an owner. Temporary ones end at teardown.",
   "The hardening roadmap sequences the rest: phase one closes the logging gap, phase two hardens the platform, and phase three automates scanning in the pipeline."])

# ---------------------------------------------------------------- 24 teardown
S("Day 10", "Tearing it down safely",
  row(col(card("The trap", "The S3 block and password policy shared the sandbox's Terraform state. A plain destroy would delete two real fixes.", "red", b=1),
          call("First destroy attempt blocked: admin rights were already removed. A destroy needs the rights of the build.", "amber", b=3), gap=26, cls="grow"),
      col(raw(term([("$ terraform state rm \\", "p", 2), ("    aws_s3_account_public_access_block.account \\", "p", 2),
                    ("    aws_iam_account_password_policy.strict", "p", 2), ("", "", 4), ("$ terraform plan -destroy", "p", 4),
                    ("Plan: 0 to add, 0 to change, 20 to destroy.", "ok", 4)]), b=2),
          card("Verified by the read-only scanner", "", "green", b=5, items=["VPC, buckets, trail, role: gone", "KMS key: pending deletion", "S3 block: still on", "Password policy: still set"]),
          gap=26, style="width:980px")),
  ["Then comes cleanup, and it needs care. The account wide S three block and the password policy shared the sandbox's Terraform state.",
   "A plain destroy would have deleted two real fixes, so they were removed from state first, a local edit that touches nothing in AWS.",
   "The first attempt at destroy was blocked, because administrator rights had already been removed. A destroy needs the same rights as the build.",
   "With the rights restored, the plan listed exactly twenty resources, and none of the two we protected.",
   "After the destroy, the read only scanner confirmed everything was gone, the key scheduled for deletion, and the real hardening still in place."])

# ---------------------------------------------------------------- 25 version control
S("Evidence", "Every day is a commit",
  row(raw(term([("e0c311d  Day 10: sandbox teardown", "", 1), ("6574214  Final verification: 62 to 38", "", 1),
                ("0fc91ae  Day 10: report, roadmap, deck", "", 1), ("6042191  Day 9: verification re-scan", "", 1),
                ("05c2bf5  Day 8: remediation sprint", "", 1), ("4dc156b  Day 7: remediation backlog", "", 1),
                ("f8def2c  Day 6: false-positive register", "", 1), ("82b2b69  Day 5: triage", "", 1),
                ("c660af1  Day 4: ScoutSuite", "", 1), ("512e099  Day 3: baseline v2", "", 1),
                ("d0ab078  Day 1-2: sandbox", "", 1)], style="height:100%"), cls="grow"),
      col(raw(term([("evidence/baseline-v2/", "p", 2), ("  results.csv  results.html  results.json", "", 2), ("  SHA256SUMS      <- hashed", "ok", 2),
                    ("  (files made read-only)", "c", 2)]), b=2),
          call("History is reconstructed honestly: real dates, labelled by day, never backdated.", "amber", b=3), gap=26, style="width:860px")),
  ["The whole engagement is committed to a private Git repository, one commit per day, with tags on the evidence.",
   "Raw scan results are hashed and made read only, so the baseline cannot quietly change.",
   "The history is reconstructed honestly: commits carry real dates, labelled by day, not backdated."])

# ---------------------------------------------------------------- 26 challenges recap
chal = [("Wrong default profile", "Verify the identity before every scan"), ("Builder had no rights", "A separate admin identity"),
        ("Baseline missed security groups", "Pin the flags, not only the version"), ("ScoutSuite crashed on new Python", "An event-loop wrapper"),
        ("Prowler per-port gap", "A second tool"), ("Terraform ignored removed blocks", "Explicit empty lists"),
        ("Stale credential report", "Wait four hours, trust direct evidence"), ("Destroy would undo real fixes", "Remove them from state first")]
S("Recap", "Eight challenges, eight solutions",
  table(["Challenge", "Solution"], [([f'<span class="t-red">{a}</span>', f'<span class="t-green">{b}</span>'], i + 2) for i, (a, b) in enumerate(chal)],
        widths=["800px", "900px"]),
  ["Let us recap the challenges.",
   "First, the wrong default profile: verify the identity before every scan.",
   "Second, the builder had no rights: use a separate administrative identity.",
   "Third, the baseline missed security groups: pin the flags, not only the version.",
   "Fourth, ScoutSuite crashed on a new Python: an event loop wrapper fixed it.",
   "Fifth, a gap in Prowler's per port checks: a second tool caught it.",
   "Sixth, Terraform ignored removed rule blocks: use explicit empty lists.",
   "Seventh, the stale credential report: wait four hours, and trust direct evidence meanwhile.",
   "Eighth, a destroy that would undo real fixes: remove them from state first."])

# ---------------------------------------------------------------- 27 lessons
less = [("Severity is not priority", "Weigh exposure, exploitability and blast radius in context.", "FaBalanceScale", "teal"),
        ("Run two tools", "A pass from one is not proof. Verify the rules.", "FaSearch", "teal"),
        ("Pin flags, not just versions", "Otherwise comparisons mislead.", "FaFlag", "amber"),
        ("Plan, apply, verify", "Read the plan. Check the live account after.", "FaClipboardCheck", "amber"),
        ("Separate identities", "The builder never scans. The scanner never builds.", "FaUserShield", "green"),
        ("Suppress with reasons", "Every mute is justified and auditable.", "FaFileAlt", "green"),
        ("Protect the evidence", "Hash it, make it read-only, commit it.", "FaGitAlt", "purple"),
        ("Fix in code", "A console-only fix is undone by the next apply.", "FaCode", "purple")]
S("Recap", "Eight lessons to keep",
  col(row(*[card(t, d, c, ic_, b=2 + i // 2, cls="grow") for i, (t, d, ic_, c) in enumerate(less[:4])]),
      row(*[card(t, d, c, ic_, b=2 + (i + 4) // 2, cls="grow") for i, (t, d, ic_, c) in enumerate(less[4:])])),
  ["Here are eight lessons to keep.",
   "Severity is not priority, so weigh exposure, exploitability and blast radius in context. And run two tools, because a pass from one is not proof.",
   "Pin the flags, not just the versions, or comparisons mislead. And plan, apply, then verify against the live account.",
   "Keep identities separate: the builder never scans, and the scanner never builds. Suppress only with written reasons.",
   "Protect the evidence by hashing it and committing it. And fix things in code, because a console only fix is undone by the next apply."])

# ---------------------------------------------------------------- 28 closing
S("Your turn", "How to repeat this",
  col(
      steps([("1", "Pin", "One benchmark version", "teal"), ("2", "Scan", "Read-only identity", "green"), ("3", "Triage", "By real risk", "amber"),
             ("4", "Fix", "Through code", "purple"), ("5", "Re-scan", "Identical flags", "teal"), ("6", "Report", "And tear down", "green")], b0=1, each=0),
      raw(chip("Quarterly full scan", "teal", 2) + chip("Monthly identity scan", "teal", 2) + chip("Re-scan after change", "teal", 2) + chip("Re-justify every mute", "amber", 2), b=2),
      call("Scanning is the easy part. The value is in triage, tuning and remediation.", "teal", b=3, style="font-size:40px;text-align:center;padding:40px")),
  ["To repeat this on your own account, pin the benchmark, create a read only scanner, scan, triage, fix through code, and re scan with identical flags.",
   "Retest quarterly with identical flags, and re justify every muted finding.",
   "And remember: scanning is the easy part. The value is in triage, tuning, and remediation. Thanks for watching."])
