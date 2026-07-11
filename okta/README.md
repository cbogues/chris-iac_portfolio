# Phase 1: Okta (Terraform)

Manages Okta groups and app-group assignments as version-controlled HCL against a free Okta Developer Edition org.

## Setup

1. **Create a free Okta Developer org**: https://developer.okta.com/signup/ (a few minutes, no cost, fully separate from any employer Okta org).
2. **Generate an API token**: in the Okta admin console, go to Security > API > Tokens > Create Token. Copy it, you won't see it again.
3. **Set credentials locally** (never put these in a committed file):
   ```bash
   export TF_VAR_okta_org_name="dev-12345678"     # the subdomain before .okta.com
   export TF_VAR_okta_base_url="okta.com"          # developer orgs use okta.com, not oktapreview.com
   export TF_VAR_okta_api_token="00abc..."          # the token from step 2
   ```
4. **Initialize and review**:
   ```bash
   cd okta
   terraform init
   terraform fmt -check
   terraform validate
   terraform plan
   ```
5. Read the plan output before applying anything. `terraform plan` is always safe, it makes no changes. `terraform apply` does.
6. Once the plan looks right:
   ```bash
   terraform apply
   ```

## What this manages

- `okta_group.it_engineering` and `okta_group.it_admins`: two example groups.
- A commented-out example of an `okta_app_group_assignment`, for once you've created a test app in the Okta admin console to assign a group to (apps themselves aren't created here; this project starts with managing assignments against existing apps, not app creation).

Expand this incrementally: add more groups, wire up real app assignments, add group rules. Small, reviewable commits are the point, not managing everything on day one.

## CI

`.github/workflows/terraform-okta.yml` (repo root) runs `terraform fmt -check`, `terraform validate`, and `terraform plan` on every pull request that touches `okta/**`, and `terraform apply` on merges to `main`. It needs four repository secrets set in GitHub (Settings > Secrets and variables > Actions): `OKTA_ORG_NAME`, `OKTA_BASE_URL`, `OKTA_API_TOKEN`.

## Rollback

Terraform is declarative: to remove a resource, delete it from the `.tf` file and run `terraform plan` to confirm it shows as a destroy, then `terraform apply`. To tear down everything this module manages:
```bash
terraform destroy
```

## State

This phase uses local state (`terraform.tfstate` in this directory, gitignored). Phase 2 introduces a remote backend that both this module and the AWS module will migrate to, if you reach that stretch goal.
