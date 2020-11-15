output "primary_access_key" {
  value = azurerm_storage_account.datalake.primary_access_key
}

output "name" {
  value = azurerm_storage_account.datalake.name
}

output "primary_blob_endpoint" {
  value = azurerm_storage_account.datalake.primary_blob_endpoint
}

output "connection_string"{
  value = azurerm_storage_account.datalake.primary_connection_string
}