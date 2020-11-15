resource "azurerm_storage_account" "datalake" {
  name                     = replace("tfg-${var.env}-datalake", "-", "")
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_kind             = "StorageV2"
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = true
}

# resource "azurerm_role_assignment" "datalake_contributor" {
#   scope                = azurerm_storage_account.datalake.id
#   role_definition_name = "Storage Blob Data Contributor"
#   principal_id         = var.object_id
# }


resource "azurerm_storage_data_lake_gen2_filesystem" "datalake_fs" {
  name               = "datalake"
  storage_account_id = azurerm_storage_account.datalake.id
}