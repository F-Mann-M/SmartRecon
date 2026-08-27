# PostgreSQL Flexible Server
resource "azurerm_postgresql_flexible_server" "postgres" {
  name                   = "${var.prefix}-psql-${var.environment}"
  resource_group_name    = azurerm_resource_group.rg.name
  location               = azurerm_resource_group.rg.location
  version                = "16"
  delegated_subnet_id    = azurerm_subnet.snet_postgres.id 
  private_dns_zone_id    = azurerm_private_dns_zone.postgres_dns_zone.id
  public_network_access_enabled = false
  
  administrator_login    = var.db_admin_user
  administrator_password = var.db_admin_password

  sku_name   = "B_Standard_B1ms" # Cost-effective burstable tier for dev
  storage_mb = 32768             # 32 GB minimum

  backup_retention_days = 7
  zone                  = "1"

  tags = local.common_tags

  depends_on = [azurerm_private_dns_zone_virtual_network_link.postgres_dns_link]
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