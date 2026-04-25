# ---------------------------------------------------------------------------
# modules/acr/main.tf – Azure Container Registry with:
#   • Admin account disabled – authentication via managed identity only
#   • Configurable SKU (Standard by default)
# ---------------------------------------------------------------------------

resource "azurerm_container_registry" "main" {
  name                = var.name
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = var.sku

  # Disable the admin account; image pulls use managed identity (AcrPull role).
  admin_enabled = false

  tags = var.tags
}
