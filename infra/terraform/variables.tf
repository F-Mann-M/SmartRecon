
# Resource group
variable "location" {
  description = "location of vnet and services"
}

variable "resource_group_name" {
  description = "name of resource group for SmartRecon"
}

# Vnet
variable "azurerm_virtual_network" {
  description = "name of the virtual network"
}

# developer ip for ssh access to vmq and for frontend access to the webapp
variable "my_ip" {
  description = "IP address of the administrative machine"
}

# Current environment dev
variable "environment" {
  description = "Environment name (e.g., dev, prod)"
}

variable "prefix" {
  description = "Prefix for resource names"
}

# Database variables
variable "db_admin_user" {
  description = "Administrator username for PostgreSQL Flexible Server"
}

variable "db_admin_password" {
  description = "Administrator password for PostgreSQL Flexible Server"
}

# Public SSH key for VM access
variable "public_key" {
  description = "Public SSH key for VM access"
}

# Azure subscription ID
variable "subscription_id" {
  description = "Azure subscription ID"
}


# Variables for GitHub Repository
variable "github_organization" {
  type        = string
  description = "GitHub organization or username"
}

variable "github_repository" {
  type        = string
  description = "GitHub repository name"
}

