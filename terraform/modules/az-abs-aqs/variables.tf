variable "monitor_rg" {
    type = string
    description = "Resource group where the blobs to monitor are."
}

variable "monitor_stg" {
    type = string
    description = "Storage account where the blobs to monitor are."
}

variable "monitor_container" {
    type = string
    description = "Container where the blobs to monitor are."
}

variable "monitor_path" {
    type = string
    description = "Path relative to monitor_container to monitor."
}

variable "aqs_rg" {
    type = string
    description = "Resource group for the queue and dead letter events."
}

variable "aqs_stg" {
    type = string
    description = "Resource group for the queue and dead letter events."
}

variable "aqs_name" {
    type = string
    description = "Name of the queue to use for the events"
}

variable "dead_letter_container" {
    type = string
    description = "Name of the dead letter events or null (it will be generated from the queue name)"
    default = ""
}