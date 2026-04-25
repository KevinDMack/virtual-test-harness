# ---------------------------------------------------------------------------
# modules/keyvault/variables.tf – Input variables for the Key Vault module.
# ---------------------------------------------------------------------------

variable "name" {
  description = "Name of the Key Vault (3–24 chars, globally unique)."
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group."
  type        = string
}

variable "location" {
  description = "Azure Government region."
  type        = string
}

variable "tenant_id" {
  description = "Azure AD tenant ID."
  type        = string
}

variable "soft_delete_retention_days" {
  description = "Days to retain soft-deleted objects (7–90)."
  type        = number
  default     = 7
}

variable "tags" {
  description = "Resource tags."
  type        = map(string)
  default     = {}
}
