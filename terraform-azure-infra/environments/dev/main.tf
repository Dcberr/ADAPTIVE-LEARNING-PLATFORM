module "resource_group" {
  source = "../../modules/resource-group"

  resource_group_name = "${var.project_name}-${var.environment}-rg"
  location            = var.location
}

module "network" {
  source = "../../modules/network"

  resource_group_name = module.resource_group.name
  location            = var.location

  vnet_name          = "${var.project_name}-${var.environment}-vnet"
  subnet_name        = "aks-subnet"
  address_space      = ["10.0.0.0/16"]
  subnet_prefixes    = ["10.0.1.0/24"]
}

module "acr" {
  source = "../../modules/acr"

  resource_group_name = module.resource_group.name
  location            = var.location

  acr_name = "${var.project_name}${var.environment}acr"
}

module "aks" {
  source = "../../modules/aks"

  resource_group_name = module.resource_group.name
  location            = var.location

  cluster_name = "${var.project_name}-${var.environment}-aks"

  subnet_id = module.network.subnet_id

  acr_id = module.acr.acr_id

  node_count = 2
  vm_size    = "Standard_B2s"
}