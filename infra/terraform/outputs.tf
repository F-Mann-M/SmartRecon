output "vm_ip_address" {
  value = azurerm_linux_virtual_machine.vm.public_ip_address
}

output "vm_identity_client_id" {
  value = azurerm_user_assigned_identity.vm_identity.client_id
}
