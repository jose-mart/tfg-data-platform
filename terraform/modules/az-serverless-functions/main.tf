resource "azurerm_app_service_plan" "sp" {
  name                = "tfg-${var.env}-sp"
  location            = var.location
  resource_group_name = var.resource_group_name
  kind                = "FunctionApp"
  reserved = true

  sku {
    tier = "Dynamic"
    size = "Y1"
    capacity = 0
  }
}

resource "azurerm_function_app" "az-function" {
  name                      = "tfg-${var.env}-fa"
  location                  = var.location
  resource_group_name       = var.resource_group_name
  app_service_plan_id       = azurerm_app_service_plan.sp.id
  storage_connection_string = var.connection_string
  os_type = var.os_type
  version = "~3"

  site_config {
      linux_fx_version = var.linux_fx_version
      use_32_bit_worker_process = var.use_32_bit_worker_process
      always_on = false
  }

  identity {
      type = "SystemAssigned"
  }

  app_settings = {
      FUNCTIONS_WORKER_RUNTIME = var.language
      sensor_data_url = "http://miv.opendata.belfla.be/miv/verkeersdata"
      sensor_description_url = "http://miv.opendata.belfla.be/miv/configuratie/xml"
  }
}