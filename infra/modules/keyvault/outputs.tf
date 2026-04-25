# ---------------------------------------------------------------------------
# modules/keyvault/outputs.tf – Values exported by the Key Vault module.
# ---------------------------------------------------------------------------

output "id" {
  description = "Resource ID of the Key Vault."
  value       = azurerm_key_vault.main.id
}

output "name" {
  description = "Name of the Key Vault."
  value       = azurerm_key_vault.main.name
}

output "uri" {
  description = "Vault URI (e.g. https://<name>.vault.usgovcloudapi.net/)."
  value       = azurerm_key_vault.main.vault_uri
}
