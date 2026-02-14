output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "aks_cluster_name" {
  description = "Name of the AKS cluster"
  value       = azurerm_kubernetes_cluster.main.name
}

output "aks_kube_config" {
  description = "Kubernetes configuration for kubectl"
  value       = azurerm_kubernetes_cluster.main.kube_config_raw
  sensitive   = true
}

output "ai_foundry_endpoint" {
  description = "Endpoint for the AI Foundry service"
  value       = azurerm_cognitive_account.main.endpoint
}

output "ai_foundry_key" {
  description = "Primary access key for AI Foundry"
  value       = azurerm_cognitive_account.main.primary_access_key
  sensitive   = true
}

output "application_insights_connection_string" {
  description = "Connection string for Application Insights"
  value       = azurerm_application_insights.main.connection_string
  sensitive   = true
}
