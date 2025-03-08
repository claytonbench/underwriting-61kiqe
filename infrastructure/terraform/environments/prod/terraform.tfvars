environment               = "production"
aws_region                = "us-east-1"
aws_profile               = "production"
project_name              = "loan-management-system"

# Terraform State Management
terraform_state_bucket    = "loan-management-system-terraform-state-prod"
terraform_lock_table      = "loan-management-system-terraform-locks-prod"

# VPC Configuration
vpc_cidr                  = "10.0.0.0/16"
availability_zones        = ["us-east-1a", "us-east-1b", "us-east-1c"]
public_subnet_cidrs       = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
private_subnet_cidrs      = ["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"]
database_subnet_cidrs     = ["10.0.7.0/24", "10.0.8.0/24", "10.0.9.0/24"]
enable_nat_gateway        = true
single_nat_gateway        = false  # Use multiple NAT Gateways for HA
enable_dns_hostnames      = true
enable_dns_support        = true

# Database Configuration
db_name                   = "loanmgmt"
db_username               = "dbadmin"
db_password               = "SENSITIVE_VALUE_PLACEHOLDER"  # Use parameter store in actual deployment
db_instance_class         = "db.r5.large"
db_allocated_storage      = 100
db_engine                 = "postgres"
db_engine_version         = "15.3"
db_multi_az               = true
db_backup_retention_period = 30
db_deletion_protection    = true
performance_insights_enabled = true
performance_insights_retention_period = 30
monitoring_interval       = 30
create_replica            = true
replica_instance_class    = "db.r5.large"

# Redis Configuration
redis_node_type           = "cache.m5.large"
redis_engine_version      = "7.0"
redis_parameter_group_name = "default.redis7"
redis_num_cache_clusters  = 3
redis_cluster_mode_enabled = true

# S3 Storage Configuration
document_bucket_name      = "loan-management-system-documents-prod"
log_bucket_name           = "loan-management-system-logs-prod"
enable_s3_versioning      = true
enable_s3_encryption      = true
s3_lifecycle_rules        = [
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
      days = 2555  # 7 years retention for compliance
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

# Container Configuration
backend_container_cpu     = 2048  # 2 vCPU
backend_container_memory  = 4096  # 4GB
frontend_container_cpu    = 1024  # 1 vCPU
frontend_container_memory = 2048  # 2GB
backend_container_port    = 8000
frontend_container_port   = 80

# Auto-scaling Configuration
backend_desired_count     = 4
frontend_desired_count    = 4
backend_max_count         = 12
frontend_max_count        = 12
backend_cpu_threshold     = 70
frontend_cpu_threshold    = 70

# Security Configuration
enable_waf                = true
waf_rule_names            = [
  "AWSManagedRulesCommonRuleSet",
  "AWSManagedRulesKnownBadInputsRuleSet",
  "AWSManagedRulesSQLiRuleSet",
  "AWSManagedRulesLinuxRuleSet",
  "AWSManagedRulesAmazonIpReputationList"
]

# CDN Configuration
enable_cloudfront         = true
cloudfront_price_class    = "PriceClass_200"  # North America and Europe

# Disaster Recovery Configuration
enable_disaster_recovery  = true
dr_region                 = "us-west-2"

# Monitoring Configuration
enable_monitoring         = true
alarm_email               = "production-alerts@example.com"

# Container Images
backend_container_image   = "123456789012.dkr.ecr.us-east-1.amazonaws.com/loan-management-backend:production"
frontend_container_image  = "123456789012.dkr.ecr.us-east-1.amazonaws.com/loan-management-frontend:production"

# SSL Configuration
certificate_arn           = "arn:aws:acm:us-east-1:123456789012:certificate/abcd1234-ef56-gh78-ij90-klmnopqrstuv"

# Deployment Configuration
health_check_grace_period_seconds = 120
deployment_maximum_percent = 200
deployment_minimum_healthy_percent = 100

# Resource Tagging
tags = {
  Environment = "production"
  Project = "LoanManagementSystem"
  ManagedBy = "Terraform"
  DataClassification = "Sensitive"
  CostCenter = "Production"
  BusinessUnit = "Lending"
}