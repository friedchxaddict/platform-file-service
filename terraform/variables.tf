variable "project_id" {
  type = string
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "service_name" {
  type    = string
  default = "platform-file-service"
}

variable "image" {
  type = string
}

variable "allow_unauthenticated" {
  type    = bool
  default = true
}