# AI Foundry Configuration
# Note: AI Foundry is part of Azure AI services

# Application Insights for monitoring
resource "azurerm_application_insights" "main" {
  name                = "${var.ai_foundry_name}-insights"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  application_type    = "web"
  
  tags = var.tags
}

# Storage Account for AI Foundry
resource "azurerm_storage_account" "ai_foundry" {
  name                     = replace(var.ai_foundry_name, "-", "")
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  
  tags = var.tags
}

# Cognitive Services Account for AI capabilities
resource "azurerm_cognitive_account" "main" {
  name                = var.ai_foundry_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  kind                = "CognitiveServices"
  sku_name            = "S0"
  
  tags = var.tags
}
