variable "okta_org_name" {
  description = "Okta org name: the subdomain before .okta.com (e.g. \"dev-12345678\" for a Developer Edition org)."
  type        = string
}

variable "okta_base_url" {
  description = "Okta base URL. Free Developer Edition orgs use \"okta.com\". Use \"oktapreview.com\" only if you're on a preview org."
  type        = string
  default     = "okta.com"
}

variable "okta_api_token" {
  description = "Okta API token (Security > API > Tokens in the admin console). Set via TF_VAR_okta_api_token env var, never in a committed file."
  type        = string
  sensitive   = true
}
