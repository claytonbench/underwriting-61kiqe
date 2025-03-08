# Terraform S3 Module for Loan Management System
# This module creates S3 buckets for document storage and logging with appropriate
# security, lifecycle, and replication configurations

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }
}

# Get current AWS region for use in IAM policies
data "aws_region" "current" {}

# Provider for replica region when cross-region replication is enabled
provider "aws" {
  alias  = "replica"
  region = var.replica_region
  
  count = var.enable_replication ? 1 : 0
}

# Local variables for naming consistency
locals {
  bucket_name = "${var.document_bucket_name}-${var.environment}"
  log_bucket_name = "${var.log_bucket_name}-${var.environment}"
}

#-----------------------
# Document Storage Bucket
#-----------------------
resource "aws_s3_bucket" "document_bucket" {
  bucket        = "${var.document_bucket_name}-${var.environment}"
  force_destroy = false

  tags = merge(var.tags, {
    Name = "${var.document_bucket_name}-${var.environment}"
  })
}

# Enable versioning on document bucket to track changes and prevent accidental deletion
resource "aws_s3_bucket_versioning" "document_bucket_versioning" {
  bucket = aws_s3_bucket.document_bucket.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# Configure server-side encryption for document bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "document_bucket_encryption" {
  bucket = aws_s3_bucket.document_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = var.kms_key_id
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

# Configure lifecycle policies for document bucket
resource "aws_s3_bucket_lifecycle_configuration" "document_bucket_lifecycle" {
  bucket = aws_s3_bucket.document_bucket.id

  rule {
    id     = "document-lifecycle"
    status = "Enabled"

    # Transition noncurrent versions to cheaper storage classes
    noncurrent_version_transition {
      noncurrent_days = var.standard_ia_transition_days
      storage_class   = "STANDARD_IA"
    }

    noncurrent_version_transition {
      noncurrent_days = var.glacier_transition_days
      storage_class   = "GLACIER"
    }

    # Expire noncurrent versions after retention period
    noncurrent_version_expiration {
      noncurrent_days = var.document_retention_days
    }
  }
}

# Block all public access to document bucket
resource "aws_s3_bucket_public_access_block" "document_bucket_public_access_block" {
  bucket = aws_s3_bucket.document_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

#-----------------------
# Log Bucket
#-----------------------
resource "aws_s3_bucket" "log_bucket" {
  bucket        = "${var.log_bucket_name}-${var.environment}"
  force_destroy = false

  tags = merge(var.tags, {
    Name = "${var.log_bucket_name}-${var.environment}"
  })
}

# Configure server-side encryption for log bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "log_bucket_encryption" {
  bucket = aws_s3_bucket.log_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = var.kms_key_id
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

# Configure lifecycle policies for log bucket
resource "aws_s3_bucket_lifecycle_configuration" "log_bucket_lifecycle" {
  bucket = aws_s3_bucket.log_bucket.id

  rule {
    id     = "log-lifecycle"
    status = "Enabled"

    # Transition logs to cheaper storage classes
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    # Expire logs after retention period
    expiration {
      days = var.log_retention_days
    }
  }
}

# Block all public access to log bucket
resource "aws_s3_bucket_public_access_block" "log_bucket_public_access_block" {
  bucket = aws_s3_bucket.log_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Configure logging for document bucket to log bucket
resource "aws_s3_bucket_logging" "document_bucket_logging" {
  bucket = aws_s3_bucket.document_bucket.id

  target_bucket = aws_s3_bucket.log_bucket.id
  target_prefix = "document-bucket-logs/"
}

#-----------------------
# Cross-Region Replication
#-----------------------
# Create replica bucket in the secondary region for disaster recovery
resource "aws_s3_bucket" "document_bucket_replica" {
  count    = var.enable_replication ? 1 : 0
  provider = aws.replica

  bucket        = "${var.document_bucket_name}-${var.environment}-replica"
  force_destroy = false

  tags = merge(var.tags, {
    Name = "${var.document_bucket_name}-${var.environment}-replica"
  })
}

# Enable versioning on replica bucket (required for replication)
resource "aws_s3_bucket_versioning" "document_bucket_replica_versioning" {
  count    = var.enable_replication ? 1 : 0
  provider = aws.replica
  
  bucket = aws_s3_bucket.document_bucket_replica[0].id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# Configure server-side encryption for replica bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "document_bucket_replica_encryption" {
  count    = var.enable_replication ? 1 : 0
  provider = aws.replica
  
  bucket = aws_s3_bucket.document_bucket_replica[0].id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = var.replica_kms_key_id != null ? var.replica_kms_key_id : var.kms_key_id
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

# Block all public access to replica bucket
resource "aws_s3_bucket_public_access_block" "document_bucket_replica_public_access_block" {
  count    = var.enable_replication ? 1 : 0
  provider = aws.replica
  
  bucket = aws_s3_bucket.document_bucket_replica[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Create IAM role for S3 replication
resource "aws_iam_role" "replication_role" {
  count = var.enable_replication ? 1 : 0
  
  name = "s3-replication-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Principal = {
          Service = "s3.amazonaws.com"
        },
        Effect = "Allow",
        Sid = ""
      }
    ]
  })

  tags = var.tags
}

# Create IAM policy for S3 replication permissions
resource "aws_iam_policy" "replication_policy" {
  count = var.enable_replication ? 1 : 0
  
  name = "s3-replication-policy-${var.environment}"
  
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "s3:GetReplicationConfiguration",
          "s3:ListBucket"
        ],
        Effect = "Allow",
        Resource = [
          aws_s3_bucket.document_bucket.arn
        ]
      },
      {
        Action = [
          "s3:GetObjectVersionForReplication",
          "s3:GetObjectVersionAcl",
          "s3:GetObjectVersionTagging"
        ],
        Effect = "Allow",
        Resource = [
          "${aws_s3_bucket.document_bucket.arn}/*"
        ]
      },
      {
        Action = [
          "s3:ReplicateObject",
          "s3:ReplicateDelete",
          "s3:ReplicateTags"
        ],
        Effect = "Allow",
        Resource = "${aws_s3_bucket.document_bucket_replica[0].arn}/*"
      },
      {
        Action = [
          "kms:Decrypt"
        ],
        Effect = "Allow",
        Resource = "${var.kms_key_id}",
        Condition = {
          StringLike = {
            "kms:ViaService": "s3.${data.aws_region.current.name}.amazonaws.com",
            "kms:EncryptionContext:aws:s3:arn": [
              "${aws_s3_bucket.document_bucket.arn}/*"
            ]
          }
        }
      },
      {
        Action = [
          "kms:Encrypt"
        ],
        Effect = "Allow",
        Resource = "${var.replica_kms_key_id != null ? var.replica_kms_key_id : var.kms_key_id}",
        Condition = {
          StringLike = {
            "kms:ViaService": "s3.${var.replica_region}.amazonaws.com",
            "kms:EncryptionContext:aws:s3:arn": [
              "${aws_s3_bucket.document_bucket_replica[0].arn}/*"
            ]
          }
        }
      }
    ]
  })
}

# Attach replication policy to replication role
resource "aws_iam_role_policy_attachment" "replication_policy_attachment" {
  count = var.enable_replication ? 1 : 0
  
  role       = aws_iam_role.replication_role[0].name
  policy_arn = aws_iam_policy.replication_policy[0].arn
}

# Configure replication for document bucket
resource "aws_s3_bucket_replication_configuration" "document_bucket_replication" {
  count = var.enable_replication ? 1 : 0
  
  # Must have bucket versioning enabled first
  depends_on = [
    aws_s3_bucket_versioning.document_bucket_versioning,
    aws_s3_bucket_versioning.document_bucket_replica_versioning
  ]

  bucket = aws_s3_bucket.document_bucket.id
  role   = aws_iam_role.replication_role[0].arn

  rule {
    id       = "document-replication"
    status   = "Enabled"
    priority = 0

    filter {
      prefix = ""
    }

    destination {
      bucket = aws_s3_bucket.document_bucket_replica[0].arn
      
      encryption_configuration {
        replica_kms_key_id = var.replica_kms_key_id != null ? var.replica_kms_key_id : var.kms_key_id
      }
    }

    source_selection_criteria {
      sse_kms_encrypted_objects {
        status = "Enabled"
      }
    }
  }
}