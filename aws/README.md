# Phase 2: AWS IAM + VPC (Terraform)

Baseline scope for this phase (remote backend migration is a stretch goal, not included here). See repo root README for the stretch goal list.

## Prerequisites

- An AWS account (free tier is enough). If you don't already have a personal one, separate from any employer account: https://aws.amazon.com/free/
- An IAM user or role with credentials configured locally, either via `aws configure` (AWS CLI) or `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` env vars. Do not use root account credentials for this, create an IAM user with programmatic access.
- Terraform CLI >= 1.5.0 (same as Phase 1).
- Your current public IP, for the SSH security group rule: `curl https://checkip.amazonaws.com`.

## Steps

1. Set your variables (env vars, not a committed file):
   ```bash
   export TF_VAR_my_ip_cidr="$(curl -s https://checkip.amazonaws.com)/32"
   ```
2. From the `aws/` directory:
   ```bash
   terraform init
   terraform fmt -check
   terraform validate
   terraform plan
   ```
3. Read the plan. Confirm it shows: one VPC, two subnets (public/private), one internet gateway, one route table, one security group, one IAM role, one S3 bucket, one CloudTrail trail. Nothing else.
4. Apply:
   ```bash
   terraform apply
   ```

## Expected output

`terraform apply` finishes with 5 outputs: `vpc_id`, `public_subnet_id`, `private_subnet_id`, `auditor_role_arn`, `cloudtrail_bucket`. Confirm the CloudTrail trail shows "Logging" as On in the AWS Console (CloudTrail > Trails).

## Rollback

```bash
terraform destroy
```
Do this before your vacation ends regardless of whether you keep building. Nothing here should be a large bill on free tier, but there's no reason to leave it running once you've captured screenshots for your README/portfolio notes.

## Edge cases

- **No NAT gateway on purpose.** The private subnet has no internet egress. This keeps the module free-tier-safe (NAT gateways bill hourly plus data processing charges). If you want to demonstrate a NAT gateway later, add it as a clearly-labeled addition and note the cost tradeoff in your README, don't add it silently.
- **CloudTrail is management-events-only, single-region.** This is the free tier. Enabling data events (S3 object-level, Lambda) or multi-region costs money, don't turn those on for this exercise.
- **`ReadOnlyAccess` managed policy is a starting point, not the end state.** A real least-privilege review would scope this to a narrower custom policy. If you have extra time, swap the managed policy attachment for a custom `aws_iam_policy` scoped to 2-3 services and note in your README why you narrowed it, that's a stronger interview story than the AWS-managed policy alone.
- **Bucket name collisions.** S3 bucket names are globally unique. The bucket name here includes your account ID to avoid collisions, if `terraform apply` still fails on the bucket name, check you don't already have a bucket with that exact name in another region.
