# chris-iac-portfolio

Personal infrastructure-as-code portfolio. Three phases, each building on the last:

```
Phase 1: okta/    Terraform-managed Okta identity resources (groups, app assignments)
Phase 2: aws/     Terraform-managed AWS IAM + VPC baseline
Phase 3: agent/   Claude + MCP agent that reads this repo's Terraform and explains it
```

Status: **All three phases scaffolded, none started.** Each has a runnable starting point plus a guided README (Prerequisites, Steps, Expected Output, Rollback, Edge Cases) so you're following a checklist, not staring at a blank file.

## Why this repo exists

Built to get hands-on, shippable reps with Terraform, AWS, and Claude/MCP tool-calling, three gaps identified against target job postings that weren't covered by prior identity/endpoint/compliance work. Each phase is small enough to finish in a few focused days and produces a real, working artifact rather than a tutorial follow-along.

## Prerequisites

- [Terraform CLI](https://developer.hashicorp.com/terraform/install) >= 1.5.0
- A free [Okta Developer Edition](https://developer.okta.com/signup/) org (separate from any employer Okta org)
- A personal AWS account, free tier (separate from any employer account)
- Python 3.10+ and an Anthropic API key, for Phase 3
- A GitHub repo with Actions enabled, and three Okta repository secrets: `OKTA_ORG_NAME`, `OKTA_BASE_URL`, `OKTA_API_TOKEN`
- Never commit real credentials. `.tfvars`, `.tfstate`, and `.env` files are gitignored.

## 9-day guided plan (baseline scope, remote backend + explain-resource are stretch goals)

| Day | Phase | Do this | Guide |
|---|---|---|---|
| 1-2 | Okta | Dev org, provider setup, manage 2 groups as HCL, CI plan-on-PR | [`okta/README.md`](okta/README.md) |
| 3-5 | AWS | Account setup, IAM role, VPC/subnets/security group, CloudTrail | [`aws/README.md`](aws/README.md) |
| 6 | Agent | Get `explain_plan` working standalone against `sample_plan.json` | [`agent/README.md`](agent/README.md), Day 6 section |
| 7 | Agent | Wire Claude tool-calling in `claude_agent.py` (the TODO stub) | [`agent/README.md`](agent/README.md), Day 7 section |
| 8 | Agent | Test against a real plan from Phase 1/2, tune | [`agent/README.md`](agent/README.md), Day 8 section |
| 9 | Polish | Update this README's status, screenshots, resume bullets, publish | — |

Each phase README follows the same structure: Prerequisites, Steps (numbered), Expected Output (so you know when you're actually done, not just "it ran"), Rollback, and Edge Cases (the specific things likely to trip you up, called out in advance instead of discovered mid-debug).

## Phase 1: Okta

See [`okta/README.md`](okta/README.md).

Goal: manage a handful of Okta groups and app-group assignments as version-controlled HCL, with `terraform plan` running automatically on every pull request via GitHub Actions. Apply runs locally (not from CI) until a remote backend gives CI the same state your laptop has, see `okta/README.md`'s CI section for why.

## Phase 2: AWS

See [`aws/README.md`](aws/README.md).

Goal: least-privilege IAM role, a VPC with public/private subnets and a scoped security group, and CloudTrail logging to S3 (management events only, free tier), provisioned via Terraform.

## Phase 3: Agent

See [`agent/README.md`](agent/README.md).

Goal: an MCP server exposing an `explain_plan` tool that reads `terraform plan` JSON output and produces a plain-English summary, wired to Claude via tool-calling in `claude_agent.py`.

## License

MIT. Use whatever's useful.
