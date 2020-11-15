resource "azurerm_storage_table" "stg_table" {
  name                 = var.table_name
  storage_account_name = var.storage_account_name
}