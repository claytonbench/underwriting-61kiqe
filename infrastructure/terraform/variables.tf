# Basic Settings
variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "The AWS region where resources will be created"
  
  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[0-9]{1}$", var.aws_region))
    error_message = "Must be a valid AWS region identifier."
  }
}

variable "environment" {
  type        = string
  default     = "development"
  description = "Deployment environment (development, staging, production)"
  
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Must be one of: development, staging, production."
  }
}

variable "project_name" {
  type        = string
  default     = "loan-management-system"
  description = "Name of the project, used for resource naming and tagging"
}

# Networking
variable "vpc_cidr" {
  type        = string
  default     = "10.0.0.0/16"
  description = "CIDR block for the VPC"
}

variable "availability_zones" {
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
  description = "List of availability zones to use for resources"
}

variable "public_subnet_cidrs" {
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
  description = "CIDR blocks for the public subnets"
}

variable "private_app_subnet_cidrs" {
  type        = list(string)
  default     = ["10.0.3.0/24", "10.0.4.0/24"]
  description = "CIDR blocks for the private application subnets"
}

variable "private_data_subnet_cidrs" {
  type        = list(string)
  default     = ["10.0.5.0/24", "10.0.6.0/24"]
  description = "CIDR blocks for the private data subnets"
}

variable "enable_nat_gateway" {
  type        = bool
  default     = true
  description = "Whether to create NAT Gateways for private subnets"
}

variable "single_nat_gateway" {
  type        = bool
  default     = false
  description = "Whether to use a single NAT Gateway for all private subnets"
}

variable "enable_dns_hostnames" {
  type        = bool
  default     = true
  description = "Whether to enable DNS hostnames in the VPC"
}

variable "enable_dns_support" {
  type        = bool
  default     = true
  description = "Whether to enable DNS support in the VPC"
}

# Database
variable "db_instance_class" {
  type        = string
  default     = "db.t3.medium"
  description = "RDS instance type for the database"
}

variable "db_allocated_storage" {
  type        = number
  default     = 100
  description = "Allocated storage for the RDS instance in GB"
}

variable "db_engine" {
  type        = string
  default     = "postgres"
  description = "Database engine to use"
}

variable "db_engine_version" {
  type        = string
  default     = "15.3"
  description = "Version of the database engine"
}

variable "db_name" {
  type        = string
  default     = "loanmgmt"
  description = "Name of the database to create"
}

variable "db_username" {
  type        = string
  description = "Username for the database"
  sensitive   = true
}

variable "db_password" {
  type        = string
  description = "Password for the database"
  sensitive   = true
}

variable "db_multi_az" {
  type        = bool
  default     = true
  description = "Whether to enable Multi-AZ deployment for RDS"
}

variable "db_backup_retention_period" {
  type        = number
  default     = 30
  description = "Number of days to retain database backups"
}

variable "db_deletion_protection" {
  type        = bool
  default     = true
  description = "Whether to enable deletion protection for the database"
}

# Redis Cache
variable "redis_node_type" {
  type        = string
  default     = "cache.t3.medium"
  description = "ElastiCache Redis node type"
}

variable "redis_engine_version" {
  type        = string
  default     = "7.0"
  description = "ElastiCache Redis engine version"
}

variable "redis_cluster_mode_enabled" {
  type        = bool
  default     = true
  description = "Whether to enable cluster mode for Redis"
}

variable "redis_num_cache_clusters" {
  type        = number
  default     = 2
  description = "Number of Redis cache clusters"
}

# Storage
variable "document_bucket_name" {
  type        = string
  default     = ""
  description = "Name of the S3 bucket for document storage"
}

variable "enable_s3_versioning" {
  type        = bool
  default     = true
  description = "Whether to enable versioning for S3 buckets"
}

variable "enable_s3_encryption" {
  type        = bool
  default     = true
  description = "Whether to enable server-side encryption for S3 buckets"
}

variable "s3_lifecycle_rules" {
  type = list(object({
    name     = string
    enabled  = bool
    prefix   = string
    transition = list(object({
      days          = number
      storage_class = string
    }))
    expiration = object({
      days = number
    })
  }))
  default     = []
  description = "Lifecycle rules for S3 buckets"
}

# ECS Service
variable "ecs_task_cpu" {
  type        = number
  default     = 1024
  description = "CPU units for ECS tasks (1024 = 1 vCPU)"
}

variable "ecs_task_memory" {
  type        = number
  default     = 2048
  description = "Memory for ECS tasks in MB"
}

variable "backend_container_port" {
  type        = number
  default     = 8000
  description = "Port the backend container listens on"
}

variable "frontend_container_port" {
  type        = number
  default     = 80
  description = "Port the frontend container listens on"
}

variable "backend_desired_count" {
  type        = number
  default     = 2
  description = "Desired count of backend tasks"
}

variable "frontend_desired_count" {
  type        = number
  default     = 2
  description = "Desired count of frontend tasks"
}

variable "backend_max_count" {
  type        = number
  default     = 10
  description = "Maximum count of backend tasks for auto-scaling"
}

variable "frontend_max_count" {
  type        = number
  default     = 10
  description = "Maximum count of frontend tasks for auto-scaling"
}

variable "backend_cpu_threshold" {
  type        = number
  default     = 70
  description = "CPU utilization threshold for backend auto-scaling"
}

variable "frontend_cpu_threshold" {
  type        = number
  default     = 70
  description = "CPU utilization threshold for frontend auto-scaling"
}

# Security
variable "enable_waf" {
  type        = bool
  default     = true
  description = "Whether to enable WAF for the application load balancer"
}

variable "waf_rule_names" {
  type        = list(string)
  default     = ["AWSManagedRulesCommonRuleSet", "AWSManagedRulesKnownBadInputsRuleSet", "AWSManagedRulesSQLiRuleSet"]
  description = "List of AWS managed WAF rule sets to apply"
}

# Content Delivery
variable "enable_cloudfront" {
  type        = bool
  default     = true
  description = "Whether to create a CloudFront distribution for the frontend"
}

variable "cloudfront_price_class" {
  type        = string
  default     = "PriceClass_100"
  description = "CloudFront price class (PriceClass_100, PriceClass_200, PriceClass_All)"
  
  validation {
    condition     = contains(["PriceClass_100", "PriceClass_200", "PriceClass_All"], var.cloudfront_price_class)
    error_message = "Must be one of: PriceClass_100, PriceClass_200, PriceClass_All."
  }
}

# Disaster Recovery
variable "enable_disaster_recovery" {
  type        = bool
  default     = false
  description = "Whether to enable cross-region disaster recovery"
}

variable "dr_region" {
  type        = string
  default     = "us-west-2"
  description = "AWS region for disaster recovery"
  
  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[0-9]{1}$", var.dr_region))
    error_message = "Must be a valid AWS region identifier."
  }
}

# Monitoring
variable "enable_monitoring" {
  type        = bool
  default     = true
  description = "Whether to enable enhanced monitoring and alerting"
}

variable "alarm_email" {
  type        = string
  default     = ""
  description = "Email address for CloudWatch alarms"
}

# Tagging
variable "tags" {
  type        = map(string)
  default     = {}
  description = "Additional tags to apply to all resources"
}