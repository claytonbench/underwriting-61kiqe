# AWS KMS (Key Management Service) encryption keys for the loan management system
# These keys are used to encrypt sensitive data at rest, including database
# information, document storage, and application secrets.

#--------------------------------------------------------------
# Locals
#--------------------------------------------------------------

locals {
  common_tags = {
    Project     = "LoanManagementSystem"
    ManagedBy   = "Terraform"
    Component   = "Security"
  }
}

#--------------------------------------------------------------
# Data sources
#--------------------------------------------------------------

# Get current AWS account ID
data "aws_caller_identity" "current" {}

# Get current AWS region
data "aws_region" "current" {}

#--------------------------------------------------------------
# Variables
#--------------------------------------------------------------

variable "environment" {
  type        = string
  description = "Deployment environment (development, staging, production)"
  default     = "development"
}

variable "kms_key_deletion_window" {
  type        = number
  description = "Number of days to wait before deleting a KMS key that has been scheduled for deletion"
  default     = 30
}

variable "kms_key_rotation_enabled" {
  type        = bool
  description = "Whether to enable automatic rotation for the KMS keys"
  default     = true
}

variable "tags" {
  type        = map(string)
  description = "Additional tags to apply to all resources"
  default     = {}
}

#--------------------------------------------------------------
# KMS Key Policies
#--------------------------------------------------------------

# Policy document for the main KMS key
data "aws_iam_policy_document" "main_key_policy" {
  statement {
    sid    = "EnableIAMUserPermissions"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions   = ["kms:*"]
    resources = ["*"]
  }

  statement {
    sid    = "AllowECSTaskExecution"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
    actions = [
      "kms:Decrypt",
      "kms:DescribeKey",
      "kms:Encrypt",
      "kms:GenerateDataKey*",
      "kms:ReEncrypt*",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "AllowCloudWatchLogs"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["logs.${data.aws_region.current.name}.amazonaws.com"]
    }
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:DescribeKey",
    ]
    resources = ["*"]
    condition {
      test     = "ArnEquals"
      variable = "kms:EncryptionContext:aws:logs:arn"
      values   = ["arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:*"]
    }
  }
}

# Policy document for the database KMS key
data "aws_iam_policy_document" "database_key_policy" {
  statement {
    sid    = "EnableIAMUserPermissions"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions   = ["kms:*"]
    resources = ["*"]
  }

  statement {
    sid    = "AllowRDSEncryption"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["rds.amazonaws.com"]
    }
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:DescribeKey",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "AllowECSTaskAccess"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
    actions = [
      "kms:Decrypt",
      "kms:DescribeKey",
    ]
    resources = ["*"]
  }
}

# Policy document for the document KMS key
data "aws_iam_policy_document" "document_key_policy" {
  statement {
    sid    = "EnableIAMUserPermissions"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions   = ["kms:*"]
    resources = ["*"]
  }

  statement {
    sid    = "AllowS3Encryption"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["s3.amazonaws.com"]
    }
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:DescribeKey",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "AllowECSTaskAccess"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:DescribeKey",
    ]
    resources = ["*"]
  }
}

#--------------------------------------------------------------
# KMS Keys and Aliases
#--------------------------------------------------------------

# Main KMS key for encrypting sensitive data in the loan management system
resource "aws_kms_key" "main" {
  description             = "Main KMS key for the loan management system"
  deletion_window_in_days = var.kms_key_deletion_window
  enable_key_rotation     = var.kms_key_rotation_enabled
  policy                  = data.aws_iam_policy_document.main_key_policy.json
  tags                    = merge(local.common_tags, var.tags, { Name = "${var.environment}-main-kms-key" })
}

# Alias for the main KMS key
resource "aws_kms_alias" "main" {
  name          = "alias/${var.environment}-loan-management-main-key"
  target_key_id = aws_kms_key.main.key_id
}

# KMS key for encrypting database data in the loan management system
resource "aws_kms_key" "database" {
  description             = "KMS key for database encryption in the loan management system"
  deletion_window_in_days = var.kms_key_deletion_window
  enable_key_rotation     = var.kms_key_rotation_enabled
  policy                  = data.aws_iam_policy_document.database_key_policy.json
  tags                    = merge(local.common_tags, var.tags, { Name = "${var.environment}-database-kms-key" })
}

# Alias for the database KMS key
resource "aws_kms_alias" "database" {
  name          = "alias/${var.environment}-loan-management-database-key"
  target_key_id = aws_kms_key.database.key_id
}

# KMS key for encrypting document data in the loan management system
resource "aws_kms_key" "document" {
  description             = "KMS key for document encryption in the loan management system"
  deletion_window_in_days = var.kms_key_deletion_window
  enable_key_rotation     = var.kms_key_rotation_enabled
  policy                  = data.aws_iam_policy_document.document_key_policy.json
  tags                    = merge(local.common_tags, var.tags, { Name = "${var.environment}-document-kms-key" })
}

# Alias for the document KMS key
resource "aws_kms_alias" "document" {
  name          = "alias/${var.environment}-loan-management-document-key"
  target_key_id = aws_kms_key.document.key_id
}

#--------------------------------------------------------------
# Outputs
#--------------------------------------------------------------

output "main_kms_key_id" {
  description = "ID of the main KMS key for encryption"
  value       = aws_kms_key.main.key_id
}

output "main_kms_key_arn" {
  description = "ARN of the main KMS key for encryption"
  value       = aws_kms_key.main.arn
}

output "database_kms_key_id" {
  description = "ID of the database KMS key for encryption"
  value       = aws_kms_key.database.key_id
}

output "database_kms_key_arn" {
  description = "ARN of the database KMS key for encryption"
  value       = aws_kms_key.database.arn
}

output "document_kms_key_id" {
  description = "ID of the document KMS key for encryption"
  value       = aws_kms_key.document.key_id
}

output "document_kms_key_arn" {
  description = "ARN of the document KMS key for encryption"
  value       = aws_kms_key.document.arn
}