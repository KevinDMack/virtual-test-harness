# ---------------------------------------------------------------------------
# outputs.tf – Root-level outputs surfaced after a successful apply.
# ---------------------------------------------------------------------------

output "resource_group_name" {
  description = "Name of the resource group that holds all resources."
  value       = azurerm_resource_group.main.name
}

output "aks_name" {
  description = "Name of the AKS cluster."
  value       = module.aks.name
}

output "aks_oidc_issuer_url" {
  description = "OIDC issuer URL for the AKS cluster (used for workload identity federation)."
  value       = module.aks.oidc_issuer_url
}

output "acr_login_server" {
  description = "Login server hostname for the Container Registry."
  value       = module.acr.login_server
}

output "keyvault_uri" {
  description = "URI of the Key Vault."
  value       = module.keyvault.uri
}

output "storage_account_name" {
  description = "Name of the storage account."
  value       = module.storage.name
}

output "storage_primary_blob_endpoint" {
  description = "Primary blob service endpoint for the storage account."
  value       = module.storage.primary_blob_endpoint
}
