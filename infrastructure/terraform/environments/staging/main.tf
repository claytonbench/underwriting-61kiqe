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

  backend "s3" {
    bucket         = "loan-management-system-terraform-state-staging"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "loan-management-system-terraform-locks-staging"
    encrypt        = true
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
  
  default_tags {
    tags = {
      Environment = "staging"
      Project     = "LoanManagementSystem"
      ManagedBy   = "Terraform"
      CostCenter  = "PreProduction"
    }
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
  default     = "staging"
}

variable "db_password" {
  description = "Password for the database"
  type        = string
  sensitive   = true
}

variable "backend_container_image" {
  description = "Docker image for the backend container"
  type        = string
  default     = "loan-management-system/backend:staging"
}

variable "frontend_container_image" {
  description = "Docker image for the frontend container"
  type        = string
  default     = "loan-management-system/frontend:staging"
}

variable "certificate_arn" {
  description = "ARN of the SSL certificate for HTTPS"
  type        = string
  default     = ""
}

module "loan_management_system" {
  source = "../../"
  
  environment                 = "staging"
  aws_region                  = var.aws_region
  aws_profile                 = var.aws_profile
  project_name                = "loan-management-system"
  
  # State management
  terraform_state_bucket      = "loan-management-system-terraform-state-staging"
  terraform_lock_table        = "loan-management-system-terraform-locks-staging"
  
  # Networking
  vpc_cidr                    = "10.0.0.0/16"
  availability_zones          = ["us-east-1a", "us-east-1b", "us-east-1c"]
  public_subnet_cidrs         = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  private_subnet_cidrs        = ["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"]
  database_subnet_cidrs       = ["10.0.7.0/24", "10.0.8.0/24", "10.0.9.0/24"]
  enable_nat_gateway          = true
  single_nat_gateway          = false

  # Database
  db_name                     = "loanmgmt"
  db_username                 = "dbadmin"
  db_password                 = var.db_password
  db_instance_class           = "db.t3.medium"
  db_allocated_storage        = 50
  db_engine                   = "postgres"
  db_engine_version           = "15.3"
  db_multi_az                 = true
  db_backup_retention_period  = 14
  db_deletion_protection      = true
  
  # Redis
  redis_node_type             = "cache.t3.medium"
  redis_engine_version        = "7.0"
  redis_parameter_group_name  = "default.redis7"
  redis_num_cache_clusters    = 2
  
  # S3 Buckets
  document_bucket_name        = "loan-management-system-documents-staging"
  log_bucket_name             = "loan-management-system-logs-staging"
  enable_s3_versioning        = true
  enable_s3_encryption        = true
  
  # Container Configuration
  backend_container_image     = var.backend_container_image
  frontend_container_image    = var.frontend_container_image
  backend_container_cpu       = 1024
  backend_container_memory    = 2048
  frontend_container_cpu      = 512
  frontend_container_memory   = 1024
  backend_container_port      = 8000
  frontend_container_port     = 80
  backend_desired_count       = 2
  frontend_desired_count      = 2
  backend_max_count           = 6
  frontend_max_count          = 6
  backend_cpu_threshold       = 70
  frontend_cpu_threshold      = 70
  
  # Security
  enable_waf                  = true
  waf_rule_names              = ["AWSManagedRulesCommonRuleSet", "AWSManagedRulesKnownBadInputsRuleSet", "AWSManagedRulesSQLiRuleSet"]
  
  # CDN
  enable_cloudfront           = true
  cloudfront_price_class      = "PriceClass_100"
  
  # Disaster Recovery
  enable_disaster_recovery    = false
  
  # Monitoring
  enable_monitoring           = true
  alarm_email                 = "staging-alerts@example.com"
  
  # SSL/TLS
  certificate_arn             = var.certificate_arn
  
  # SNS Topic for Alarms
  alarm_sns_topic_arn         = module.loan_management_system.alarm_sns_topic_arn
  
  # Tags
  tags = {
    Environment = "staging"
    Project     = "LoanManagementSystem"
    ManagedBy   = "Terraform"
    CostCenter  = "PreProduction"
  }
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

output "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = module.loan_management_system.cloudfront_domain_name
}