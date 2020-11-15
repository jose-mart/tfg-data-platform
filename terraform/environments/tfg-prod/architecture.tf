locals{
  stream_analytics_query = file("./environments/tfg-prod/stream_analytics_query/query.sql")
}


# Environment

module "environment" {
  source = "./custom_configuration"
}

# Configure Azure Resource Group

resource "azurerm_resource_group" "rg" {
    name     = "tfg-${var.env}-rg"
    location = module.environment.location
}

# ABS - AQS

module "abs_aqs_sensor_data"{
  source = "../../modules/az-abs-aqs"

  monitor_rg = azurerm_resource_group.rg.name
  monitor_stg = module.storage.name
  monitor_container = "datalake"
  monitor_path = "raw/sensor_data"
  aqs_rg = azurerm_resource_group.rg.name
  aqs_stg = module.storage.name
  aqs_name = "sensor-data-queue"
  dead_letter_container = "sensor-data"
}

module "abs_aqs_sensor_description"{
  source = "../../modules/az-abs-aqs"

  monitor_rg = azurerm_resource_group.rg.name
  monitor_stg = module.storage.name
  monitor_container = "datalake"
  monitor_path = "raw/sensor_description"
  aqs_rg = azurerm_resource_group.rg.name
  aqs_stg = module.storage.name
  aqs_name = "sensor-description-queue"
  dead_letter_container = "sensor-description"
}

# ADF

module "adf_devops"{
    source = "../../modules/az-adf-devops"

    env = var.env
    location = azurerm_resource_group.rg.location
    resource_group_name = "tfg-${var.env}-rg"
    account_name = module.environment.adf_vsts.account_name
    branch_name = module.environment.adf_vsts.branch_name
    project_name = module.environment.adf_vsts.project_name
    repository_name = module.environment.adf_vsts.repository_name
    root_folder = module.environment.adf_vsts.root_folder
    tenant_id = var.tenant_id
}

# Azure Storage Account

module "storage"{
  source = "../../modules/az-stg"

  resource_group_name = azurerm_resource_group.rg.name
  location = azurerm_resource_group.rg.location
  env = var.env
  object_id = var.object_id
}

# Watermark table

module "stg-table"{
  source = "../../modules/az_stg_table"

  storage_account_name = module.storage.name
  table_name = "ingestionlog"
}

# Configuration table

module "stg-conf-table"{
  source = "../../modules/az_stg_table"

  storage_account_name = module.storage.name
  table_name = "conftable"
}

# Azure function

module "az-func"{
  source = "../../modules/az-serverless-functions"

  env = var.env
  location = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  connection_string = module.storage.connection_string
  os_type = "linux"
  linux_fx_version = "PYTHON|3.7"
  use_32_bit_worker_process = false
  language = "python"
}

# Azure SQL Server

resource "azurerm_sql_server" "sqlserver" {
  name                         = "tfg-${var.env}-sqlserver"
  resource_group_name          = azurerm_resource_group.rg.name
  location                     = azurerm_resource_group.rg.location
  version                      = "12.0"
  administrator_login          = var.sqlserver_user
  administrator_login_password = var.sqlserver_password
}

# Azure SQL Database

resource "azurerm_sql_database" "database" {
  name                = "tfg-${var.env}-db"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  server_name         = azurerm_sql_server.sqlserver.name
  edition = "basic"
}

# Azure databricks

resource "azurerm_databricks_workspace" "dbricks"{
  name                = "tfg-${var.env}-dbricks"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "standard"
}

# Azure key vault

resource "azurerm_key_vault" "kv" {
  name                        = "tfg-${var.env}-kv"
  location                    = azurerm_resource_group.rg.location
  resource_group_name         = azurerm_resource_group.rg.name 
  enabled_for_disk_encryption = true
  tenant_id                   = var.tenant_id

  soft_delete_enabled = true
  sku_name = "standard"
}

# Azure key vault Policies

resource "azurerm_key_vault_access_policy" "kv_user_policy" {
  key_vault_id = azurerm_key_vault.kv.id 

  tenant_id = var.tenant_id
  object_id = var.object_id

  certificate_permissions = [
    "Get",
    "List",
    "Update",
    "Create",
    "Import",
    "Delete",
    "Recover",
    "Backup",
    "Restore",
    "ManageContacts",
    "ManageIssuers",
    "GetIssuers",
    "ListIssuers",
    "SetIssuers",
    "DeleteIssuers",
    "Purge"
  ]

  key_permissions = [
    "Get",
    "List",
    "Update",
    "Create",
    "Import",
    "Delete",
    "Recover",
    "Backup",
    "Restore"
  ]

  secret_permissions = [
    "Get",
    "List",
    "Set",
    "Delete",
    "Recover",
    "Backup",
    "Restore"
  ]

  storage_permissions = [
    "get",
  ]
}


resource "azurerm_key_vault_access_policy" "kv_adf_policy" {
  key_vault_id = azurerm_key_vault.kv.id

  tenant_id = module.adf_devops.tenant_id
  object_id = module.adf_devops.principal_id

  depends_on = [module.adf_devops]

  key_permissions = [
    "Get",
    "List",
    "Update",
    "Create",
    "Import",
    "Delete",
    "Recover",
    "Backup",
    "Restore"
  ]

  secret_permissions = [
    "Get",
    "List",
    "Recover"
  ]
}


# Azure Key Vault Secrets

resource "azurerm_key_vault_secret" "stg_key" {
  name         = "stg-key"
  value        = module.storage.primary_access_key
  key_vault_id = azurerm_key_vault.kv.id
}

resource "azurerm_key_vault_secret" "stg_name" {
  name         = "stg-name"
  value        = module.storage.name
  key_vault_id = azurerm_key_vault.kv.id
}

resource "azurerm_key_vault_secret" "databricks-token" {
  name         = "databricks-token"
  value        = "dapif47c9cdb4aada16c9223892cfdaa7eb6"
  key_vault_id = azurerm_key_vault.kv.id
}

resource "azurerm_key_vault_secret" "db_username" {
  name         = "db-username"
  value        = var.sqlserver_user
  key_vault_id = azurerm_key_vault.kv.id
}

resource "azurerm_key_vault_secret" "db_password" {
  name         = "db-password"
  value        = var.sqlserver_password
  key_vault_id = azurerm_key_vault.kv.id
}

resource "azurerm_key_vault_secret" "db_hostname" {
  name         = "db-hostname"
  value        = "${azurerm_sql_server.sqlserver.name}.database.windows.net"
  key_vault_id = azurerm_key_vault.kv.id
}

resource "azurerm_key_vault_secret" "db_database" {
  name         = "db-database"
  value        = azurerm_sql_database.database.name
  key_vault_id = azurerm_key_vault.kv.id
}

resource "azurerm_key_vault_secret" "stg_connection_string" {
  name         = "stg-connection-string"
  value        = module.storage.connection_string
  key_vault_id = azurerm_key_vault.kv.id
}

# Stream Analytics

resource "azurerm_stream_analytics_job" "stream_analytics" {
  name                                     = "tfg-${var.env}-sa"
  resource_group_name                      = azurerm_resource_group.rg.name
  location                                 = azurerm_resource_group.rg.location
  compatibility_level                      = "1.1"
  data_locale                              = "en-GB"
  events_late_arrival_max_delay_in_seconds = 60
  events_out_of_order_max_delay_in_seconds = 50
  events_out_of_order_policy               = "Adjust"
  output_error_policy                      = "Drop"
  streaming_units                          = 6

  transformation_query = local.stream_analytics_query
}

# Stream analytics inputs

resource "azurerm_stream_analytics_stream_input_blob" "sa_input_sensor_data" {
  name                      = "sensor-data"
  stream_analytics_job_name = azurerm_stream_analytics_job.stream_analytics.name
  resource_group_name       = azurerm_stream_analytics_job.stream_analytics.resource_group_name
  storage_account_name      = module.storage.name
  storage_account_key       = module.storage.primary_access_key
  storage_container_name    = "datalake"
  path_pattern              = "raw/sensor_data/"
  date_format               = "yyyy/MM/dd"
  time_format               = "HH"

  serialization {
    type     = "Json"
    encoding = "UTF8"
  }
}

resource "azurerm_stream_analytics_stream_input_blob" "sa_input_sensor_description" {
  name                      = "sensor-description"
  stream_analytics_job_name = azurerm_stream_analytics_job.stream_analytics.name
  resource_group_name       = azurerm_stream_analytics_job.stream_analytics.resource_group_name
  storage_account_name      = module.storage.name
  storage_account_key       = module.storage.primary_access_key
  storage_container_name    = "datalake"
  path_pattern              = "raw/sensor_description/"
  date_format               = "yyyy/MM/dd"
  time_format               = "HH"

  serialization {
    type     = "Json"
    encoding = "UTF8"
  }
}
