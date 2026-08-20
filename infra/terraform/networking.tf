# Terraform configuration for Azure networking resources

resource "azurerm_virtual_network" "vnet" {
  name                = "smartrecon-vnet"
  address_space       = ["10.1.0.0/16"]
  location            = var.location
  resource_group_name = var.resource_group_name

  tags = {
    project = "SmartRecon"
  }
}

# Subnets
resource "azurerm_subnet" "snet_compute" {
  name                 = "snet-compute"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.1.1.0/24"]
}

resource "azurerm_subnet" "snet_postgres" {
  name                 = "snet-postgres"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.1.2.0/24"]

  delegation {
    name = "delegation_postgres"

    service_delegation {
      name    = "Microsoft.DBforPostgreSQL/flexibleServers"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
    }
  }
}

resource "azurerm_subnet" "snet_endpoints" {
  name                 = "snet-endpoints"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.1.3.0/24"]
}

resource "azurerm_network_security_group" "nsg_compute" {
  name                = "smartrecon-nsg-compute"
  location            = var.location
  resource_group_name = var.resource_group_name

  security_rule {
    name                       = "Allow-SSH-From-MyIP"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = var.my_ip
    destination_address_prefix = "*"
    description                = "Allow SSH from the admin IP into the compute subnet"
  }

  security_rule {
    name                       = "Allow-VNet-Internal"
    priority                   = 200
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "VirtualNetwork"
    destination_address_prefix = "VirtualNetwork"
    description                = "Allow internal VNet traffic"
  }

  tags = {
    project = "SmartRecon"
  }
}

resource "azurerm_network_security_group" "nsg_postgres" {
  name                = "smartrecon-nsg-postgres"
  location            = var.location
  resource_group_name = var.resource_group_name

  security_rule {
    name                       = "Allow-Postgres-From-Compute"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "5432"
    source_address_prefix      = "10.1.1.0/24"
    destination_address_prefix = "*"
    description                = "Allow PostgreSQL traffic from the compute subnet"
  }

  security_rule {
    name                       = "Allow-VNet-Internal"
    priority                   = 200
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "VirtualNetwork"
    destination_address_prefix = "VirtualNetwork"
    description                = "Allow internal VNet traffic"
  }

  tags = {
    project = "SmartRecon"
  }
}

resource "azurerm_network_security_group" "nsg_endpoints" {
  name                = "smartrecon-nsg-endpoints"
  location            = var.location
  resource_group_name = var.resource_group_name

  security_rule {
    name                       = "Allow-VNet-Internal"
    priority                   = 200
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "VirtualNetwork"
    destination_address_prefix = "VirtualNetwork"
    description                = "Allow internal VNet traffic"
  }

  tags = {
    project = "SmartRecon"
  }
}

resource "azurerm_subnet_network_security_group_association" "compute_assoc" {
  subnet_id                 = azurerm_subnet.snet_compute.id
  network_security_group_id = azurerm_network_security_group.nsg_compute.id
}

resource "azurerm_subnet_network_security_group_association" "postgres_assoc" {
  subnet_id                 = azurerm_subnet.snet_postgres.id
  network_security_group_id = azurerm_network_security_group.nsg_postgres.id
}

resource "azurerm_subnet_network_security_group_association" "endpoints_assoc" {
  subnet_id                 = azurerm_subnet.snet_endpoints.id
  network_security_group_id = azurerm_network_security_group.nsg_endpoints.id
}
