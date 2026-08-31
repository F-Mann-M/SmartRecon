# Network Security Groups (NSGs) for SmartRecon Azure Deployment
# NSG: Application Gateway Subnet (Restricted to Developer IP)
resource "azurerm_network_security_group" "nsg_gateway" {
  name                = "smartrecon-nsg-gateway"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  # Azure Gateway infrastructure management & health probes
  security_rule {
    name                       = "Allow-Azure-GatewayManager"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "65200-65535"
    source_address_prefix      = "GatewayManager"
    destination_address_prefix = "*"
    description                = "Allow Azure GatewayManager control plane communication"
  }

  # Inbound HTTP restricted to IP address of the developer (temporary for testing purposes)
  security_rule {
    name                       = "Allow-HTTP-From-MyIP"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = var.my_ip
    destination_address_prefix = "*"
    description                = "Allow HTTP web traffic exclusively from developer IP"
  }

  # Inbound HTTPS restricted to developer IP
  security_rule {
    name                       = "Allow-HTTPS-From-MyIP"
    priority                   = 120
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = var.my_ip
    destination_address_prefix = "*"
    description                = "Allow HTTPS web traffic exclusively from developer IP"
  }

  # Azure Load Balancer health monitoring
  security_rule {
    name                       = "Allow-Azure-LoadBalancer"
    priority                   = 130
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "AzureLoadBalancer"
    destination_address_prefix = "*"
    description                = "Allow Azure Load Balancer health checks"
  }

  tags = local.common_tags
}


# NSG: Compute Subnet (VM with FastAPI + SSH)
resource "azurerm_network_security_group" "nsg_compute" {
  name                = "smartrecon-nsg-compute"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  # SSH access restricted strictly to developer IP
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
    description                = "Allow SSH from the developer IP into the compute subnet"
  }

  # FastAPI port 8000 traffic forwarding only from Gateway subnet
  security_rule {
    name                       = "Allow-FastAPI-From-Gateway"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8000"
    source_address_prefix      = azurerm_subnet.snet_gateway.address_prefixes[0]
    destination_address_prefix = "*"
    description                = "Allow reverse-proxy traffic from Application Gateway"
  }

  # Internal VNet communication
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

  tags = local.common_tags
}



# NSG: PostgreSQL Subnet
resource "azurerm_network_security_group" "nsg_postgres" {
  name                = "smartrecon-nsg-postgres"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  security_rule {
    name                       = "Allow-Postgres-From-Compute"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "5432"
    source_address_prefix      = azurerm_subnet.snet_compute.address_prefixes[0]
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

  tags = local.common_tags
}


# NSG: Endpoints Subnet (Foundry, Storage, Key Vault Private Endpoints)
resource "azurerm_network_security_group" "nsg_endpoints" {
  name                = "smartrecon-nsg-endpoints"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

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

  tags = local.common_tags
}

# Subnet <-> NSG Associations
resource "azurerm_subnet_network_security_group_association" "gateway_assoc" {
  subnet_id                 = azurerm_subnet.snet_gateway.id
  network_security_group_id = azurerm_network_security_group.nsg_gateway.id
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