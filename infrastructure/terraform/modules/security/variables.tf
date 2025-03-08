# Variables for the security module which manages security resources including
# security groups, IAM roles, KMS encryption keys, and WAF configurations 
# for the loan management system.

#--------------------------------------------------------------
# General Configuration Variables
#--------------------------------------------------------------

variable "environment" {
  description = "Deployment environment (development, staging, production)"
  type        = string
  
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production."
  }
}

#--------------------------------------------------------------
# Network Configuration Variables
#--------------------------------------------------------------

variable "vpc_id" {
  description = "ID of the VPC where security resources will be created"
  type        = string
  
  validation {
    condition     = can(regex("^vpc-", var.vpc_id))
    error_message = "VPC ID must be a valid VPC identifier starting with 'vpc-'."
  }
}

variable "vpc_cidr" {
  description = "CIDR block of the VPC for security group rules"
  type        = string
  
  validation {
    condition     = can(cidrnetmask(var.vpc_cidr))
    error_message = "VPC CIDR block must be a valid CIDR notation."
  }
}

variable "allowed_cidr_blocks" {
  description = "List of CIDR blocks allowed to access the ALB"
  type        = list(string)
  default     = ["0.0.0.0/0"]
  
  validation {
    condition     = alltrue([for cidr in var.allowed_cidr_blocks : can(cidrnetmask(cidr))])
    error_message = "All CIDR blocks must be valid CIDR notation."
  }
}

#--------------------------------------------------------------
# Port Configuration Variables
#--------------------------------------------------------------

variable "backend_container_port" {
  description = "Port the backend container listens on"
  type        = number
  default     = 8000
  
  validation {
    condition     = var.backend_container_port > 0 && var.backend_container_port < 65536
    error_message = "Backend container port must be between 1 and 65535."
  }
}

variable "frontend_container_port" {
  description = "Port the frontend container listens on"
  type        = number
  default     = 80
  
  validation {
    condition     = var.frontend_container_port > 0 && var.frontend_container_port < 65536
    error_message = "Frontend container port must be between 1 and 65535."
  }
}

variable "db_port" {
  description = "Port the PostgreSQL database listens on"
  type        = number
  default     = 5432
  
  validation {
    condition     = var.db_port > 0 && var.db_port < 65536
    error_message = "Database port must be between 1 and 65535."
  }
}

variable "redis_port" {
  description = "Port the Redis ElastiCache cluster listens on"
  type        = number
  default     = 6379
  
  validation {
    condition     = var.redis_port > 0 && var.redis_port < 65536
    error_message = "Redis port must be between 1 and 65535."
  }
}

#--------------------------------------------------------------
# Storage Configuration Variables
#--------------------------------------------------------------

variable "document_bucket_name" {
  description = "Base name of the S3 bucket for document storage (will be appended with environment)"
  type        = string
  
  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$", var.document_bucket_name))
    error_message = "S3 bucket name must follow AWS S3 bucket naming rules."
  }
}

variable "log_bucket_name" {
  description = "Base name of the S3 bucket for logs (will be appended with environment)"
  type        = string
  
  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$", var.log_bucket_name))
    error_message = "S3 bucket name must follow AWS S3 bucket naming rules."
  }
}

#--------------------------------------------------------------
# WAF Configuration Variables
#--------------------------------------------------------------

variable "enable_waf" {
  description = "Whether to enable WAF for the application load balancer"
  type        = bool
  default     = true
}

variable "alb_arn" {
  description = "ARN of the Application Load Balancer to associate with WAF"
  type        = string
  default     = ""
}

variable "waf_rate_limit" {
  description = "Request rate limit for WAF rate-based rules"
  type        = number
  default     = 1000
  
  validation {
    condition     = var.waf_rate_limit > 0
    error_message = "WAF rate limit must be a positive number."
  }
}

#--------------------------------------------------------------
# KMS Configuration Variables
#--------------------------------------------------------------

variable "kms_key_deletion_window" {
  description = "Number of days to wait before deleting a KMS key that has been scheduled for deletion"
  type        = number
  default     = 30
  
  validation {
    condition     = var.kms_key_deletion_window >= 7 && var.kms_key_deletion_window <= 30
    error_message = "KMS key deletion window must be between 7 and 30 days."
  }
}

variable "kms_key_rotation_enabled" {
  description = "Whether to enable automatic rotation for the KMS key"
  type        = bool
  default     = true
}

#--------------------------------------------------------------
# Parameter Store Variables
#--------------------------------------------------------------

variable "ssm_parameter_prefix" {
  description = "Prefix for SSM parameters used by the application"
  type        = string
  default     = "loan-management-system"
  
  validation {
    condition     = can(regex("^[a-zA-Z0-9./_-]{1,1011}$", var.ssm_parameter_prefix))
    error_message = "SSM parameter prefix must follow AWS Parameter Store naming rules."
  }
}