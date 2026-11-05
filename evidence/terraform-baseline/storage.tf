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

# S1: Block Public Access explicitly disabled on every setting
resource "aws_s3_bucket_public_access_block" "public_data" {
  bucket = aws_s3_bucket.public_data.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# S3: bucket ACL set to public-read
resource "aws_s3_bucket_ownership_controls" "public_data" {
  bucket = aws_s3_bucket.public_data.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "public_data" {
  bucket = aws_s3_bucket.public_data.id
  acl    = "public-read"

  depends_on = [
    aws_s3_bucket_ownership_controls.public_data,
    aws_s3_bucket_public_access_block.public_data,
  ]
}

# S2: bucket policy allows anonymous read
resource "aws_s3_bucket_policy" "public_data" {
  bucket = aws_s3_bucket.public_data.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicRead"
        Effect    = "Allow"
        Principal = "*"
        Action    = ["s3:GetObject"]
        Resource  = "${aws_s3_bucket.public_data.arn}/*"
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.public_data]
}

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
