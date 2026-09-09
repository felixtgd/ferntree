terraform {
  required_providers {
    minio = {
      source  = "aminueza/minio"
      version = "~> 3.3"
    }
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.68"
    }
  }
}

provider "minio" {
  minio_server   = "fsn1.your-objectstorage.com"
  minio_user     = var.s3_access_key
  minio_password = var.s3_secret_key
  minio_region   = "fsn1"
  minio_ssl      = true
}

provider "hcloud" {
  token = var.hcloud_token
}
