output "tenant_id" {
  value = azurerm_data_factory.adf.identity[0].tenant_id
}

output "principal_id" {
  value = azurerm_data_factory.adf.identity[0].principal_id
}