terraform {
  required_version = ">= 1.5.0"

  required_providers {
    okta = {
      source  = "okta/okta"
      version = "~> 4.0"
    }
  }

  # Local state for now. Migrating to a remote backend (S3 + DynamoDB, provisioned
  # in the aws/ module) is a stretch goal once Phase 2 is built.
}

provider "okta" {
  org_name  = var.okta_org_name
  base_url  = var.okta_base_url
  api_token = var.okta_api_token
}
