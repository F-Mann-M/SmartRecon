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

variable "db_admin_user" {
  description = "Administrator username for PostgreSQL Flexible Server"
}

variable "db_admin_password" {
  description = "Administrator password for PostgreSQL Flexible Server"
}

variable "public_key" {
  description = "Public SSH key for VM access"
}

variable "subscription_id" {
  description = "Azure subscription ID"
}