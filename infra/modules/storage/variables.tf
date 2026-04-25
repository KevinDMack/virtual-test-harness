# ---------------------------------------------------------------------------
# modules/storage/variables.tf – Input variables for the Storage Account module.
# ---------------------------------------------------------------------------

variable "name" {
  description = "Storage account name (3–24 chars, lowercase alphanumeric, globally unique)."
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

variable "account_replication_type" {
  description = "Data redundancy type accepted by the azurerm provider: LRS, GRS, ZRS, RAGRS (read-access GRS), GZRS, or RAGZRS (read-access GZRS)."
  type        = string
  default     = "LRS"
}

variable "tags" {
  description = "Resource tags."
  type        = map(string)
  default     = {}
}
