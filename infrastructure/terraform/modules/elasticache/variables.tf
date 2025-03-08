variable "environment" {
  description = "Environment name (e.g., development, staging, production)"
  type        = string
}

variable "redis_node_type" {
  description = "ElastiCache node type for Redis cluster"
  type        = string
  default     = "cache.t3.medium"
}

variable "redis_engine_version" {
  description = "Redis engine version"
  type        = string
  default     = "7.0"
}

variable "redis_parameter_group_name" {
  description = "Name of the parameter group to associate with the Redis cluster"
  type        = string
  default     = "default.redis7"
}

variable "subnet_group_name" {
  description = "Name of the ElastiCache subnet group where the cluster will be deployed"
  type        = string
}

variable "security_group_ids" {
  description = "List of security group IDs to associate with the Redis cluster"
  type        = list(string)
  default     = []
}

variable "redis_num_cache_clusters" {
  description = "Number of cache clusters (nodes) in the Redis replication group"
  type        = number
  default     = 2
}

variable "redis_auth_token" {
  description = "Auth token for Redis authentication (transit encryption must be enabled)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "kms_key_id" {
  description = "KMS key ID for encrypting Redis data at rest"
  type        = string
  default     = ""
}

variable "redis_max_connections" {
  description = "Maximum number of connections Redis should support"
  type        = number
  default     = 1000
}

variable "enable_monitoring" {
  description = "Whether to enable CloudWatch alarms for Redis monitoring"
  type        = bool
  default     = true
}

variable "alarm_actions" {
  description = "List of ARNs to notify when Redis alarms trigger (e.g., SNS topic ARNs)"
  type        = list(string)
  default     = []
}