variable "resource_group_name" {}
variable "location" {}

variable "cluster_name" {}

variable "subnet_id" {}
variable "acr_id" {}

variable "node_count" {
  default = 2
}

variable "vm_size" {
  default = "Standard_B2s"
}