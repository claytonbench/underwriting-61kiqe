# AWS ElastiCache Redis Module - v1.0.0
# This module creates a Redis replication group with appropriate configuration
# for the loan management system, including high availability, security,
# and monitoring features.

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
}

# Common tags to be applied to all resources
locals {
  common_tags = {
    Project     = "LoanManagementSystem"
    Environment = var.environment
    ManagedBy   = "Terraform"
    Component   = "ElastiCache"
  }
}

# Random ID for ElastiCache replication group name uniqueness
resource "random_id" "redis_id" {
  byte_length = 4
}

# ElastiCache Redis Replication Group
resource "aws_elasticache_replication_group" "redis" {
  replication_group_id          = "${lower(var.environment)}-redis-${random_id.redis_id.hex}"
  description                   = "Redis cluster for ${var.environment} environment"
  node_type                     = var.redis_node_type
  num_cache_clusters            = var.redis_num_cache_clusters
  parameter_group_name          = var.redis_parameter_group_name
  port                          = 6379
  subnet_group_name             = var.subnet_group_name
  security_group_ids            = var.security_group_ids
  engine_version                = var.redis_engine_version
  automatic_failover_enabled    = var.redis_num_cache_clusters > 1 ? true : false
  multi_az_enabled              = var.redis_num_cache_clusters > 1 ? true : false
  at_rest_encryption_enabled    = true
  transit_encryption_enabled    = var.redis_auth_token != "" ? true : false
  auth_token                    = var.redis_auth_token != "" ? var.redis_auth_token : null
  kms_key_id                    = var.kms_key_id != "" ? var.kms_key_id : null
  maintenance_window            = "sun:05:00-sun:09:00"
  snapshot_window               = "03:00-05:00"
  snapshot_retention_limit      = 7
  apply_immediately             = true
  auto_minor_version_upgrade    = true
  
  tags = merge(
    local.common_tags,
    {
      Name        = "${var.environment}-redis"
      Environment = var.environment
    }
  )
}

# CloudWatch alarm for Redis CPU utilization
resource "aws_cloudwatch_metric_alarm" "redis_cpu_utilization" {
  count               = var.enable_monitoring ? 1 : 0
  alarm_name          = "${var.environment}-redis-cpu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ElastiCache"
  period              = 300
  statistic           = "Average"
  threshold           = 75
  alarm_description   = "This metric monitors Redis CPU utilization"
  alarm_actions       = var.alarm_actions
  ok_actions          = var.alarm_actions
  
  dimensions = {
    ReplicationGroupId = aws_elasticache_replication_group.redis.id
  }
  
  tags = merge(
    local.common_tags,
    {
      Environment = var.environment
    }
  )
}

# CloudWatch alarm for Redis memory utilization
resource "aws_cloudwatch_metric_alarm" "redis_memory_utilization" {
  count               = var.enable_monitoring ? 1 : 0
  alarm_name          = "${var.environment}-redis-memory-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "DatabaseMemoryUsagePercentage"
  namespace           = "AWS/ElastiCache"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "This metric monitors Redis memory utilization"
  alarm_actions       = var.alarm_actions
  ok_actions          = var.alarm_actions
  
  dimensions = {
    ReplicationGroupId = aws_elasticache_replication_group.redis.id
  }
  
  tags = merge(
    local.common_tags,
    {
      Environment = var.environment
    }
  )
}

# CloudWatch alarm for Redis connection count
resource "aws_cloudwatch_metric_alarm" "redis_connections" {
  count               = var.enable_monitoring ? 1 : 0
  alarm_name          = "${var.environment}-redis-connections"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CurrConnections"
  namespace           = "AWS/ElastiCache"
  period              = 300
  statistic           = "Average"
  threshold           = var.redis_max_connections * 0.8
  alarm_description   = "This metric monitors Redis connection count"
  alarm_actions       = var.alarm_actions
  ok_actions          = var.alarm_actions
  
  dimensions = {
    ReplicationGroupId = aws_elasticache_replication_group.redis.id
  }
  
  tags = merge(
    local.common_tags,
    {
      Environment = var.environment
    }
  )
}