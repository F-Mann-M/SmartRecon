# Output the ip address of the virtual machine
output "vm_ip_address" {
  value = azurerm_linux_virtual_machine.vm.public_ip_address
}

 