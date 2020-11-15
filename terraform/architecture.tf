# Get workspace

locals {
    workspace = "${lookup(var.env, terraform.workspace, "dev")}"
}

# Saving status

terraform {
  backend "azurerm" {
    resource_group_name   = "tfg-dev-rg"
    storage_account_name  = "tfgdevdatalake"
    container_name        = "terraform-dev-state"
    key                   = "terraform.tfstate"
  }
}

# Configure Azure provider

provider "azurerm" {
  version = "=2.17.0"
  features {}
}

data "azurerm_client_config" "current"{}

module "deployment"{
    source = "./environments/tfg-prod"

    env = local.workspace
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id
    sqlserver_user = "tfg${local.workspace}"
    sqlserver_password = "TrabajodefindeestudiosCurso2019_2020!"
}