output "it_engineering_group_id" {
  description = "Object ID of the IT-Engineering group"
  value       = okta_group.it_engineering.id
}

output "it_admins_group_id" {
  description = "Object ID of the IT-Admins group"
  value       = okta_group.it_admins.id
}
