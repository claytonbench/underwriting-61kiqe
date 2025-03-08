# Main Terraform configuration file for the Loan Management System infrastructure

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
  
  # Note: Variables in backend configuration must be provided during terraform init
  # using -backend-config options or partial configuration
  backend "s3" {
    bucket         = var.terraform_state_bucket
    key            = "terraform.tfstate"
    region         = var.aws_region
    dynamodb_table = var.terraform_lock_table
    encrypt        = true
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
  
  default_tags {
    tags = {
      Environment = var.environment
      Project     = "LoanManagementSystem"
      ManagedBy   = "Terraform"
    }
  }
}

# Define common tags for resource identification and organization
locals {
  common_tags = {
    Project     = "LoanManagementSystem"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# VPC Module: Creates the network infrastructure with public/private subnets
module "vpc" {
  source = "./modules/vpc"
  
  environment            = var.environment
  aws_region             = var.aws_region
  vpc_cidr               = var.vpc_cidr
  availability_zones     = var.availability_zones
  public_subnet_cidrs    = var.public_subnet_cidrs
  private_subnet_cidrs   = var.private_subnet_cidrs
  database_subnet_cidrs  = var.database_subnet_cidrs
  enable_nat_gateway     = var.enable_nat_gateway
  single_nat_gateway     = var.single_nat_gateway
  flow_log_bucket_arn    = module.s3.log_bucket_arn
}

# Security Module: Sets up security groups, IAM roles, and WAF rules
module "security" {
  source = "./modules/security"
  
  environment          = var.environment
  vpc_id               = module.vpc.vpc_id
  vpc_cidr             = var.vpc_cidr
  document_bucket_name = var.document_bucket_name
  log_bucket_name      = var.log_bucket_name
  enable_waf           = var.enable_waf
  alb_arn              = module.ecs.alb_arn
}

# S3 Module: Sets up document storage and logging buckets
module "s3" {
  source = "./modules/s3"
  
  environment           = var.environment
  document_bucket_name  = var.document_bucket_name
  log_bucket_name       = var.log_bucket_name
  kms_key_id            = module.security.kms_key_id
  enable_s3_versioning  = var.enable_s3_versioning
  enable_s3_encryption  = var.enable_s3_encryption
  s3_lifecycle_rules    = var.s3_lifecycle_rules
}

# RDS Module: Creates the PostgreSQL database for the application
module "rds" {
  source = "./modules/rds"
  
  environment              = var.environment
  identifier               = "${var.environment}-postgres"
  vpc_id                   = module.vpc.vpc_id
  subnet_ids               = module.vpc.database_subnet_ids
  use_existing_subnet_group = false
  allowed_security_groups  = [module.security.app_security_group_id]
  
  engine                   = var.db_engine
  engine_version           = var.db_engine_version
  instance_class           = var.db_instance_class
  allocated_storage        = var.db_allocated_storage
  storage_encrypted        = true
  kms_key_id               = module.security.kms_key_id
  
  db_name                  = var.db_name
  username                 = var.db_username
  password                 = var.db_password
  
  multi_az                 = var.db_multi_az
  backup_retention_period  = var.db_backup_retention_period
  deletion_protection      = var.db_deletion_protection
  performance_insights_enabled = true
  
  create_cloudwatch_alarms = var.enable_monitoring
  alarm_actions            = [var.alarm_sns_topic_arn]
}

# ElastiCache Module: Sets up Redis for caching and session management
module "elasticache" {
  source = "./modules/elasticache"
  
  environment               = var.environment
  redis_node_type           = var.redis_node_type
  redis_engine_version      = var.redis_engine_version
  redis_parameter_group_name = var.redis_parameter_group_name
  subnet_group_name         = module.vpc.elasticache_subnet_group_name
  security_group_ids        = [module.security.elasticache_security_group_id]
  redis_num_cache_clusters  = var.redis_num_cache_clusters
  kms_key_id                = module.security.kms_key_id
  enable_monitoring         = var.enable_monitoring
  alarm_actions             = [var.alarm_sns_topic_arn]
}

# ECS Module: Deploys the application containers and load balancer
module "ecs" {
  source = "./modules/ecs"
  
  environment                 = var.environment
  aws_region                  = var.aws_region
  vpc_id                      = module.vpc.vpc_id
  public_subnet_ids           = module.vpc.public_subnet_ids
  private_subnet_ids          = module.vpc.private_subnet_ids
  app_security_group_id       = module.security.app_security_group_id
  alb_security_group_id       = module.security.alb_security_group_id
  ecs_task_execution_role_arn = module.security.ecs_task_execution_role_arn
  ecs_task_role_arn           = module.security.ecs_task_role_arn
  
  backend_container_image     = var.backend_container_image
  frontend_container_image    = var.frontend_container_image
  backend_container_port      = var.backend_container_port
  frontend_container_port     = var.frontend_container_port
  
  backend_container_cpu       = var.backend_container_cpu
  backend_container_memory    = var.backend_container_memory
  frontend_container_cpu      = var.frontend_container_cpu
  frontend_container_memory   = var.frontend_container_memory
  
  backend_desired_count       = var.backend_desired_count
  frontend_desired_count      = var.frontend_desired_count
  backend_max_count           = var.backend_max_count
  frontend_max_count          = var.frontend_max_count
  backend_cpu_threshold       = var.backend_cpu_threshold
  frontend_cpu_threshold      = var.frontend_cpu_threshold
  
  db_host                     = module.rds.db_instance_endpoint
  db_name                     = var.db_name
  db_username                 = var.db_username
  db_password                 = var.db_password
  redis_host                  = module.elasticache.redis_endpoint
  document_bucket_name        = module.s3.document_bucket_name
  
  certificate_arn             = var.certificate_arn
  enable_cloudfront           = var.enable_cloudfront
  cloudfront_price_class      = var.cloudfront_price_class
  
  alarm_sns_topic_arn         = var.alarm_sns_topic_arn
}

# Monitoring Module: Sets up CloudWatch dashboards, alarms, and alerts
module "monitoring" {
  source = "./modules/monitoring"
  
  environment                    = var.environment
  enable_monitoring              = var.enable_monitoring
  alarm_email                    = var.alarm_email
  
  vpc_id                         = module.vpc.vpc_id
  rds_instance_id                = module.rds.db_instance_id
  elasticache_replication_group_id = module.elasticache.redis_replication_group_id
  ecs_cluster_name               = module.ecs.ecs_cluster_name
  backend_service_name           = module.ecs.backend_service_name
  frontend_service_name          = module.ecs.frontend_service_name
  alb_arn_suffix                 = module.ecs.alb_arn_suffix
  document_bucket_name           = module.s3.document_bucket_name
  log_bucket_name                = module.s3.log_bucket_name
  
  count = var.enable_monitoring ? 1 : 0
}