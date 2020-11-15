data "azurerm_storage_account" "monitorstg" {
  name                = var.monitor_stg
  resource_group_name = var.monitor_rg
}


data "azurerm_storage_account" "aqsstg" {
  name                = var.aqs_stg
  resource_group_name = var.aqs_rg
}


resource "azurerm_storage_container" "stg-dead-letter" {
  name                 = "${var.aqs_name}-deadletter"
  storage_account_name = var.aqs_stg
}


resource "azurerm_storage_queue" "default" {
  name                 = var.aqs_name
  storage_account_name = var.aqs_stg 
}


resource "azurerm_eventgrid_event_subscription" "default" {
  name  = "${azurerm_storage_queue.default.name}-eg"
  scope = data.azurerm_storage_account.monitorstg.id
  event_delivery_schema = "EventGridSchema"

  storage_queue_endpoint {
    storage_account_id = data.azurerm_storage_account.aqsstg.id 
    queue_name         = azurerm_storage_queue.default.name 
  }

  included_event_types = [
    "Microsoft.Storage.BlobCreated"
  ]

  subject_filter {
      subject_begins_with = "/blobServices/default/containers/${var.monitor_container}/blobs/${var.monitor_path}"
      case_sensitive = false
  }

  advanced_filter {
    string_in {
      key = "data.api"
      values = ["CopyBlob", "PutBlob","PutBlockList","FlushWithClose"]
    }
  }

  storage_blob_dead_letter_destination {
    storage_account_id = data.azurerm_storage_account.aqsstg.id
    storage_blob_container_name = azurerm_storage_container.stg-dead-letter.name
  }
}