# Terraform configuration for Azure networking resources

# Virtual Network
resource "azurerm_virtual_network" "vnet" {
  name                = "smartrecon-vnet"
  address_space       = ["10.1.0.0/16"]
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  tags = local.common_tags
}

# Subnets
# # Subnet for application gateway
# resource "azurerm_subnet" "snet_gateway" {
#   name                 = "snet-gateway"
#   resource_group_name  = azurerm_resource_group.rg.name
#   virtual_network_name = azurerm_virtual_network.vnet.name
#   address_prefixes     = ["10.1.0.0/24"]
# }

# # Public IP for Application Gateway
# resource "azurerm_public_ip" "application_gateway_public_ip" {
#   name                = "agw-public-ip"
#   location            = azurerm_resource_group.rg.location
#   resource_group_name = azurerm_resource_group.rg.name
#   allocation_method   = "Static"
#   sku                 = "Standard"
#   tags                = local.common_tags
# }

# Subnet where the backend lives
resource "azurerm_subnet" "snet_compute" {
  name                 = "snet-compute"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.1.1.0/24"]
}

# Consolidated Endpoints Subnet (Storage, Foundry, and PostgreSQL)
resource "azurerm_subnet" "snet_endpoints" {
  name                 = "snet-endpoints"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.1.3.0/24"]
}

# Private DNS Zone for PostgreSQL Private Link
resource "azurerm_private_dns_zone" "postgres_dns_zone" {
  name                = "privatelink.postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.rg.name
  tags                = local.common_tags
}

# private DNS zone link to the vnet for the postgres private endpoint
resource "azurerm_private_dns_zone_virtual_network_link" "postgres_dns_link" {
  name                  = "${var.prefix}-postgres-dns-link"
  resource_group_name   = azurerm_resource_group.rg.name
  private_dns_zone_name = azurerm_private_dns_zone.postgres_dns_zone.name
  virtual_network_id    = azurerm_virtual_network.vnet.id
}