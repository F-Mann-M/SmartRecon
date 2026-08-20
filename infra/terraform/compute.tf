# Compute resources for the SmartRecon project
# This file defines the compute resources, including a Linux virtual machine and its associated network interface and public IP address.

resource "azurerm_public_ip" "vm_public_ip" {
  name                = "${var.prefix}-vm-pip-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name
  allocation_method   = "Static"
  sku                 = "Standard"

  tags = local.common_tags
}

resource "azurerm_network_interface" "nic" {
  name                = "${var.prefix}-vm-nic-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.snet_compute.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.vm_public_ip.id
  }

  tags = local.common_tags
}

resource "azurerm_linux_virtual_machine" "vm" {
  name                = "${var.prefix}-vm-${var.environment}"
  resource_group_name = var.resource_group_name
  location            = var.location
  size = "Standard_B2ats_v2" # or "Standard_B2pts_v2"
  admin_username      = "adminuser"
  network_interface_ids = [
    azurerm_network_interface.nic.id,
  ]

  admin_ssh_key {
    username   = "adminuser"
    public_key = file(pathexpand("~/.ssh/id_ed25519.pub"))
  }

  disable_password_authentication = true

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "ubuntu-24_04-lts"
    sku       = "server"
    version   = "latest"
  }

  tags = local.common_tags
}