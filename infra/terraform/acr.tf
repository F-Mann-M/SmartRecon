# Create Azure Container Registry (Basic SKU)
resource "azurerm_container_registry" "acr" {
  name                = "${replace(var.prefix, "-", "")}acr${var.environment}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = false # Disabled in favor of Managed Identity / Entra ID auth

  tags = local.common_tags
}

# Allow VM's Managed Identity to pull images from ACR
resource "azurerm_role_assignment" "vm_acr_pull" {
  scope                = azurerm_container_registry.acr.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_user_assigned_identity.vm_identity.principal_id
}

