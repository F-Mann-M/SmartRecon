# Azure AI Foundry / Cognitive Services Account
resource "azurerm_cognitive_account" "foundry" {
  name                          = "${var.prefix}-ai-${var.environment}"
  location                      = azurerm_resource_group.rg.location
  resource_group_name           = azurerm_resource_group.rg.name
  kind                          = "AIServices"
  sku_name                      = "S0" # Standard SKU for Foundry
  custom_subdomain_name         = "${var.prefix}-ai-${var.environment}"
  public_network_access_enabled = false

  tags = local.common_tags
}

# Embedding Model Deployment (e.g. text-embedding-3-small)
resource "azurerm_cognitive_deployment" "embedding" {
  name                 = "text-embedding-3-small"
  cognitive_account_id = azurerm_cognitive_account.foundry.id

  model {
    format  = "OpenAI"
    name    = "text-embedding-3-small"
    version = "1"
  }

  sku {
    name     = "GlobalStandard"
    capacity = 20 # 20k Tokens Per Minute (TPM) quota
  }
}


# GPT Model Deployment 
resource "azurerm_cognitive_deployment" "reasoning_agent" {
  name                 = "gpt-5-mini"
  cognitive_account_id = azurerm_cognitive_account.foundry.id

  model {
    format  = "OpenAI"
    name    = "gpt-5-mini"
    version = "2025-08-07"
  }

  sku {
    name     = "GlobalStandard"
    capacity = 30
  }
}

# Private DNS Zone for AI Foundry / Cognitive Services
resource "azurerm_private_dns_zone" "cognitiveservices_dns" {
  name                = "privatelink.cognitiveservices.azure.com"
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_private_dns_zone_virtual_network_link" "cognitiveservices_dns_link" {
  name                  = "${var.prefix}-cognitiveservices-dns-link"
  resource_group_name   = azurerm_resource_group.rg.name
  private_dns_zone_name = azurerm_private_dns_zone.cognitiveservices_dns.name
  virtual_network_id    = azurerm_virtual_network.vnet.id
}

# Private Endpoint in snet-endpoint
resource "azurerm_private_endpoint" "foundry_pe" {
  name                = "${var.prefix}-foundry-pe"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  subnet_id           = azurerm_subnet.snet_endpoints.id

  private_service_connection {
    name                           = "${var.prefix}-foundry-psc"
    private_connection_resource_id = azurerm_cognitive_account.foundry.id
    is_manual_connection           = false
    subresource_names              = ["account"]
  }

  private_dns_zone_group {
    name                 = "foundry-dns-zone-group"
    private_dns_zone_ids = [azurerm_private_dns_zone.cognitiveservices_dns.id]
  }

  depends_on = [
    azurerm_private_dns_zone_virtual_network_link.cognitiveservices_dns_link,
    azurerm_cognitive_deployment.embedding,
    azurerm_cognitive_deployment.reasoning_agent
  ]
}

