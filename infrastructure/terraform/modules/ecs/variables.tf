variable "environment" {
  description = "Environment name (e.g., development, staging, production)"
  type        = string
}

variable "aws_region" {
  description = "AWS region where resources will be created"
  type        = string
  default     = "us-east-1"
}

variable "vpc_id" {
  description = "ID of the VPC where resources will be created"
  type        = string
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for the load balancer"
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for the ECS tasks"
  type        = list(string)
}

variable "app_security_group_id" {
  description = "Security group ID for the ECS tasks"
  type        = string
}

variable "alb_security_group_id" {
  description = "Security group ID for the Application Load Balancer"
  type        = string
}

variable "ecs_task_execution_role_arn" {
  description = "ARN of the IAM role for ECS task execution"
  type        = string
}

variable "ecs_task_role_arn" {
  description = "ARN of the IAM role for ECS tasks"
  type        = string
}

variable "backend_container_image" {
  description = "Docker image for the backend container"
  type        = string
}

variable "frontend_container_image" {
  description = "Docker image for the frontend container"
  type        = string
}

variable "backend_container_port" {
  description = "Port exposed by the backend container"
  type        = number
  default     = 8000
}

variable "frontend_container_port" {
  description = "Port exposed by the frontend container"
  type        = number
  default     = 80
}

variable "backend_container_cpu" {
  description = "CPU units for the backend container (1 vCPU = 1024 CPU units)"
  type        = number
  default     = 1024
}

variable "backend_container_memory" {
  description = "Memory for the backend container in MiB"
  type        = number
  default     = 2048
}

variable "frontend_container_cpu" {
  description = "CPU units for the frontend container (1 vCPU = 1024 CPU units)"
  type        = number
  default     = 512
}

variable "frontend_container_memory" {
  description = "Memory for the frontend container in MiB"
  type        = number
  default     = 1024
}

variable "backend_desired_count" {
  description = "Desired number of backend tasks"
  type        = number
  default     = 2
}

variable "frontend_desired_count" {
  description = "Desired number of frontend tasks"
  type        = number
  default     = 2
}

variable "backend_max_count" {
  description = "Maximum number of backend tasks for auto-scaling"
  type        = number
  default     = 10
}

variable "frontend_max_count" {
  description = "Maximum number of frontend tasks for auto-scaling"
  type        = number
  default     = 10
}

variable "backend_cpu_threshold" {
  description = "CPU utilization threshold (percentage) for backend auto-scaling"
  type        = number
  default     = 70
}

variable "frontend_cpu_threshold" {
  description = "CPU utilization threshold (percentage) for frontend auto-scaling"
  type        = number
  default     = 70
}

variable "health_check_grace_period_seconds" {
  description = "Grace period for health checks after task starts"
  type        = number
  default     = 60
}

variable "deployment_maximum_percent" {
  description = "Maximum percentage of tasks that can be running during a deployment"
  type        = number
  default     = 200
}

variable "deployment_minimum_healthy_percent" {
  description = "Minimum percentage of tasks that must remain healthy during a deployment"
  type        = number
  default     = 100
}

variable "enable_execute_command" {
  description = "Enable ECS Exec for running commands in containers"
  type        = bool
  default     = true
}

variable "db_host" {
  description = "Database host endpoint"
  type        = string
}

variable "db_name" {
  description = "Database name"
  type        = string
}

variable "db_username" {
  description = "Database username"
  type        = string
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "redis_host" {
  description = "Redis host endpoint"
  type        = string
}

variable "document_bucket_name" {
  description = "Name of the S3 bucket for document storage"
  type        = string
}

variable "certificate_arn" {
  description = "ARN of the SSL certificate for HTTPS"
  type        = string
}

variable "enable_cloudfront" {
  description = "Enable CloudFront distribution in front of the ALB"
  type        = bool
  default     = false
}

variable "cloudfront_price_class" {
  description = "CloudFront price class (PriceClass_100, PriceClass_200, PriceClass_All)"
  type        = string
  default     = "PriceClass_100"
}

variable "alarm_sns_topic_arn" {
  description = "ARN of the SNS topic for CloudWatch alarms"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}