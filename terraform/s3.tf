# ===================== S3 ARTIFACTS STORAGE =====================

resource "aws_s3_bucket" "fakeguard_artifacts" {
  bucket_prefix = "${var.project_name}-artifacts-"
  force_destroy = false

  tags = {
    Name = "${var.project_name}-artifacts-bucket"
  }
}

# Enforce Server-Side Encryption (SSE-S3 AES-256)
resource "aws_s3_bucket_server_side_encryption_configuration" "artifacts_encryption" {
  bucket = aws_s3_bucket.fakeguard_artifacts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Object Versioning
resource "aws_s3_bucket_versioning" "artifacts_versioning" {
  bucket = aws_s3_bucket.fakeguard_artifacts.id

  versioning_configuration {
    status = var.enable_s3_versioning ? "Enabled" : "Suspended"
  }
}

# Enforce S3 Block Public Access (All 4 settings enabled)
resource "aws_s3_bucket_public_access_block" "artifacts_pab" {
  bucket = aws_s3_bucket.fakeguard_artifacts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
