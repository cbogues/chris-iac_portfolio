variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Short name used to tag/prefix all resources"
  type        = string
  default     = "iac-portfolio"
}

variable "my_ip_cidr" {
  description = "Your current public IP in CIDR form (e.g. \"203.0.113.4/32\"), used to scope the SSH security group rule to just you. Find yours at https://checkip.amazonaws.com then append /32."
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.20.0.0/16"
}
