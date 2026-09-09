locals {
  buckets = {
    data = {
      visibility = "private"
    }
  }
}

module "storage" {
  source     = "../modules/storage"
  for_each   = local.buckets
  project    = local.project
  name       = each.key
  visibility = each.value.visibility
  providers = {
    minio = minio
  }
}
