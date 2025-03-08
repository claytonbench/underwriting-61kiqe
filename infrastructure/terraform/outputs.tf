# Output values from the root module
# These provide important information about created resources for reference and integration

# VPC and Networking outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = module.vpc.private_subnet_ids
}

output "database_subnet_ids" {
  description = "List of database subnet IDs"
  value       = module.vpc.database_subnet_ids
}

# Application Load Balancer outputs
output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = module.ecs.alb_dns_name
}

output "alb_zone_id" {
  description = "Route 53 zone ID of the Application Load Balancer"
  value       = module.ecs.alb_zone_id
}

# CloudFront output (conditional)
output "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = var.enable_cloudfront ? module.ecs.cloudfront_domain_name : null
}

# Database outputs
output "db_endpoint" {
  description = "Endpoint of the RDS database"
  value       = module.rds.db_instance_endpoint
}

output "db_name" {
  description = "Name of the database"
  value       = module.rds.db_instance_name
}

output "db_username" {
  description = "Username for the database"
  value       = module.rds.db_instance_username
}

# Redis outputs
output "redis_endpoint" {
  description = "Endpoint of the Redis cluster"
  value       = module.elasticache.redis_endpoint
}

output "redis_port" {
  description = "Port of the Redis cluster"
  value       = module.elasticache.redis_port
}

# S3 bucket outputs
output "document_bucket_name" {
  description = "Name of the S3 bucket for document storage"
  value       = module.s3.document_bucket_name
}

output "log_bucket_name" {
  description = "Name of the S3 bucket for logs"
  value       = module.s3.log_bucket_name
}

# Security outputs
output "kms_key_id" {
  description = "ID of the KMS key for encryption"
  value       = module.security.kms_key_id
}

# ECS outputs
output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = module.ecs.cluster_name
}

output "backend_service_name" {
  description = "Name of the backend ECS service"
  value       = module.ecs.backend_service_name
}

output "frontend_service_name" {
  description = "Name of the frontend ECS service"
  value       = module.ecs.frontend_service_name
}

# WAF output (conditional)
output "web_acl_arn" {
  description = "ARN of the WAF Web ACL"
  value       = var.enable_waf ? module.security.web_acl_arn : null
}

# Security group outputs
output "app_security_group_id" {
  description = "ID of the security group for application containers"
  value       = module.security.app_security_group_id
}

output "database_security_group_id" {
  description = "ID of the security group for the database"
  value       = module.security.database_security_group_id
}

output "elasticache_security_group_id" {
  description = "ID of the security group for ElastiCache"
  value       = module.security.elasticache_security_group_id
}

# Disaster recovery output (conditional)
output "document_bucket_replica_name" {
  description = "Name of the replica S3 bucket for document storage"
  value       = var.enable_disaster_recovery ? module.s3.document_bucket_replica_name : null
}

# Environment output
output "environment" {
  description = "Deployment environment name"
  value       = var.environment
}