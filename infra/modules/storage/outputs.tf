# ---------------------------------------------------------------------------
# modules/storage/outputs.tf – Values exported by the Storage Account module.
# ---------------------------------------------------------------------------

output "id" {
  description = "Resource ID of the storage account."
  value       = azurerm_storage_account.main.id
}

output "name" {
  description = "Name of the storage account."
  value       = azurerm_storage_account.main.name
}

output "primary_blob_endpoint" {
  description = "Primary blob service endpoint URL."
  value       = azurerm_storage_account.main.primary_blob_endpoint
}
