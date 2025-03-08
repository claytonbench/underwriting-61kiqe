# Terraform configuration for Loan Management System - Development Environment
# This file defines the development environment infrastructure using Terraform

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.4"
    }
  }

  required_version = ">= 1.2.0"

  backend "s3" {
    bucket         = "loan-management-system-terraform-state-dev"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "loan-management-system-terraform-locks-dev"
    encrypt        = true
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
  
  default_tags {
    tags = {
      Environment = "development"
      Project     = "LoanManagementSystem"
      ManagedBy   = "Terraform"
      CostCenter  = "Development"
    }
  }
}

module "loan_management_system" {
  source = "../../"

  # Environment Configuration
  environment              = "development"
  aws_region               = "us-east-1"
  aws_profile              = "development"
  project_name             = "loan-management-system"
  terraform_state_bucket   = "loan-management-system-terraform-state-dev"
  terraform_lock_table     = "loan-management-system-terraform-locks-dev"

  # Network Configuration
  vpc_cidr                 = "10.0.0.0/16"
  availability_zones       = ["us-east-1a", "us-east-1b"]
  public_subnet_cidrs      = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnet_cidrs     = ["10.0.3.0/24", "10.0.4.0/24"]
  database_subnet_cidrs    = ["10.0.5.0/24", "10.0.6.0/24"]
  enable_nat_gateway       = true
  single_nat_gateway       = true

  # Database Configuration
  db_name                  = "loanmgmt"
  db_username              = "dbadmin"
  db_password              = var.db_password
  db_instance_class        = "db.t3.small"
  db_allocated_storage     = 20
  db_engine                = "postgres"
  db_engine_version        = "15.3"
  db_multi_az              = false
  db_backup_retention_period = 7
  db_deletion_protection   = false

  # Redis Configuration
  redis_node_type          = "cache.t3.small"
  redis_engine_version     = "7.0"
  redis_parameter_group_name = "default.redis7"
  redis_num_cache_clusters = 1

  # S3 Configuration
  document_bucket_name     = "loan-management-system-documents-dev"
  log_bucket_name          = "loan-management-system-logs-dev"
  enable_s3_versioning     = true
  enable_s3_encryption     = true

  # Container Configuration
  backend_container_image  = var.backend_container_image
  frontend_container_image = var.frontend_container_image
  backend_container_cpu    = 512
  backend_container_memory = 1024
  frontend_container_cpu   = 256
  frontend_container_memory = 512
  backend_container_port   = 8000
  frontend_container_port  = 80
  backend_desired_count    = 1
  frontend_desired_count   = 1
  backend_max_count        = 2
  frontend_max_count       = 2
  backend_cpu_threshold    = 70
  frontend_cpu_threshold   = 70

  # Security Configuration
  enable_waf               = true
  enable_cloudfront        = true
  cloudfront_price_class   = "PriceClass_100"
  enable_disaster_recovery = false
  enable_monitoring        = true
  alarm_email              = "dev-alerts@example.com"
  certificate_arn          = var.certificate_arn

  # Reference to outputs (this would typically be populated by the module)
  alarm_sns_topic_arn      = module.loan_management_system.alarm_sns_topic_arn

  # Tags
  tags = {
    Environment = "development"
    Project     = "LoanManagementSystem"
    ManagedBy   = "Terraform"
    CostCenter  = "Development"
  }
}

variable "aws_region" {
  description = "AWS region where resources will be created"
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "AWS CLI profile to use for authentication"
  type        = string
  default     = "development"
}

variable "db_password" {
  description = "Password for the database"
  type        = string
  sensitive   = true
}

variable "backend_container_image" {
  description = "Docker image for the backend container"
  type        = string
  default     = "123456789012.dkr.ecr.us-east-1.amazonaws.com/loan-management-backend:dev"
}

variable "frontend_container_image" {
  description = "Docker image for the frontend container"
  type        = string
  default     = "123456789012.dkr.ecr.us-east-1.amazonaws.com/loan-management-frontend:dev"
}

variable "certificate_arn" {
  description = "ARN of the SSL certificate for HTTPS"
  type        = string
  default     = ""
}

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