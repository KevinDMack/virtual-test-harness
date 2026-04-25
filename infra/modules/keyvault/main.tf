# ---------------------------------------------------------------------------
# modules/keyvault/main.tf – Azure Key Vault with:
#   • RBAC-based authorization (no legacy access policies)
#   • Purge protection enabled
#   • Soft-delete retention configurable
# ---------------------------------------------------------------------------

resource "azurerm_key_vault" "main" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name
  tenant_id           = var.tenant_id
  sku_name            = "standard"

  # Use Azure RBAC for data-plane authorization instead of access policies.
  enable_rbac_authorization = true

  # Retention and protection
  soft_delete_retention_days = var.soft_delete_retention_days
  purge_protection_enabled   = true

  tags = var.tags
}
