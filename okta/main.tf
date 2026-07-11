# Phase 1 starter resources. Expand incrementally: add groups, wire real app
# assignments once you've created a test app in the Okta admin console, add
# group rules. Small, reviewable commits are the point of this exercise.

resource "okta_group" "it_engineering" {
  name        = "IT-Engineering"
  description = "Engineering team members, managed via Terraform"
}

resource "okta_group" "it_admins" {
  name        = "IT-Admins"
  description = "IT administrators, managed via Terraform"
}

# Example of a group-based app assignment. Apps themselves aren't created by
# this module (that requires more setup than a starter project needs); this
# manages assignments against an app you've already created manually in the
# Okta admin console for testing.
#
# resource "okta_app_group_assignment" "example" {
#   app_id   = var.example_app_id
#   group_id = okta_group.it_engineering.id
# }
