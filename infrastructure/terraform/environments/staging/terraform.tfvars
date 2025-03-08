# Environment Identification
environment             = "staging"
aws_region              = "us-east-1"
aws_profile             = "staging"
project_name            = "loan-management-system"

# Terraform State Management
terraform_state_bucket  = "loan-management-system-terraform-state-staging"
terraform_lock_table    = "loan-management-system-terraform-locks-staging"

# VPC and Networking Configuration
vpc_cidr                = "10.0.0.0/16"
availability_zones      = ["us-east-1a", "us-east-1b", "us-east-1c"]
public_subnet_cidrs     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
private_subnet_cidrs    = ["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"]
database_subnet_cidrs   = ["10.0.7.0/24", "10.0.8.0/24", "10.0.9.0/24"]
enable_nat_gateway      = true
single_nat_gateway      = false
enable_dns_hostnames    = true
enable_dns_support      = true

# Database Configuration
db_name                  = "loanmgmt"
db_username              = "dbadmin"
db_password              = "SENSITIVE_VALUE_PLACEHOLDER"
db_instance_class        = "db.t3.medium"
db_allocated_storage     = 50
db_engine                = "postgres"
db_engine_version        = "15.3"
db_multi_az              = true
db_backup_retention_period = 14
db_deletion_protection   = true

# Redis Cache Configuration
redis_node_type           = "cache.t3.medium"
redis_engine_version      = "7.0"
redis_parameter_group_name = "default.redis7"
redis_num_cache_clusters  = 2

# S3 Storage Configuration
document_bucket_name      = "loan-management-system-documents-staging"
log_bucket_name           = "loan-management-system-logs-staging"
enable_s3_versioning      = true
enable_s3_encryption      = true

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
      days = 2555
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
      days = 730
    }
  }
]

# Container Resource Configuration
backend_container_cpu    = 1024  # 1 vCPU
backend_container_memory = 2048  # 2GB
frontend_container_cpu   = 512   # 0.5 vCPU
frontend_container_memory = 1024  # 1GB
backend_container_port   = 8000
frontend_container_port  = 80

# Auto-scaling Configuration
backend_desired_count    = 2
frontend_desired_count   = 2
backend_max_count        = 6
frontend_max_count       = 6
backend_cpu_threshold    = 70
frontend_cpu_threshold   = 70

# WAF and CloudFront Configuration
enable_waf               = true
waf_rule_names           = ["AWSManagedRulesCommonRuleSet", "AWSManagedRulesKnownBadInputsRuleSet", "AWSManagedRulesSQLiRuleSet"]
enable_cloudfront        = true
cloudfront_price_class   = "PriceClass_100"

# Disaster Recovery Configuration
enable_disaster_recovery = false  # Disabled for staging

# Monitoring and Alerting
enable_monitoring        = true
alarm_email              = "staging-alerts@example.com"

# Container Images
backend_container_image  = "123456789012.dkr.ecr.us-east-1.amazonaws.com/loan-management-backend:staging"
frontend_container_image = "123456789012.dkr.ecr.us-east-1.amazonaws.com/loan-management-frontend:staging"

# SSL Certificate
certificate_arn          = "arn:aws:acm:us-east-1:123456789012:certificate/abcd1234-ef56-gh78-ij90-klmnopqrstuv"

# Resource Tagging
tags = {
  Environment = "staging"
  Project = "LoanManagementSystem"
  ManagedBy = "Terraform"
  DataClassification = "Sensitive"
  CostCenter = "PreProduction"
}