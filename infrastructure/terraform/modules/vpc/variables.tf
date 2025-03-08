variable "environment" {
  description = "Environment name (e.g., development, staging, production)"
  type        = string
}

variable "aws_region" {
  description = "AWS region where the VPC will be created"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones to use for subnet creation"
  type        = list(string)
}

variable "public_subnet_cidrs" {
  description = "List of CIDR blocks for public subnets (one per AZ)"
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "List of CIDR blocks for private subnets (one per AZ)"
  type        = list(string)
}

variable "database_subnet_cidrs" {
  description = "List of CIDR blocks for database subnets (one per AZ)"
  type        = list(string)
}

variable "enable_nat_gateway" {
  description = "Flag to enable NAT Gateway for private subnets"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Flag to use a single NAT Gateway instead of one per AZ (cost savings)"
  type        = bool
  default     = false
}

variable "enable_dns_hostnames" {
  description = "Flag to enable DNS hostnames in the VPC"
  type        = bool
  default     = true
}

variable "enable_dns_support" {
  description = "Flag to enable DNS support in the VPC"
  type        = bool
  default     = true
}

variable "enable_vpc_flow_logs" {
  description = "Flag to enable VPC Flow Logs for network monitoring and security analysis"
  type        = bool
  default     = false
}

variable "flow_log_bucket_arn" {
  description = "ARN of the S3 bucket for storing VPC flow logs"
  type        = string
  default     = ""
}

variable "create_database_subnet_group" {
  description = "Flag to create a database subnet group for RDS instances"
  type        = bool
  default     = true
}

variable "create_elasticache_subnet_group" {
  description = "Flag to create an ElastiCache subnet group for Redis clusters"
  type        = bool
  default     = true
}

variable "enable_s3_endpoint" {
  description = "Flag to create a VPC endpoint for S3 to allow private access without internet"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Additional tags to apply to all resources created by this module"
  type        = map(string)
  default     = {}
}