
# VM identities and role assignments for accessing storage account
resource "azurerm_user_assigned_identity" "vm_identity" {
  name                = "${var.prefix}-vm-identity"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_role_assignment" "storage_role" {
  scope                = azurerm_storage_account.storage.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_user_assigned_identity.vm_identity.principal_id
}