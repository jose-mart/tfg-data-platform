output "storage_name" {
  value = module.storage.name
}

output "rg_name"{
    value = azurerm_resource_group.rg.name
}