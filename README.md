# chris-iac-portfolio

Personal infrastructure-as-code portfolio. Four phases, each building on the last:

```
Phase 1: okta/    Terraform-managed Okta identity resources (groups, app assignments)
Phase 2: aws/     Terraform-managed AWS IAM + VPC baseline
Phase 3: agent/   Claude + MCP agent that reads this repo's Terraform and explains it
Phase 4: scim/    SCIM 2.0 server, provisioned FROM the real Okta org in Phase 1
```

Status: **All four phases complete and verified**, built in 4 real days against a 9-day plan. See `PROGRESS.md` for the detailed checklist and dates. Each phase has a guided README (Prerequisites, Steps, Expected Output, Rollback, Edge Cases) so it's a checklist to follow, not a blank file to stare at.

## Why this repo exists

Built to get hands-on, shippable reps with Terraform, AWS, and Claude/MCP tool-calling, three gaps identified against target job postings that weren't covered by prior identity/endpoint/compliance work. Each phase is small enough to finish in a few focused days and produces a real, working artifact rather than a tutorial follow-along.

## Prerequisites

- [Terraform CLI](https://developer.hashicorp.com/terraform/install) >= 1.5.0
- A free [Okta Developer Edition](https://developer.okta.com/signup/) org (separate from any employer Okta org)
- A personal AWS account, free tier (separate from any employer account)
- Python 3.10+ and an Anthropic API key, for Phase 3
- [ngrok](https://ngrok.com/download) (free tier), for Phase 4
- A GitHub repo with Actions enabled, and three Okta repository secrets: `OKTA_ORG_NAME`, `OKTA_BASE_URL`, `OKTA_API_TOKEN`
- Never commit real credentials. `.tfvars`, `.tfstate`, and `.env` files are gitignored.

## Guided plan (baseline scope, remote backend + explain-resource are stretch goals)

Originally scoped as 9 days; Phases 1-3 ended up taking 3, see `PROGRESS.md` for the real timeline.

| Phase | Do this | Guide |
|---|---|---|
| 1: Okta | Dev org, provider setup, manage 2 groups as HCL, CI plan-on-PR | [`okta/README.md`](okta/README.md) |
| 2: AWS | Account setup, IAM role, VPC/subnets/security group, CloudTrail | [`aws/README.md`](aws/README.md) |
| 3: Agent | Get `explain_plan` working, then wire Claude tool-calling, then test against a real plan | [`agent/README.md`](agent/README.md) |
| 4: SCIM | Build + test locally, expose via ngrok, provision a real user from Okta | [`scim/README.md`](scim/README.md) |
| Polish | Update this README's status, screenshots, resume bullets, publish | — |

Each phase README follows the same structure: Prerequisites, Steps (numbered), Expected Output (so you know when you're actually done, not just "it ran"), Rollback, and Edge Cases (the specific things likely to trip you up, called out in advance instead of discovered mid-debug).

## Architecture

Not four disconnected exercises, one progression, each phase reusing or connecting to what came before:

```
Phase 1 (Okta)          Phase 2 (AWS)              Phase 3 (Agent)                Phase 4 (SCIM)
Terraform + one    -->  Terraform + a second  -->  Claude + MCP, reads      -->   FastAPI server,
identity provider,      provider (cloud IAM/       and explains the              provisioned FROM
local state, PR-only    networking), same IaC      terraform plan output         the real Okta org
CI (see below for       discipline extended         from Phases 1-2               in Phase 1, not
why apply stays          to a new domain                                          a mock IdP
local, not CI)
```

The connective tissue is real, not narrative dressing:

- **Phase 3 reads Phase 1 and 2's actual output.** `explain_plan` was tested against a real `terraform plan -json` generated from the `okta/` module, not just the bundled sample file.
- **Phase 4 is provisioned by the real Okta org from Phase 1.** The `IT-Admins` group created by Terraform in Phase 1 is the same group pushed through SCIM in Phase 4, visible in the Phase 4 evidence screenshots.
- **Phase 1's CI pipeline and Phase 4's Okta integration both surfaced real bugs**, documented rather than cleaned up: a state-drift issue when CI tried to apply without shared state (Phase 1), and an Okta form-field quirk plus a bearer-token double-prefix bug caught only by inspecting live request headers (Phase 4). Diagnosing and fixing both, with the evidence kept, is a better interview story than four clean runs.
- **Phase 4 is deployable onto Phase 2's AWS infra** as a documented (not required) next step, instead of the default `ngrok` tunnel.

Skill progression across the four phases: single-provider Terraform with local state, to multi-provider Terraform plus cloud networking/IAM, to an AI layer that operates on the infrastructure just built, to a protocol-level identity service that the very first phase's IdP actually talks to.

## Phase 1: Okta

See [`okta/README.md`](okta/README.md).

Goal: manage a handful of Okta groups and app-group assignments as version-controlled HCL, with `terraform plan` running automatically on every pull request via GitHub Actions. Apply runs locally (not from CI) until a remote backend gives CI the same state your laptop has, see `okta/README.md`'s CI section for why.

## Phase 2: AWS

See [`aws/README.md`](aws/README.md).

Goal: least-privilege IAM role, a VPC with public/private subnets and a scoped security group, and CloudTrail logging to S3 (management events only, free tier), provisioned via Terraform.

## Phase 3: Agent

See [`agent/README.md`](agent/README.md).

Goal: an MCP server exposing an `explain_plan` tool that reads `terraform plan` JSON output and produces a plain-English summary, wired to Claude via tool-calling in `claude_agent.py`.

## Phase 4: SCIM server

See [`scim/README.md`](scim/README.md).

Goal: a SCIM 2.0 server (FastAPI, RFC 7643/7644) provisioned FROM the real Okta org in Phase 1, not just tested with curl. Proves protocol-level identity understanding (SCIM create/PATCH-deactivate/group membership) instead of admin-console framing. Optionally deployable onto Phase 2's AWS infra instead of the default `ngrok` tunnel.

## License

MIT. Use whatever's useful.
