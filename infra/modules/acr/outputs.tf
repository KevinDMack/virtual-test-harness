# ---------------------------------------------------------------------------
# modules/acr/outputs.tf – Values exported by the Container Registry module.
# ---------------------------------------------------------------------------

output "id" {
  description = "Resource ID of the Container Registry."
  value       = azurerm_container_registry.main.id
}

output "name" {
  description = "Name of the Container Registry."
  value       = azurerm_container_registry.main.name
}

output "login_server" {
  description = "Login server hostname (e.g. <name>.azurecr.us)."
  value       = azurerm_container_registry.main.login_server
}
