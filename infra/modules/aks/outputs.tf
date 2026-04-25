# ---------------------------------------------------------------------------
# modules/aks/outputs.tf – Values exported by the AKS module.
# ---------------------------------------------------------------------------

output "name" {
  description = "Name of the AKS cluster."
  value       = azurerm_kubernetes_cluster.main.name
}

output "id" {
  description = "Resource ID of the AKS cluster."
  value       = azurerm_kubernetes_cluster.main.id
}

output "identity_principal_id" {
  description = "Principal ID of the AKS system-assigned managed identity (control plane)."
  value       = azurerm_kubernetes_cluster.main.identity[0].principal_id
}

output "kubelet_identity_object_id" {
  description = "Object ID of the kubelet managed identity (used for ACR pulls)."
  value       = azurerm_kubernetes_cluster.main.kubelet_identity[0].object_id
}

output "oidc_issuer_url" {
  description = "OIDC issuer URL for workload identity federation."
  value       = azurerm_kubernetes_cluster.main.oidc_issuer_url
}

output "kube_config_raw" {
  description = "Raw kubeconfig for the cluster (sensitive)."
  value       = azurerm_kubernetes_cluster.main.kube_config_raw
  sensitive   = true
}
