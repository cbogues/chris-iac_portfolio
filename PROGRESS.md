# Progress: chris-iac-portfolio
Author: Chris Bogues
Last updated: 2026-07-12

Baseline scope. Stretch goals are tracked separately at the bottom, don't start them until the baseline for that phase is done.

## Phase 1: Okta (days 1-2)
- [x] Free Okta org created (Integrator Free Plan)
- [x] `okta` Terraform provider configured, credentials set as env vars
- [x] `terraform init` / `plan` / `apply` run successfully for `it_engineering` + `it_admins` groups (2026-07-10)
- [x] GitHub Actions secrets set (`OKTA_ORG_NAME`, `OKTA_BASE_URL`, `OKTA_API_TOKEN`)
- [x] CI plan-on-PR workflow verified working (PR #1, `Terraform Okta Plan` check passed, 2026-07-10)
- [x] Diagnosed and fixed CI auto-apply failure (2026-07-11): CI had no access to local `terraform.tfstate`, tried to recreate `it_engineering`/`it_admins` and got "already exists" from the Okta API. Reconciled with `terraform import okta_group.it_test`, removed the auto-apply job from CI until the remote backend stretch goal exists. See `okta/README.md` CI section.
- [x] `okta/README.md` screenshots/notes added (2026-07-11)

## Phase 2: AWS (days 3-5)
- [x] Personal AWS account set up (IAM user `iac-portfolio-admin`, MFA enabled, not root credentials)
- [x] `my_ip_cidr` set, `terraform plan` reviewed (14 to add, 0 to change, 0 to destroy)
- [x] `terraform apply` run: VPC, subnets, security group, IAM auditor role, CloudTrail (2026-07-12, 14 resources, 0 errors)
- [x] CloudTrail confirmed "Logging: On" in AWS Console (2026-07-12)
- [x] `aws/README.md` screenshots/notes added (2026-07-12)

## Phase 3: Agent (days 6-8)
- [x] Day 6: `explain_plan()` tested standalone against `sample_plan.json` (2026-07-12)
- [x] Day 7: `claude_agent.py` tool-calling loop implemented (the TODO filled in) (2026-07-12)
- [x] Day 7: `python claude_agent.py` returns a correct natural-language summary (2026-07-12, correctly named actual resources, two-call tool loop confirmed via HTTP logs)
- [x] Day 8: tested against a real plan generated from Phase 1 or 2 (2026-07-12, real Okta `terraform plan` correctly reported as no-op)
- [x] Day 8: prompt tuned so it reliably calls the tool instead of guessing (2026-07-12, correctly distinguished a 3-change plan from a 0-change plan across two tests, no tuning needed beyond the initial schema)

## Phase 4: SCIM server (promoted from stretch goal 3, 2026-07-12)

Promoted from a standalone follow-on to a full phase because it genuinely integrates with Phases 1 and 2 (provisioned from the real Okta org, optionally deployable to the AWS infra) instead of standing alone.

- [x] Local venv set up, `pip install -r requirements.txt`, `.env` token generated (2026-07-16)
- [x] `pytest` passing (6 tests: auth, create, duplicate rejection, filter lookup, PATCH-deactivate, group membership) (2026-07-16)
- [ ] Server sanity-checked locally with `curl`
- [ ] `ngrok` tunnel live, Okta SCIM test app configured and "Test API Credentials" passing
- [ ] Real user provisioned from Okta, confirmed on the server side
- [ ] Real deactivation (PATCH) triggered from Okta, confirmed on the server side
- [ ] Group membership push from Okta confirmed
- [ ] `scim/README.md` evidence/screenshots added

## Polish
- [ ] Root README status line updated to reflect what's actually built
- [ ] Architecture note added tying all four phases together
- [ ] Resume bullets drafted (see the 4 draft bullets in `_OUTPUTS/20260709_vacation_portfolio_projects.md`, plus a new one for the SCIM phase), `[QUANTIFY]` placeholders filled in with real numbers
- [x] Repo pushed to GitHub / made public (2026-07-10, ahead of schedule via `gh repo create`)

## Stretch goals (only if ahead of schedule, in this priority order)
- [ ] 1. Remote backend: bootstrap S3 + DynamoDB, migrate both Okta and AWS module state to it
- [ ] 2. `explain-resource` MCP tool added to the agent
- [ ] 3. Deploy the SCIM server to Phase 2's AWS infra instead of `ngrok` (requires real TLS termination and a new security group rule, see `scim/README.md` edge cases)
