# ---------------------------------------------------------------------------
# IAM — intentionally misconfigured
# Findings:
#  I1. Customer-managed policy grants Action="*" Resource="*" (full admin)
#  I2. IAM user has that policy attached AND an inline policy, both wildcard
#  I3. IAM user has an access key created (long-lived credential, no rotation)
#  I4. No MFA enforced / no password policy resource managing complexity or age
#  I5. IAM role trusts the whole account root (no MFA / external ID condition)
#  I6. Role has PassRole + AdministratorAccess with no condition keys
#  I7. S3 bucket policy (see storage.tf) is referenced by a role with "*" principal
# ---------------------------------------------------------------------------

data "aws_caller_identity" "current" {}

# I1/I2/I3 [REMEDIATED Day 8, B03]: the wildcard managed policy, the inline wildcard policy,
# the IAM user and its static access key were deleted. Nothing used them.

# I5/I6: role assumable by any principal in this account, carrying admin rights
resource "aws_iam_role" "overly_permissive" {
  name = "${var.name_prefix}-account-admin-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root" }
        Action    = "sts:AssumeRole"
        # Scoped to this account only (the account is shared with real identities),
        # but still no MFA / external ID condition and the role carries full admin
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "overly_permissive_admin" {
  role       = aws_iam_role.overly_permissive.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

# I4 [REMEDIATED Day 8, B16]: account password policy (CIS 1.8, 1.9).
# No forced expiry (max_password_age = 0): current NIST SP 800-63B guidance advises against it.
resource "aws_iam_account_password_policy" "strict" {
  minimum_password_length        = 14
  password_reuse_prevention      = 24
  require_lowercase_characters   = true
  require_uppercase_characters   = true
  require_numbers                = true
  require_symbols                = true
  allow_users_to_change_password = true
  max_password_age               = 0
}
