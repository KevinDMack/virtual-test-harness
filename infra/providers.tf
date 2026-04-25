terraform {
  required_version = ">= 1.10.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }

  # Backend is configured at init time via infra/scripts/init.sh.
  # All state is stored in an Azure Government Storage Account.
  backend "azurerm" {}
}

provider "azurerm" {
  environment = "usgovernment"

  features {
    key_vault {
      purge_soft_delete_on_destroy               = false
      recover_soft_deleted_key_vaults            = true
      purge_soft_deleted_secrets_on_destroy      = false
      recover_soft_deleted_secrets               = true
      purge_soft_deleted_certificates_on_destroy = false
      recover_soft_deleted_certificates          = true
    }
  }
}
