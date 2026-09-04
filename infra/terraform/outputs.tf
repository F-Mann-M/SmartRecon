# Temporary outputs for debugging and GitHub Actions integration. 
# only for development purposes. Remove or secure these outputs in production to avoid exposing sensitive information.

# output "application_gateway_public_ip" {
#   value       = azurerm_public_ip.application_gateway_public_ip.ip_address
#   description = "The public IP address of the Application Gateway. Use this to access the web application"
# }

output "vm_ip_address" {
  value = azurerm_linux_virtual_machine.vm.public_ip_address
  description = "The public IP address of the virtual machine. Use this to SSH into the VM."
}

output "vm_identity_client_id" {
  value = azurerm_user_assigned_identity.vm_identity.client_id
  description = "set as AZURE_CLIENT_ID in GitHub secrets for OIDC authentication"
}

# Output the Storage Account primary blob endpoint
output "azurerm_storage_account_primary_blob_endpoint" {
  value = azurerm_storage_account.storage.primary_blob_endpoint
  description = "set as AZURE_STORAGE_ACCOUNT_PRIMARY_BLOB_ENDPOINT in GitHub secrets"
}

# Output the ACR login server URL
output "acr_login_server" {
  value       = azurerm_container_registry.acr.login_server
  description = "set as ACR_LOGIN_SERVER in GitHub secrets"
}

# Outputs needed for GitHub Secrets / Variables
output "azure_client_id" {
  value       = azuread_application.github_actions.client_id
  description = "Set as AZURE_CLIENT_ID in GitHub secrets"
}

output "azure_tenant_id" {
  value       = data.azurerm_client_config.current.tenant_id
  description = "Set as AZURE_TENANT_ID in GitHub secrets"
}

output "azure_subscription_id" {
  value       = data.azurerm_client_config.current.subscription_id
  description = "Set as AZURE_SUBSCRIPTION_ID in GitHub secrets"
}

# Output the Key Vault Name. There is no User Authentication yet. 
#   value       = azurerm_key_vault.kv.name
#   description = "Name of the Azure Key Vault"
# }