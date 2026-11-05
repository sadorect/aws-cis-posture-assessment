# ---------------------------------------------------------------------------
# LOGGING & ENCRYPTION — intentionally misconfigured
# Findings:
#  L1. CloudTrail exists but is single-region (CIS 3.1)
#  L2. CloudTrail log file validation disabled (CIS 3.2)
#  L3. CloudTrail not encrypted with a KMS key / not sent to CloudWatch Logs
#  L4. Trail bucket has no access logging, versioning or default CMK encryption
#  L5. Customer-managed KMS key with automatic rotation disabled (CIS 3.6/3.8)
# ---------------------------------------------------------------------------

data "aws_partition" "current" {}

# L5: CMK with rotation explicitly off
resource "aws_kms_key" "no_rotation" {
  description         = "Sandbox CMK with automatic rotation disabled"
  enable_key_rotation = false
}

resource "aws_s3_bucket" "trail" {
  bucket        = "${var.name_prefix}-trail-${random_id.bucket_suffix.hex}"
  force_destroy = var.allow_destroy_s3

  tags = {
    Name = "${var.name_prefix}-trail"
  }
}

resource "aws_s3_bucket_policy" "trail" {
  bucket = aws_s3_bucket.trail.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AWSCloudTrailAclCheck"
        Effect    = "Allow"
        Principal = { Service = "cloudtrail.amazonaws.com" }
        Action    = "s3:GetBucketAcl"
        Resource  = aws_s3_bucket.trail.arn
      },
      {
        Sid       = "AWSCloudTrailWrite"
        Effect    = "Allow"
        Principal = { Service = "cloudtrail.amazonaws.com" }
        Action    = "s3:PutObject"
        Resource  = "${aws_s3_bucket.trail.arn}/AWSLogs/${data.aws_caller_identity.current.account_id}/*"
        Condition = { StringEquals = { "s3:x-amz-acl" = "bucket-owner-full-control" } }
      }
    ]
  })
}

# L1/L2/L3: single-region trail, no log validation, no KMS, no CloudWatch
resource "aws_cloudtrail" "weak" {
  name                          = "${var.name_prefix}-trail"
  s3_bucket_name                = aws_s3_bucket.trail.id
  is_multi_region_trail         = false
  enable_log_file_validation    = false
  include_global_service_events = true

  depends_on = [aws_s3_bucket_policy.trail]
}
