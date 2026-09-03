# PostgreSQL Flexible Server
resource "azurerm_postgresql_flexible_server" "postgres" {
  name                   = "${var.prefix}-psql-${var.environment}"
  resource_group_name    = azurerm_resource_group.rg.name
  location               = azurerm_resource_group.rg.location
  version                = "16"
  
  public_network_access_enabled = false
  
  administrator_login    = var.db_admin_user
  administrator_password = var.db_admin_password

  sku_name   = "B_Standard_B1ms"
  storage_mb = 32768

  backup_retention_days = 7
  zone                  = "1"

  tags = local.common_tags
}

# Private Endpoint for PostgreSQL
resource "azurerm_private_endpoint" "postgres_endpoint" {
  name                = "${var.prefix}-psql-pe"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  subnet_id           = azurerm_subnet.snet_endpoints.id

  private_service_connection {
    name                           = "${var.prefix}-psql-psc"
    private_connection_resource_id = azurerm_postgresql_flexible_server.postgres.id
    is_manual_connection           = false
    subresource_names              = ["postgresqlServer"]
  }

  private_dns_zone_group {
    name                 = "postgres-dns-zone-group"
    private_dns_zone_ids = [azurerm_private_dns_zone.postgres_dns_zone.id]
  }

  tags = local.common_tags
}

# Create Application Database
resource "azurerm_postgresql_flexible_server_database" "app_db" {
  name      = "smartrecon"
  server_id = azurerm_postgresql_flexible_server.postgres.id
  collation = "en_US.utf8"
  charset   = "UTF8"
}

# Enable pgvector in the Allowed Extensions Parameter
resource "azurerm_postgresql_flexible_server_configuration" "pgvector_extension" {
  name      = "azure.extensions"
  server_id = azurerm_postgresql_flexible_server.postgres.id
  value     = "VECTOR"
}