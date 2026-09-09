terraform {
  required_providers {
    minio = {
      source                = "aminueza/minio"
      configuration_aliases = [minio]
    }
  }
}

resource "minio_s3_bucket" "data" {
  bucket         = "${var.project}-s3-${var.name}"
  acl            = var.visibility
  object_locking = false
}

resource "minio_s3_bucket_versioning" "bucket_versioning" {
  bucket = minio_s3_bucket.data.bucket
  versioning_configuration {
    status = "Enabled"
  }
  depends_on = [minio_s3_bucket.data]
}
