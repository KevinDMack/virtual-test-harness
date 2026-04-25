# ---------------------------------------------------------------------------
# modules/storage/main.tf – Azure Storage Account with:
#   • Shared-access-key (SAS) access disabled – Azure AD auth only
#   • Public blob access disabled
#   • TLS 1.2+ enforced
#   • HTTPS-only traffic
# ---------------------------------------------------------------------------

resource "azurerm_storage_account" "main" {
  name                     = var.name
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = var.account_replication_type

  # Security hardening
  shared_access_key_enabled       = false
  allow_nested_items_to_be_public = false
  min_tls_version                 = "TLS1_2"
  https_traffic_only_enabled      = true

  # Identity-based access – no local keys
  default_to_oauth_authentication = true

  blob_properties {
    # Soft-delete for blobs (7-day retention)
    delete_retention_policy {
      days = 7
    }
    # Soft-delete for containers (7-day retention)
    container_delete_retention_policy {
      days = 7
    }
  }

  tags = var.tags
}
