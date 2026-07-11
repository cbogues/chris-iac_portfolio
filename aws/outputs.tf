output "vpc_id" {
  value = aws_vpc.main.id
}

output "public_subnet_id" {
  value = aws_subnet.public.id
}

output "private_subnet_id" {
  value = aws_subnet.private.id
}

output "auditor_role_arn" {
  value = aws_iam_role.auditor.arn
}

output "cloudtrail_bucket" {
  value = aws_s3_bucket.cloudtrail_logs.id
}
