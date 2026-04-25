# ---------------------------------------------------------------------------
# variables.tf – Root-level input variables for the virtual-test-harness
#                infrastructure deployment (Azure Government / usgovarizona).
# ---------------------------------------------------------------------------

variable "prefix" {
  description = "Short lowercase prefix prepended to every resource name (2–8 chars)."
  type        = string
  default     = "vth"

  validation {
    condition     = can(regex("^[a-z0-9]{2,8}$", var.prefix))
    error_message = "prefix must be 2–8 lowercase alphanumeric characters."
  }
}

variable "environment" {
  description = "Deployment environment label (e.g. dev, staging, prod)."
  type        = string
  default     = "dev"
}

variable "location" {
  description = "Azure Government region for all resources."
  type        = string
  default     = "usgovarizona"
}

variable "tags" {
  description = "Additional tags merged onto every resource."
  type        = map(string)
  default     = {}
}

# ── AKS ────────────────────────────────────────────────────────────────────────

variable "aks_node_count" {
  description = "Number of nodes in the default (system) node pool."
  type        = number
  default     = 2
}

variable "aks_vm_size" {
  description = "VM SKU for the default node pool."
  type        = string
  default     = "Standard_DS2_v2"
}

variable "aks_kubernetes_version" {
  description = "Kubernetes version.  Leave null to use the latest stable version."
  type        = string
  default     = null
}

# ── Key Vault ──────────────────────────────────────────────────────────────────

variable "kv_soft_delete_retention_days" {
  description = "Number of days to retain soft-deleted Key Vault objects."
  type        = number
  default     = 7
}

# ── Storage ────────────────────────────────────────────────────────────────────

variable "storage_replication_type" {
  description = "Storage account replication type (LRS, GRS, ZRS, …)."
  type        = string
  default     = "LRS"
}

# ── Container Registry ─────────────────────────────────────────────────────────

variable "acr_sku" {
  description = "ACR pricing tier (Basic, Standard, Premium)."
  type        = string
  default     = "Standard"
}
