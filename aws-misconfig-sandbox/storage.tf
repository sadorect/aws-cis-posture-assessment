# ---------------------------------------------------------------------------
# STORAGE — intentionally misconfigured
# Findings:
#  S1. S3 bucket has Block Public Access fully disabled
#  S2. S3 bucket policy grants Principal "*" s3:GetObject
#  S3. S3 bucket ACL set to public-read
#  S4. No default encryption (SSE) configured on the bucket
#  S5. No versioning enabled (ransomware/accidental-delete exposure)
#  S6. No access logging / no object-lock
#  S7. Unencrypted, publicly-exposed-by-SG EBS volume attached conceptually
#      via the wide-open security group (see networking.tf) with no KMS key
# ---------------------------------------------------------------------------

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "public_data" {
  bucket        = "${var.name_prefix}-public-data-${random_id.bucket_suffix.hex}"
  force_destroy = var.allow_destroy_s3

  tags = {
    Name = "${var.name_prefix}-public-data"
  }
}

# S1 [REMEDIATED Day 8, B04]: Block Public Access enabled on every setting
resource "aws_s3_bucket_public_access_block" "public_data" {
  bucket = aws_s3_bucket.public_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 [REMEDIATED Day 8, B04]: bucket ACL reset to private
resource "aws_s3_bucket_ownership_controls" "public_data" {
  bucket = aws_s3_bucket.public_data.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "public_data" {
  bucket = aws_s3_bucket.public_data.id
  acl    = "private"

  depends_on = [
    aws_s3_bucket_ownership_controls.public_data,
    aws_s3_bucket_public_access_block.public_data,
  ]
}

# S2 [REMEDIATED Day 8, B04]: the anonymous-read bucket policy was deleted.

# S4: no aws_s3_bucket_server_side_encryption_configuration resource declared
# S5: no aws_s3_bucket_versioning resource declared
# S6: no aws_s3_bucket_logging resource declared

# S7: unencrypted EBS volume, no KMS key, sitting in a public subnet reachable
# through the wide-open security group defined in networking.tf
resource "aws_ebs_volume" "unencrypted" {
  availability_zone = "${var.aws_region}a"
  size              = 8
  encrypted         = false

  tags = {
    Name = "${var.name_prefix}-unencrypted-volume"
  }
}

# B06 [Day 8]: account-level Block Public Access, so no bucket in the account can be
# made public by mistake. Baseline had no account-level setting (CIS 2.1.4).
resource "aws_s3_account_public_access_block" "account" {
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
