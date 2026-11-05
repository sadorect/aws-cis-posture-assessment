output "vpc_id" {
  value = aws_vpc.sandbox.id
}

output "wide_open_security_group_id" {
  value = aws_security_group.wide_open.id
}

output "public_bucket_name" {
  value = aws_s3_bucket.public_data.bucket
}

output "sandbox_admin_access_key_id" {
  value     = aws_iam_access_key.sandbox_admin_key.id
  sensitive = true
}

output "sandbox_admin_secret_access_key" {
  value     = aws_iam_access_key.sandbox_admin_key.secret
  sensitive = true
}

output "account_admin_role_arn" {
  value = aws_iam_role.overly_permissive.arn
}
