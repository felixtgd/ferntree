terraform {
  backend "s3" {
    bucket                      = "ferntree-state"
    endpoint                    = "https://fsn1.your-objectstorage.com"
    key                         = "opentofu.tfstate"
    region                      = "main"
    skip_credentials_validation = true
    skip_metadata_api_check     = true
    skip_region_validation      = true
  }
}
