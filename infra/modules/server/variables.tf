variable "name" {
  description = "The name of the server"
  type        = string
}

variable "project" {
  description = "The name of the project"
  type        = string
}

variable "location" {
  description = "The location (i.e. datacenter) where the server will be created"
  type        = string
}

variable "labels" {
  description = "Labels to apply to the server and its resources"
  type        = map(string)
}

variable "image" {
  description = "The image to use for the server"
  type        = string
}

variable "type" {
  description = "The type of server to create, see https://www.hetzner.com/cloud/"
  type        = string
}

variable "ssh_public_key" {
  description = "The SSH public key to use for the server"
  type        = string
  sensitive   = true
}

variable "github_user" {
  description = "GitHub username for the server setup"
  type        = string
}

variable "github_email" {
  description = "GitHub email for the server setup"
  type        = string
}
