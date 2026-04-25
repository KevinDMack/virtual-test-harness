# ---------------------------------------------------------------------------
# main.tf – Root module.  Composes the AKS, Key Vault, Storage, and ACR
#           sub-modules and wires role assignments between them.
# ---------------------------------------------------------------------------

data "azurerm_client_config" "current" {}

# ── Resource Group ─────────────────────────────────────────────────────────────

resource "azurerm_resource_group" "main" {
  name     = "rg-${var.prefix}-${var.environment}"
  location = var.location

  tags = merge(var.tags, {
    environment = var.environment
    managed_by  = "terraform"
  })
}

# ── Sub-modules ────────────────────────────────────────────────────────────────

module "acr" {
  source = "./modules/acr"

  name                = "${var.prefix}acr${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = var.acr_sku
  tags                = azurerm_resource_group.main.tags
}

module "keyvault" {
  source = "./modules/keyvault"

  name                       = "kv-${var.prefix}-${var.environment}"
  resource_group_name        = azurerm_resource_group.main.name
  location                   = azurerm_resource_group.main.location
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days = var.kv_soft_delete_retention_days
  tags                       = azurerm_resource_group.main.tags
}

module "storage" {
  source = "./modules/storage"

  name                     = "${var.prefix}st${var.environment}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_replication_type = var.storage_replication_type
  tags                     = azurerm_resource_group.main.tags
}

module "aks" {
  source = "./modules/aks"

  name                = "aks-${var.prefix}-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  dns_prefix          = "${var.prefix}-${var.environment}"
  node_count          = var.aks_node_count
  vm_size             = var.aks_vm_size
  kubernetes_version  = var.aks_kubernetes_version
  tags                = azurerm_resource_group.main.tags
}

# ── Role Assignments ───────────────────────────────────────────────────────────

# AKS kubelet identity → AcrPull on the Container Registry
# Enables the cluster to pull images without admin credentials.
resource "azurerm_role_assignment" "aks_acr_pull" {
  principal_id         = module.aks.kubelet_identity_object_id
  role_definition_name = "AcrPull"
  scope                = module.acr.id
}

# AKS control-plane identity → Key Vault Secrets User
# Required for the CSI Secret Store driver to read secrets from Key Vault.
resource "azurerm_role_assignment" "aks_kv_secrets_user" {
  principal_id         = module.aks.identity_principal_id
  role_definition_name = "Key Vault Secrets User"
  scope                = module.keyvault.id
}

# AKS control-plane identity → Storage Blob Data Contributor
# Allows pods (via workload identity) to read/write blobs in the storage account.
resource "azurerm_role_assignment" "aks_storage_blob" {
  principal_id         = module.aks.identity_principal_id
  role_definition_name = "Storage Blob Data Contributor"
  scope                = module.storage.id
}
