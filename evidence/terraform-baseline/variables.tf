variable "aws_region" {
  description = "AWS region to deploy the sandbox into"
  type        = string
  default     = "eu-west-2"
}

variable "name_prefix" {
  description = "Prefix applied to all resource names"
  type        = string
  default     = "misconfig-sandbox"
}

variable "vpc_cidr" {
  description = "CIDR block for the sandbox VPC"
  type        = string
  default     = "10.90.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR block for the public subnet"
  type        = string
  default     = "10.90.1.0/24"
}

variable "allow_destroy_s3" {
  description = "Allow terraform destroy to delete non-empty buckets (sandbox convenience)"
  type        = bool
  default     = true
}
