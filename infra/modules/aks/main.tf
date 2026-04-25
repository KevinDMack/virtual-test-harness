# ---------------------------------------------------------------------------
# modules/aks/main.tf – AKS cluster with:
#   • System-assigned managed identity
#   • OIDC issuer + Workload Identity enabled (for pod-level Azure auth)
#   • Key Vault CSI Secret Store driver enabled
# ---------------------------------------------------------------------------

resource "azurerm_kubernetes_cluster" "main" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = var.dns_prefix
  kubernetes_version  = var.kubernetes_version

  # ── Identity ──────────────────────────────────────────────────────────────
  identity {
    type = "SystemAssigned"
  }

  # ── Default node pool ─────────────────────────────────────────────────────
  default_node_pool {
    name       = "system"
    node_count = var.node_count
    vm_size    = var.vm_size

    # Upgrade settings are required when node_count is set without auto-scaling.
    upgrade_settings {
      max_surge = "10%"
    }
  }

  # ── Workload Identity (OIDC) ───────────────────────────────────────────────
  # Required for per-pod Azure RBAC via federated credential tokens.
  oidc_issuer_enabled       = true
  workload_identity_enabled = true

  # ── Key Vault CSI Secret Store driver ─────────────────────────────────────
  # Allows Kubernetes pods to mount secrets from Azure Key Vault as volumes.
  key_vault_secrets_provider {
    secret_rotation_enabled  = true
    secret_rotation_interval = "2m"
  }

  tags = var.tags
}
