variable "environment" {
  description = "Deployment environment (development, staging, production)"
  type        = string

  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production."
  }
}

variable "document_bucket_name" {
  description = "Base name for the document storage S3 bucket (will be appended with environment)"
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$", var.document_bucket_name))
    error_message = "The document bucket name must be a valid S3 bucket name, conforming to DNS naming conventions."
  }
}

variable "log_bucket_name" {
  description = "Base name for the log storage S3 bucket (will be appended with environment)"
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$", var.log_bucket_name))
    error_message = "The log bucket name must be a valid S3 bucket name, conforming to DNS naming conventions."
  }
}

variable "kms_key_id" {
  description = "KMS key ID for server-side encryption of S3 bucket contents"
  type        = string

  validation {
    condition     = can(regex("^(arn:aws:kms:[a-z0-9-]+:[0-9]{12}:key/[a-f0-9-]{36}|[a-f0-9-]{36})$", var.kms_key_id))
    error_message = "The KMS key ID must be a valid ARN or UUID format."
  }
}

variable "enable_replication" {
  description = "Whether to enable cross-region replication for disaster recovery"
  type        = bool
  default     = false
}

variable "replica_region" {
  description = "AWS region for the replica S3 bucket when replication is enabled"
  type        = string
  default     = "us-west-2"

  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[0-9]$", var.replica_region))
    error_message = "The replica region must be a valid AWS region (e.g., us-west-2)."
  }
}

variable "replica_kms_key_id" {
  description = "KMS key ID in the replica region for server-side encryption of replicated objects"
  type        = string
  default     = null

  validation {
    condition     = var.replica_kms_key_id == null || can(regex("^(arn:aws:kms:[a-z0-9-]+:[0-9]{12}:key/[a-f0-9-]{36}|[a-f0-9-]{36})$", var.replica_kms_key_id))
    error_message = "If provided, the replica KMS key ID must be a valid ARN or UUID format."
  }
}

variable "document_retention_days" {
  description = "Number of days to retain non-current document versions before deletion"
  type        = number
  default     = 2555  # 7 years for compliance requirements

  validation {
    condition     = var.document_retention_days > 0
    error_message = "Document retention days must be a positive number."
  }
}

variable "log_retention_days" {
  description = "Number of days to retain log files before deletion"
  type        = number
  default     = 730  # 2 years

  validation {
    condition     = var.log_retention_days > 0
    error_message = "Log retention days must be a positive number."
  }
}

variable "standard_ia_transition_days" {
  description = "Number of days before transitioning objects to STANDARD_IA storage class"
  type        = number
  default     = 90  # 3 months

  validation {
    condition     = var.standard_ia_transition_days >= 30
    error_message = "Standard IA transition must be at least 30 days as recommended by AWS for cost optimization."
  }
}

variable "glacier_transition_days" {
  description = "Number of days before transitioning objects to GLACIER storage class"
  type        = number
  default     = 365  # 1 year

  validation {
    condition     = var.glacier_transition_days > var.standard_ia_transition_days
    error_message = "Glacier transition days must be greater than Standard IA transition days."
  }
}

variable "tags" {
  description = "Tags to apply to all resources created by this module"
  type        = map(string)
  default     = {}

  validation {
    condition     = length(keys(var.tags)) <= 50
    error_message = "Maximum of 50 tags are allowed for AWS resources."
  }
}