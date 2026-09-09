variable "project" {
  description = "The name of the project"
  type        = string
}

variable "name" {
  description = "The name of the storage bucket"
  type        = string
}

variable "visibility" {
  description = "The visibility of the storage bucket (private or public)"
  type        = string
}
