environment         = "development"
aws_region          = "us-east-1"
aws_profile         = "development"
project_name        = "loan-management-system"

# Terraform State Management
terraform_state_bucket = "loan-management-system-terraform-state-dev"
terraform_lock_table   = "loan-management-system-terraform-locks-dev"

# VPC and Networking
vpc_cidr              = "10.0.0.0/16"
availability_zones    = ["us-east-1a", "us-east-1b"]
public_subnet_cidrs   = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnet_cidrs  = ["10.0.3.0/24", "10.0.4.0/24"]
database_subnet_cidrs = ["10.0.5.0/24", "10.0.6.0/24"]
enable_nat_gateway    = true
single_nat_gateway    = true  # Cost optimization for development

# RDS Database Configuration
db_name                   = "loanmgmt"
db_username               = "dbadmin"
db_instance_class         = "db.t3.small"  # Smaller instance for development
db_allocated_storage      = 20  # Smaller storage for development
db_engine                 = "postgres"
db_engine_version         = "15.3"
db_multi_az               = false  # Disabled for development to reduce costs
db_backup_retention_period = 7  # Shorter retention for development
db_deletion_protection     = false  # Disabled for development environment

# Redis Cache Configuration
redis_node_type            = "cache.t3.small"  # Smaller instance for development
redis_engine_version       = "7.0"
redis_parameter_group_name = "default.redis7"
redis_num_cache_clusters   = 1  # Single node for development

# S3 Storage Configuration
document_bucket_name = "loan-management-system-documents-dev"
log_bucket_name      = "loan-management-system-logs-dev"
enable_s3_versioning = true
enable_s3_encryption = true

# ECS Container Configuration - Backend
backend_container_cpu        = 512  # 0.5 vCPU
backend_container_memory     = 1024  # 1GB
backend_container_port       = 8000
backend_desired_count        = 1  # Single instance for development
backend_max_count            = 2  # Limited auto-scaling for development
backend_cpu_threshold        = 70

# ECS Container Configuration - Frontend
frontend_container_cpu       = 256  # 0.25 vCPU
frontend_container_memory    = 512  # 0.5GB 
frontend_container_port      = 80
frontend_desired_count       = 1  # Single instance for development
frontend_max_count           = 2  # Limited auto-scaling for development
frontend_cpu_threshold       = 70

# Security and CDN Configuration
enable_waf                  = true
enable_cloudfront           = true
cloudfront_price_class      = "PriceClass_100"  # Lowest cost option for development

# Disaster Recovery and Monitoring
enable_disaster_recovery    = false  # Disabled for development
enable_monitoring           = true
alarm_email                 = "dev-alerts@example.com"

# Container Images
backend_container_image     = "123456789012.dkr.ecr.us-east-1.amazonaws.com/loan-management-backend:dev"
frontend_container_image    = "123456789012.dkr.ecr.us-east-1.amazonaws.com/loan-management-frontend:dev"

# Resource Tagging
tags = {
  Environment = "development"
  Project     = "LoanManagementSystem"
  ManagedBy   = "Terraform"
  CostCenter  = "Development"
}