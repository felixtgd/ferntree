variable "s3_access_key" {
  description = "S3 access key for Hetzner Object Storage"
  type        = string
  sensitive   = true
}

variable "s3_secret_key" {
  description = "S3 secret key for Hetzner Object Storage"
  type        = string
  sensitive   = true
}

variable "hcloud_token" {
  description = "Hetzner Cloud API Token"
  type        = string
  sensitive   = true
}
