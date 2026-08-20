variable "location" {
  description = "location of vnet and services"
}

variable "resource_group_name" {
  description = "name of resource group for SmartRecon"
}

variable "azurerm_virtual_network" {
  description = "name of the virtual network"
}

variable "my_ip" {
  description = "IP address of the administrative machine"
}

variable "environment" {
  description = "Environment name (e.g., dev, prod)"
}

variable "prefix" {
  description = "Prefix for resource names"
}
