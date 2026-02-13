variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "rg-virtual-test-harness"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"
}

variable "aks_cluster_name" {
  description = "Name of the AKS cluster"
  type        = string
  default     = "aks-virtual-test-harness"
}

variable "aks_dns_prefix" {
  description = "DNS prefix for the AKS cluster"
  type        = string
  default     = "vth"
}

variable "aks_node_count" {
  description = "Number of nodes in the AKS cluster"
  type        = number
  default     = 3
}

variable "aks_node_size" {
  description = "VM size for AKS nodes"
  type        = string
  default     = "Standard_D2s_v3"
}

variable "ai_foundry_name" {
  description = "Name of the AI Foundry workspace"
  type        = string
  default     = "ai-foundry-vth"
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default = {
    environment = "dev"
    project     = "virtual-test-harness"
  }
}
