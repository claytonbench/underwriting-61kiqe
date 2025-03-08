# Variables for the RDS module
# This file defines all input variables for the RDS module that provisions
# and configures an AWS RDS PostgreSQL database instance for the loan management system.

variable "identifier" {
  description = "Identifier for the RDS instance"
  type        = string
}

variable "environment" {
  description = "Environment name (e.g., development, staging, production)"
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC where the RDS instance will be created"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs where the RDS instance can be deployed"
  type        = list(string)
}

variable "use_existing_subnet_group" {
  description = "Whether to use an existing DB subnet group"
  type        = bool
  default     = false
}

variable "existing_subnet_group_name" {
  description = "Name of existing DB subnet group to use if use_existing_subnet_group is true"
  type        = string
  default     = ""
}

variable "allowed_security_groups" {
  description = "List of security group IDs that are allowed to access the RDS instance"
  type        = list(string)
  default     = []
}

variable "engine" {
  description = "Database engine to use"
  type        = string
  default     = "postgres"
}

variable "engine_version" {
  description = "Version of the database engine"
  type        = string
  default     = "15.3"
}

variable "family" {
  description = "The family of the DB parameter group"
  type        = string
  default     = "postgres15"
}

variable "instance_class" {
  description = "The instance type for the RDS instance"
  type        = string
  default     = "db.t3.medium"
}

variable "allocated_storage" {
  description = "Allocated storage size in GB"
  type        = number
  default     = 20
}

variable "max_allocated_storage" {
  description = "Maximum storage size in GB for storage autoscaling"
  type        = number
  default     = 100
}

variable "storage_type" {
  description = "Storage type for the RDS instance (gp2, gp3, io1)"
  type        = string
  default     = "gp3"
}

variable "storage_encrypted" {
  description = "Whether to encrypt the RDS storage"
  type        = bool
  default     = true
}

variable "kms_key_id" {
  description = "KMS key ID for storage encryption"
  type        = string
  default     = ""
}

variable "db_name" {
  description = "Name of the database to create"
  type        = string
  default     = "loanmgmt"
}

variable "username" {
  description = "Username for the master DB user"
  type        = string
  default     = "dbadmin"
}

variable "password" {
  description = "Password for the master DB user (leave empty to generate a random password)"
  type        = string
  default     = ""
}

variable "port" {
  description = "Port on which the database accepts connections"
  type        = number
  default     = 5432
}

variable "parameters" {
  description = "List of DB parameters to apply"
  type        = list(map(string))
  default     = []
}

variable "backup_retention_period" {
  description = "Number of days to retain backups"
  type        = number
  default     = 7
}

variable "backup_window" {
  description = "Daily time range during which backups are created"
  type        = string
  default     = "03:00-06:00"
}

variable "maintenance_window" {
  description = "Weekly time range during which system maintenance can occur"
  type        = string
  default     = "Sun:00:00-Sun:03:00"
}

variable "multi_az" {
  description = "Whether to deploy a multi-AZ RDS instance for high availability"
  type        = bool
  default     = false
}

variable "publicly_accessible" {
  description = "Whether the RDS instance should be publicly accessible"
  type        = bool
  default     = false
}

variable "skip_final_snapshot" {
  description = "Whether to skip the final snapshot when the RDS instance is deleted"
  type        = bool
  default     = false
}

variable "copy_tags_to_snapshot" {
  description = "Whether to copy resource tags to the final snapshot"
  type        = bool
  default     = true
}

variable "deletion_protection" {
  description = "Whether to enable deletion protection for the RDS instance"
  type        = bool
  default     = true
}

variable "performance_insights_enabled" {
  description = "Whether to enable Performance Insights"
  type        = bool
  default     = true
}

variable "performance_insights_retention_period" {
  description = "Retention period for Performance Insights in days (7, 731 (2 years) or multiple of 31)"
  type        = number
  default     = 7
}

variable "monitoring_interval" {
  description = "Interval in seconds for Enhanced Monitoring (0, 1, 5, 10, 15, 30, 60)"
  type        = number
  default     = 60
}

variable "monitoring_role_arn" {
  description = "ARN of the IAM role for Enhanced Monitoring (leave empty to create a new role)"
  type        = string
  default     = ""
}

variable "enabled_cloudwatch_logs_exports" {
  description = "List of log types to export to CloudWatch"
  type        = list(string)
  default     = ["postgresql", "upgrade"]
}

variable "auto_minor_version_upgrade" {
  description = "Whether to automatically upgrade minor engine versions"
  type        = bool
  default     = true
}

variable "apply_immediately" {
  description = "Whether to apply changes immediately or during the next maintenance window"
  type        = bool
  default     = false
}

variable "create_replica" {
  description = "Whether to create a read replica"
  type        = bool
  default     = false
}

variable "replica_instance_class" {
  description = "Instance class for the read replica"
  type        = string
  default     = ""
}

variable "create_cloudwatch_alarms" {
  description = "Whether to create CloudWatch alarms for the RDS instance"
  type        = bool
  default     = true
}

variable "cpu_utilization_threshold" {
  description = "Threshold for CPU utilization alarm (percentage)"
  type        = number
  default     = 80
}

variable "free_storage_threshold" {
  description = "Threshold for free storage space alarm (bytes)"
  type        = number
  default     = 5368709120
}

variable "free_memory_threshold" {
  description = "Threshold for free memory alarm (bytes)"
  type        = number
  default     = 1073741824
}

variable "connection_count_threshold" {
  description = "Threshold for database connection count alarm"
  type        = number
  default     = 100
}

variable "alarm_actions" {
  description = "List of ARNs to notify when an alarm transitions to ALARM state"
  type        = list(string)
  default     = []
}

variable "ok_actions" {
  description = "List of ARNs to notify when an alarm transitions to OK state"
  type        = list(string)
  default     = []
}