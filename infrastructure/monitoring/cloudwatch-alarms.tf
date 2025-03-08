# CloudWatch Alarms for the Loan Management System
# This file defines comprehensive alerting for various AWS resources with appropriate thresholds
# HashiCorp/aws provider version: ~> 4.16

# Variables for CloudWatch alarm configuration
variable "environment" {
  type        = string
  description = "Deployment environment (development, staging, production)"
  default     = "development"
}

variable "region" {
  type        = string
  description = "AWS region where resources are deployed"
  default     = "us-east-1"
}

variable "sns_topic_arn" {
  type        = string
  description = "ARN of the SNS topic for alarm notifications"
  default     = ""
}

# ECS variables
variable "ecs_cluster_name" {
  type        = string
  description = "Name of the ECS cluster"
  default     = ""
}

variable "backend_service_name" {
  type        = string
  description = "Name of the backend ECS service"
  default     = ""
}

variable "frontend_service_name" {
  type        = string
  description = "Name of the frontend ECS service"
  default     = ""
}

# RDS variables
variable "db_instance_identifier" {
  type        = string
  description = "Identifier of the RDS database instance"
  default     = ""
}

variable "db_replica_identifier" {
  type        = string
  description = "Identifier of the RDS read replica instance"
  default     = ""
}

variable "rds_free_storage_threshold" {
  type        = number
  description = "Threshold for RDS free storage space in bytes"
  default     = 5368709120 # 5 GB
}

variable "rds_free_memory_threshold" {
  type        = number
  description = "Threshold for RDS free memory in bytes"
  default     = 1073741824 # 1 GB
}

variable "rds_connection_count_threshold" {
  type        = number
  description = "Threshold for RDS database connections"
  default     = 100
}

# ElastiCache variables
variable "redis_replication_group_id" {
  type        = string
  description = "ID of the ElastiCache Redis replication group"
  default     = ""
}

variable "redis_max_connections" {
  type        = number
  description = "Maximum number of connections for Redis"
  default     = 1000
}

# ALB variables
variable "alb_name" {
  type        = string
  description = "Name of the Application Load Balancer"
  default     = ""
}

# S3 variables
variable "document_bucket_name" {
  type        = string
  description = "Name of the S3 bucket for document storage"
  default     = ""
}

variable "s3_bucket_size_threshold" {
  type        = number
  description = "Threshold for S3 bucket size in bytes"
  default     = 107374182400 # 100 GB
}

# Define common tags for resources
locals {
  common_tags = {
    Project     = "LoanManagementSystem"
    Environment = "${var.environment}"
    ManagedBy   = "Terraform"
    Component   = "Monitoring"
  }
}

# ECS Service Alarms
resource "aws_cloudwatch_metric_alarm" "backend_high_cpu" {
  alarm_name          = "${var.environment}-backend-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Average"
  threshold           = 85
  alarm_description   = "This metric monitors backend ECS service CPU utilization"
  dimensions = {
    ClusterName = "${var.ecs_cluster_name}"
    ServiceName = "${var.backend_service_name}"
  }
  alarm_actions = ["${var.sns_topic_arn}"]
  ok_actions    = ["${var.sns_topic_arn}"]
  tags = {
    Environment = "${var.environment}"
    Component   = "ECS"
  }
}

resource "aws_cloudwatch_metric_alarm" "frontend_high_cpu" {
  alarm_name          = "${var.environment}-frontend-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Average"
  threshold           = 85
  alarm_description   = "This metric monitors frontend ECS service CPU utilization"
  dimensions = {
    ClusterName = "${var.ecs_cluster_name}"
    ServiceName = "${var.frontend_service_name}"
  }
  alarm_actions = ["${var.sns_topic_arn}"]
  ok_actions    = ["${var.sns_topic_arn}"]
  tags = {
    Environment = "${var.environment}"
    Component   = "ECS"
  }
}

resource "aws_cloudwatch_metric_alarm" "backend_high_memory" {
  alarm_name          = "${var.environment}-backend-high-memory"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Average"
  threshold           = 85
  alarm_description   = "This metric monitors backend ECS service memory utilization"
  dimensions = {
    ClusterName = "${var.ecs_cluster_name}"
    ServiceName = "${var.backend_service_name}"
  }
  alarm_actions = ["${var.sns_topic_arn}"]
  ok_actions    = ["${var.sns_topic_arn}"]
  tags = {
    Environment = "${var.environment}"
    Component   = "ECS"
  }
}

resource "aws_cloudwatch_metric_alarm" "frontend_high_memory" {
  alarm_name          = "${var.environment}-frontend-high-memory"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Average"
  threshold           = 85
  alarm_description   = "This metric monitors frontend ECS service memory utilization"
  dimensions = {
    ClusterName = "${var.ecs_cluster_name}"
    ServiceName = "${var.frontend_service_name}"
  }
  alarm_actions = ["${var.sns_topic_arn}"]
  ok_actions    = ["${var.sns_topic_arn}"]
  tags = {
    Environment = "${var.environment}"
    Component   = "ECS"
  }
}

# RDS Database Alarms
resource "aws_cloudwatch_metric_alarm" "rds_cpu_utilization_high" {
  alarm_name          = "${var.environment}-rds-cpu-utilization-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 75
  alarm_description   = "Average database CPU utilization is too high"
  dimensions = {
    DBInstanceIdentifier = "${var.db_instance_identifier}"
  }
  alarm_actions = ["${var.sns_topic_arn}"]
  ok_actions    = ["${var.sns_topic_arn}"]
  tags = {
    Environment = "${var.environment}"
    Component   = "RDS"
  }
}

resource "aws_cloudwatch_metric_alarm" "rds_free_storage_space_low" {
  alarm_name          = "${var.environment}-rds-free-storage-space-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 3
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = "${var.rds_free_storage_threshold}"
  alarm_description   = "Average database free storage space is too low"
  dimensions = {
    DBInstanceIdentifier = "${var.db_instance_identifier}"
  }
  alarm_actions = ["${var.sns_topic_arn}"]
  ok_actions    = ["${var.sns_topic_arn}"]
  tags = {
    Environment = "${var.environment}"
    Component   = "RDS"
  }
}

resource "aws_cloudwatch_metric_alarm" "rds_free_memory_low" {
  alarm_name          = "${var.environment}-rds-free-memory-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 3
  metric_name         = "FreeableMemory"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = "${var.rds_free_memory_threshold}"
  alarm_description   = "Average database freeable memory is too low"
  dimensions = {
    DBInstanceIdentifier = "${var.db_instance_identifier}"
  }
  alarm_actions = ["${var.sns_topic_arn}"]
  ok_actions    = ["${var.sns_topic_arn}"]
  tags = {
    Environment = "${var.environment}"
    Component   = "RDS"
  }
}

resource "aws_cloudwatch_metric_alarm" "rds_high_connection_count" {
  alarm_name          = "${var.environment}-rds-high-connection-count"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = "${var.rds_connection_count_threshold}"
  alarm_description   = "Average database connection count is too high"
  dimensions = {
    DBInstanceIdentifier = "${var.db_instance_identifier}"
  }
  alarm_actions = ["${var.sns_topic_arn}"]
  ok_actions    = ["${var.sns_topic_arn}"]
  tags = {
    Environment = "${var.environment}"
    Component   = "RDS"
  }
}

resource "aws_cloudwatch_metric_alarm" "rds_replica_lag_high" {
  count               = "${var.db_replica_identifier != "" ? 1 : 0}"
  alarm_name          = "${var.environment}-rds-replica-lag-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "ReplicaLag"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 30
  alarm_description   = "RDS read replica lag is too high"
  dimensions = {
    DBInstanceIdentifier = "${var.db_replica_identifier}"
  }
  alarm_actions = ["${var.sns_topic_arn}"]
  ok_actions    = ["${var.sns_topic_arn}"]
  tags = {
    Environment = "${var.environment}"
    Component   = "RDS"
  }
}

# ElastiCache Redis Alarms
resource "aws_cloudwatch_metric_alarm" "elasticache_cpu_high" {
  alarm_name          = "${var.environment}-elasticache-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ElastiCache"
  period              = 300
  statistic           = "Average"
  threshold           = 75
  alarm_description   = "ElastiCache Redis CPU utilization is too high"
  dimensions = {
    ReplicationGroupId = "${var.redis_replication_group_id}"
  }
  alarm_actions = ["${var.sns_topic_arn}"]
  ok_actions    = ["${var.sns_topic_arn}"]
  tags = {
    Environment = "${var.environment}"
    Component   = "ElastiCache"
  }
}

resource "aws_cloudwatch_metric_alarm" "elasticache_memory_high" {
  alarm_name          = "${var.environment}-elasticache-memory-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "DatabaseMemoryUsagePercentage"
  namespace           = "AWS/ElastiCache"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "ElastiCache Redis memory usage is too high"
  dimensions = {
    ReplicationGroupId = "${var.redis_replication_group_id}"
  }
  alarm_actions = ["${var.sns_topic_arn}"]
  ok_actions    = ["${var.sns_topic_arn}"]
  tags = {
    Environment = "${var.environment}"
    Component   = "ElastiCache"
  }
}

resource "aws_cloudwatch_metric_alarm" "elasticache_connections_high" {
  alarm_name          = "${var.environment}-elasticache-connections-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CurrConnections"
  namespace           = "AWS/ElastiCache"
  period              = 300
  statistic           = "Average"
  threshold           = "${var.redis_max_connections * 0.8}"
  alarm_description   = "ElastiCache Redis connection count is too high"
  dimensions = {
    ReplicationGroupId = "${var.redis_replication_group_id}"
  }
  alarm_actions = ["${var.sns_topic_arn}"]
  ok_actions    = ["${var.sns_topic_arn}"]
  tags = {
    Environment = "${var.environment}"
    Component   = "ElastiCache"
  }
}

# Application Load Balancer Alarms
resource "aws_cloudwatch_metric_alarm" "alb_5xx_errors_high" {
  alarm_name          = "${var.environment}-alb-5xx-errors-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HTTPCode_ELB_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "Application Load Balancer 5XX error count is too high"
  dimensions = {
    LoadBalancer = "${var.alb_name}"
  }
  alarm_actions = ["${var.sns_topic_arn}"]
  ok_actions    = ["${var.sns_topic_arn}"]
  tags = {
    Environment = "${var.environment}"
    Component   = "ALB"
  }
}

resource "aws_cloudwatch_metric_alarm" "alb_4xx_errors_high" {
  alarm_name          = "${var.environment}-alb-4xx-errors-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HTTPCode_ELB_4XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Sum"
  threshold           = 100
  alarm_description   = "Application Load Balancer 4XX error count is too high"
  dimensions = {
    LoadBalancer = "${var.alb_name}"
  }
  alarm_actions = ["${var.sns_topic_arn}"]
  ok_actions    = ["${var.sns_topic_arn}"]
  tags = {
    Environment = "${var.environment}"
    Component   = "ALB"
  }
}

resource "aws_cloudwatch_metric_alarm" "alb_target_response_time_high" {
  alarm_name          = "${var.environment}-alb-target-response-time-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  extended_statistic  = "p95"
  threshold           = 1
  alarm_description   = "Application Load Balancer p95 target response time is too high"
  dimensions = {
    LoadBalancer = "${var.alb_name}"
  }
  alarm_actions = ["${var.sns_topic_arn}"]
  ok_actions    = ["${var.sns_topic_arn}"]
  tags = {
    Environment = "${var.environment}"
    Component   = "ALB"
  }
}

# S3 Storage Alarm
resource "aws_cloudwatch_metric_alarm" "s3_bucket_size_high" {
  alarm_name          = "${var.environment}-s3-bucket-size-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "BucketSizeBytes"
  namespace           = "AWS/S3"
  period              = 86400
  statistic           = "Average"
  threshold           = "${var.s3_bucket_size_threshold}"
  alarm_description   = "S3 document bucket size is approaching limit"
  dimensions = {
    BucketName  = "${var.document_bucket_name}"
    StorageType = "StandardStorage"
  }
  alarm_actions = ["${var.sns_topic_arn}"]
  ok_actions    = ["${var.sns_topic_arn}"]
  tags = {
    Environment = "${var.environment}"
    Component   = "S3"
  }
}

# Business Process SLA Alarms
resource "aws_cloudwatch_metric_alarm" "application_submission_sla_breach" {
  alarm_name          = "${var.environment}-application-submission-sla-breach"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ApplicationSubmissionSuccessRate"
  namespace           = "LoanManagementSystem"
  period              = 900
  statistic           = "Average"
  threshold           = 98
  alarm_description   = "Application submission success rate is below SLA threshold"
  dimensions = {
    Environment = "${var.environment}"
  }
  alarm_actions = ["${var.sns_topic_arn}"]
  ok_actions    = ["${var.sns_topic_arn}"]
  tags = {
    Environment = "${var.environment}"
    Component   = "BusinessProcess"
  }
}

resource "aws_cloudwatch_metric_alarm" "underwriting_decision_sla_breach" {
  alarm_name          = "${var.environment}-underwriting-decision-sla-breach"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "UnderwritingDecisionComplianceRate"
  namespace           = "LoanManagementSystem"
  period              = 86400
  statistic           = "Average"
  threshold           = 90
  alarm_description   = "Underwriting decision compliance rate is below SLA threshold"
  dimensions = {
    Environment = "${var.environment}"
  }
  alarm_actions = ["${var.sns_topic_arn}"]
  ok_actions    = ["${var.sns_topic_arn}"]
  tags = {
    Environment = "${var.environment}"
    Component   = "BusinessProcess"
  }
}

resource "aws_cloudwatch_metric_alarm" "document_generation_sla_breach" {
  alarm_name          = "${var.environment}-document-generation-sla-breach"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "DocumentGenerationComplianceRate"
  namespace           = "LoanManagementSystem"
  period              = 3600
  statistic           = "Average"
  threshold           = 95
  alarm_description   = "Document generation compliance rate is below SLA threshold"
  dimensions = {
    Environment = "${var.environment}"
  }
  alarm_actions = ["${var.sns_topic_arn}"]
  ok_actions    = ["${var.sns_topic_arn}"]
  tags = {
    Environment = "${var.environment}"
    Component   = "BusinessProcess"
  }
}

resource "aws_cloudwatch_metric_alarm" "funding_disbursement_sla_breach" {
  alarm_name          = "${var.environment}-funding-disbursement-sla-breach"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "FundingDisbursementComplianceRate"
  namespace           = "LoanManagementSystem"
  period              = 86400
  statistic           = "Average"
  threshold           = 90
  alarm_description   = "Funding disbursement compliance rate is below SLA threshold"
  dimensions = {
    Environment = "${var.environment}"
  }
  alarm_actions = ["${var.sns_topic_arn}"]
  ok_actions    = ["${var.sns_topic_arn}"]
  tags = {
    Environment = "${var.environment}"
    Component   = "BusinessProcess"
  }
}

# Output alarm ARNs for reference
output "alarm_arns" {
  description = "Map of CloudWatch alarm ARNs for reference"
  value = {
    backend_high_cpu             = "${aws_cloudwatch_metric_alarm.backend_high_cpu.arn}"
    frontend_high_cpu            = "${aws_cloudwatch_metric_alarm.frontend_high_cpu.arn}"
    backend_high_memory          = "${aws_cloudwatch_metric_alarm.backend_high_memory.arn}"
    frontend_high_memory         = "${aws_cloudwatch_metric_alarm.frontend_high_memory.arn}"
    rds_cpu_utilization_high     = "${aws_cloudwatch_metric_alarm.rds_cpu_utilization_high.arn}"
    rds_free_storage_space_low   = "${aws_cloudwatch_metric_alarm.rds_free_storage_space_low.arn}"
    rds_free_memory_low          = "${aws_cloudwatch_metric_alarm.rds_free_memory_low.arn}"
    rds_high_connection_count    = "${aws_cloudwatch_metric_alarm.rds_high_connection_count.arn}"
    elasticache_cpu_high         = "${aws_cloudwatch_metric_alarm.elasticache_cpu_high.arn}"
    elasticache_memory_high      = "${aws_cloudwatch_metric_alarm.elasticache_memory_high.arn}"
    elasticache_connections_high = "${aws_cloudwatch_metric_alarm.elasticache_connections_high.arn}"
    alb_5xx_errors_high          = "${aws_cloudwatch_metric_alarm.alb_5xx_errors_high.arn}"
    alb_4xx_errors_high          = "${aws_cloudwatch_metric_alarm.alb_4xx_errors_high.arn}"
    alb_target_response_time_high = "${aws_cloudwatch_metric_alarm.alb_target_response_time_high.arn}"
  }
}

output "business_alarm_arns" {
  description = "Map of business process SLA alarm ARNs for reference"
  value = {
    application_submission_sla_breach = "${aws_cloudwatch_metric_alarm.application_submission_sla_breach.arn}"
    underwriting_decision_sla_breach  = "${aws_cloudwatch_metric_alarm.underwriting_decision_sla_breach.arn}"
    document_generation_sla_breach    = "${aws_cloudwatch_metric_alarm.document_generation_sla_breach.arn}"
    funding_disbursement_sla_breach   = "${aws_cloudwatch_metric_alarm.funding_disbursement_sla_breach.arn}"
  }
}