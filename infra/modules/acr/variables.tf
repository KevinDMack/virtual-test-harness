# ---------------------------------------------------------------------------
# modules/acr/variables.tf – Input variables for the Container Registry module.
# ---------------------------------------------------------------------------

variable "name" {
  description = "Container Registry name (5–50 chars, alphanumeric, globally unique)."
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

variable "sku" {
  description = "ACR pricing tier: Basic, Standard, or Premium."
  type        = string
  default     = "Standard"
}

variable "tags" {
  description = "Resource tags."
  type        = map(string)
  default     = {}
}
