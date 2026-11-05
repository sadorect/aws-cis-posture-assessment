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

# I1: wildcard managed policy
resource "aws_iam_policy" "admin_wildcard" {
  name        = "${var.name_prefix}-admin-wildcard"
  description = "Deliberately over-permissive policy for sandbox findings"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "FullAdmin"
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })
}

# I2/I3: standing IAM user with wildcard access and a static access key
resource "aws_iam_user" "sandbox_admin" {
  name = "${var.name_prefix}-admin-user"
  path = "/"
}

resource "aws_iam_user_policy_attachment" "sandbox_admin_attach" {
  user       = aws_iam_user.sandbox_admin.name
  policy_arn = aws_iam_policy.admin_wildcard.arn
}

# I2: redundant inline wildcard policy on top of the managed one
resource "aws_iam_user_policy" "inline_wildcard" {
  name = "${var.name_prefix}-inline-wildcard"
  user = aws_iam_user.sandbox_admin.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })
}

# I3: long-lived access key, never rotated, no last-used monitoring configured
resource "aws_iam_access_key" "sandbox_admin_key" {
  user = aws_iam_user.sandbox_admin.name
}

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

# I4: account password policy intentionally left at AWS defaults —
# no aws_iam_account_password_policy resource is declared, so minimum
# length / rotation / reuse-prevention / MFA are not enforced by IaC.
