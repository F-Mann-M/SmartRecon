# Storage for invoices and statements
resource "azurerm_storage_account" "storage" {
    name                     = "${var.prefix}storage${var.environment}"
    location                 = azurerm_resource_group.rg.location
    resource_group_name      = azurerm_resource_group.rg.name
    account_tier             = "Standard"
    account_replication_type = "LRS"

    tags = local.common_tags
}

# create container for invoices and statements
resource "azurerm_storage_container" "containers" {
    for_each = toset(["invoices", "bank-statements"])
    name                  = each.key
    storage_account_id    = azurerm_storage_account.storage.id
    container_access_type = "private"
}

# Enable Microsoft Defender for Storage to protect against malware and other threats
resource "azurerm_security_center_storage_defender" "storage_defender" {
  storage_account_id                          = azurerm_storage_account.storage.id
  malware_scanning_on_upload_enabled          = true
  malware_scanning_on_upload_cap_gb_per_month = 5000
  sensitive_data_discovery_enabled            = false
}