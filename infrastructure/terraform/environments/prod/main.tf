# Terraform configuration for the production environment of the loan management system
# This file initializes the backend, sets up providers, and calls the root module with production-specific configurations

# Configure the Terraform backend to store state in S3
terraform {
  backend "s3" {
    bucket         = "loan-management-system-terraform-state-prod"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "loan-management-system-terraform-locks-prod"
    encrypt        = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws" # version ~> 4.16
      version = "~> 4.16"
    }
    random = {
      source  = "hashicorp/random" # version ~> 3.4
      version = "~> 3.4"
    }
  }

  required_version = ">= 1.2.0"
}

# Configure the AWS provider
provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile

  default_tags {
    tags = {
      Environment        = "production"
      Project            = "LoanManagementSystem"
      ManagedBy          = "Terraform"
      DataClassification = "Sensitive"
      BusinessCriticality = "High"
      CostCenter         = "Production"
    }
  }
}

# Call the main loan management system module with production-specific configurations
module "loan_management_system" {
  source = "loan-management-system/module" # version 1.0.0

  # General configuration
  environment              = "production"
  aws_region               = var.aws_region
  aws_profile              = var.aws_profile
  project_name             = "loan-management-system"
  terraform_state_bucket   = "loan-management-system-terraform-state-prod"
  terraform_lock_table     = "loan-management-system-terraform-locks-prod"

  # Networking configuration
  vpc_cidr                 = "10.0.0.0/16"
  availability_zones       = ["us-east-1a", "us-east-1b", "us-east-1c"]
  public_subnet_cidrs      = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  private_subnet_cidrs     = ["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"]
  database_subnet_cidrs    = ["10.0.7.0/24", "10.0.8.0/24", "10.0.9.0/24"]
  enable_nat_gateway       = true
  single_nat_gateway       = false  # Use multiple NAT gateways for high availability

  # Database configuration
  db_name                     = "loanmgmt"
  db_username                 = "dbadmin"
  db_password                 = var.db_password
  db_instance_class           = "db.m5.large"
  db_allocated_storage        = 100
  db_engine                   = "postgres"
  db_engine_version           = "15.3"
  db_multi_az                 = true  # Enable multi-AZ for high availability
  db_backup_retention_period  = 30    # Retain backups for 30 days
  db_deletion_protection      = true  # Protect against accidental deletion

  # Redis cache configuration
  redis_node_type             = "cache.m5.large"
  redis_engine_version        = "7.0"
  redis_parameter_group_name  = "default.redis7"
  redis_num_cache_clusters    = 3     # Deploy across multiple AZs

  # S3 bucket configuration
  document_bucket_name        = "loan-management-system-documents-prod"
  log_bucket_name             = "loan-management-system-logs-prod"
  enable_s3_versioning        = true
  enable_s3_encryption        = true
  
  # S3 lifecycle rules
  s3_lifecycle_rules = [
    {
      name = "archive-documents"
      enabled = true
      prefix = "documents/"
      transition = [
        {
          days = 90
          storage_class = "STANDARD_IA"
        },
        {
          days = 365
          storage_class = "GLACIER"
        }
      ]
      expiration = {
        days = 2555  # ~7 years retention for compliance
      }
    },
    {
      name = "archive-logs"
      enabled = true
      prefix = "logs/"
      transition = [
        {
          days = 30
          storage_class = "STANDARD_IA"
        },
        {
          days = 90
          storage_class = "GLACIER"
        }
      ]
      expiration = {
        days = 730  # 2 years retention for logs
      }
    }
  ]

  # Container configuration
  backend_container_image     = var.backend_container_image
  frontend_container_image    = var.frontend_container_image
  backend_container_cpu       = 2048  # 2 vCPU
  backend_container_memory    = 4096  # 4 GB
  frontend_container_cpu      = 1024  # 1 vCPU
  frontend_container_memory   = 2048  # 2 GB
  backend_container_port      = 8000
  frontend_container_port     = 80
  
  # Auto-scaling configuration
  backend_desired_count       = 4
  frontend_desired_count      = 4
  backend_max_count           = 12
  frontend_max_count          = 12
  backend_cpu_threshold       = 70  # Scale out at 70% CPU utilization
  frontend_cpu_threshold      = 70  # Scale out at 70% CPU utilization

  # Security configuration
  enable_waf                  = true
  waf_rule_names              = [
    "AWSManagedRulesCommonRuleSet",
    "AWSManagedRulesKnownBadInputsRuleSet", 
    "AWSManagedRulesSQLiRuleSet",
    "AWSManagedRulesLinuxRuleSet",
    "AWSManagedRulesPHPRuleSet"
  ]

  # CDN configuration
  enable_cloudfront           = true
  cloudfront_price_class      = "PriceClass_All"  # Deploy to all edge locations

  # Disaster recovery configuration
  enable_disaster_recovery    = true
  dr_region                   = "us-west-2"  # Use US West as DR region

  # Monitoring configuration
  enable_monitoring           = true
  alarm_email                 = "production-alerts@loanmanagementsystem.com"
  certificate_arn             = var.certificate_arn
  alarm_sns_topic_arn         = module.loan_management_system.alarm_sns_topic_arn

  # Additional tags
  tags = {
    Environment          = "production"
    Project              = "LoanManagementSystem"
    ManagedBy            = "Terraform"
    DataClassification   = "Sensitive"
    BusinessCriticality  = "High"
    CostCenter           = "Production"
  }
}

# Input variables
variable "aws_region" {
  description = "AWS region where resources will be created"
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "AWS CLI profile to use for authentication"
  type        = string
  default     = "production"
}

variable "db_password" {
  description = "Password for the database"
  type        = string
  sensitive   = true
}

variable "backend_container_image" {
  description = "Docker image for the backend container"
  type        = string
  default     = "123456789012.dkr.ecr.us-east-1.amazonaws.com/loan-management-backend:production"
}

variable "frontend_container_image" {
  description = "Docker image for the frontend container"
  type        = string
  default     = "123456789012.dkr.ecr.us-east-1.amazonaws.com/loan-management-frontend:production"
}

variable "certificate_arn" {
  description = "ARN of the SSL certificate for HTTPS"
  type        = string
  default     = ""
}

# Output values
output "vpc_id" {
  description = "ID of the VPC"
  value       = module.loan_management_system.vpc_id
}

output "alb_dns_name" {
  description = "DNS name of the application load balancer"
  value       = module.loan_management_system.alb_dns_name
}

output "rds_endpoint" {
  description = "Endpoint of the RDS database"
  value       = module.loan_management_system.rds_endpoint
}

output "redis_endpoint" {
  description = "Endpoint of the Redis cluster"
  value       = module.loan_management_system.redis_endpoint
}

output "document_bucket_name" {
  description = "Name of the S3 bucket for document storage"
  value       = module.loan_management_system.document_bucket_name
}

output "log_bucket_name" {
  description = "Name of the S3 bucket for logs"
  value       = module.loan_management_system.log_bucket_name
}

output "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = module.loan_management_system.cloudfront_domain_name
}

output "dr_region_resources" {
  description = "Resources created in the disaster recovery region"
  value       = module.loan_management_system.dr_region_resources
}