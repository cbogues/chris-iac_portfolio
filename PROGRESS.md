# Progress: chris-iac-portfolio
Author: Chris Bogues
Last updated: 2026-07-10

Baseline scope. Stretch goals are tracked separately at the bottom, don't start them until the baseline for that phase is done.

## Phase 1: Okta (days 1-2)
- [x] Free Okta org created (Integrator Free Plan)
- [x] `okta` Terraform provider configured, credentials set as env vars
- [x] `terraform init` / `plan` / `apply` run successfully for `it_engineering` + `it_admins` groups (2026-07-10)
- [x] GitHub Actions secrets set (`OKTA_ORG_NAME`, `OKTA_BASE_URL`, `OKTA_API_TOKEN`)
- [x] CI plan-on-PR workflow verified working (PR #1, `Terraform Okta Plan` check passed, 2026-07-10)
- [ ] `okta/README.md` screenshots/notes added

## Phase 2: AWS (days 3-5)
- [ ] Personal AWS account set up (IAM user, not root credentials)
- [ ] `my_ip_cidr` set, `terraform plan` reviewed
- [ ] `terraform apply` run: VPC, subnets, security group, IAM auditor role, CloudTrail
- [ ] CloudTrail confirmed "Logging: On" in AWS Console
- [ ] `aws/README.md` screenshots/notes added

## Phase 3: Agent (days 6-8)
- [ ] Day 6: `explain_plan()` tested standalone against `sample_plan.json`
- [ ] Day 7: `claude_agent.py` tool-calling loop implemented (the TODO filled in)
- [ ] Day 7: `python claude_agent.py` returns a correct natural-language summary
- [ ] Day 8: tested against a real plan generated from Phase 1 or 2
- [ ] Day 8: prompt tuned so it reliably calls the tool instead of guessing

## Day 9: Polish
- [ ] Root README status line updated to reflect what's actually built
- [ ] Architecture note added tying the three phases together
- [ ] Resume bullets drafted (see the 4 draft bullets in `_OUTPUTS/20260709_vacation_portfolio_projects.md`), `[QUANTIFY]` placeholders filled in with real numbers
- [x] Repo pushed to GitHub / made public (2026-07-10, ahead of schedule via `gh repo create`)

## Stretch goals (only if ahead of schedule, in this priority order)
- [ ] 1. Remote backend: bootstrap S3 + DynamoDB, migrate both Okta and AWS module state to it
- [ ] 2. `explain-resource` MCP tool added to the agent
- [ ] 3. SCIM 2.0 server (separate follow-on project, doesn't live in this repo)
