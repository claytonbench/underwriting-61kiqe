# Security groups for Loan Management System infrastructure
# AWS provider version: ~> 4.16

locals {
  common_tags = {
    Environment = var.environment
    Terraform   = "true"
    Project     = "LoanManagementSystem"
  }
}

# Security group for the Application Load Balancer
resource "aws_security_group" "alb" {
  name        = "${var.environment}-alb-sg"
  description = "Controls access to the Application Load Balancer"
  vpc_id      = var.vpc_id

  ingress {
    protocol    = "tcp"
    from_port   = 80
    to_port     = 80
    cidr_blocks = var.allowed_cidr_blocks
    description = "HTTP from allowed CIDR blocks"
  }

  ingress {
    protocol    = "tcp"
    from_port   = 443
    to_port     = 443
    cidr_blocks = var.allowed_cidr_blocks
    description = "HTTPS from allowed CIDR blocks"
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = merge(local.common_tags, { Name = "${var.environment}-alb-sg" })
}

# Security group for application containers
resource "aws_security_group" "app" {
  name        = "${var.environment}-app-sg"
  description = "Controls access to the application containers"
  vpc_id      = var.vpc_id

  ingress {
    protocol        = "tcp"
    from_port       = var.backend_container_port
    to_port         = var.backend_container_port
    security_groups = [aws_security_group.alb.id]
    description     = "Backend container port from ALB"
  }

  ingress {
    protocol        = "tcp"
    from_port       = var.frontend_container_port
    to_port         = var.frontend_container_port
    security_groups = [aws_security_group.alb.id]
    description     = "Frontend container port from ALB"
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = merge(local.common_tags, { Name = "${var.environment}-app-sg" })
}

# Security group for RDS database
resource "aws_security_group" "database" {
  name        = "${var.environment}-db-sg"
  description = "Controls access to the PostgreSQL database"
  vpc_id      = var.vpc_id

  ingress {
    protocol        = "tcp"
    from_port       = var.db_port
    to_port         = var.db_port
    security_groups = [aws_security_group.app.id]
    description     = "PostgreSQL from application"
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = merge(local.common_tags, { Name = "${var.environment}-db-sg" })
}

# Security group for ElastiCache Redis
resource "aws_security_group" "elasticache" {
  name        = "${var.environment}-redis-sg"
  description = "Controls access to ElastiCache Redis"
  vpc_id      = var.vpc_id

  ingress {
    protocol        = "tcp"
    from_port       = var.redis_port
    to_port         = var.redis_port
    security_groups = [aws_security_group.app.id]
    description     = "Redis from application"
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = merge(local.common_tags, { Name = "${var.environment}-redis-sg" })
}

# Rule to allow communication between application containers
resource "aws_security_group_rule" "app_to_app" {
  security_group_id        = aws_security_group.app.id
  type                     = "ingress"
  from_port                = 0
  to_port                  = 65535
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.app.id
  description              = "Allow all traffic between application containers"
}

# Rule to allow SSH access from bastion host to application containers
resource "aws_security_group_rule" "bastion_to_app" {
  count = var.create_bastion ? 1 : 0

  security_group_id        = aws_security_group.app.id
  type                     = "ingress"
  from_port                = 22
  to_port                  = 22
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.bastion[0].id
  description              = "SSH from bastion host"
}

# Rule to allow database access from bastion host for administration
resource "aws_security_group_rule" "bastion_to_db" {
  count = var.create_bastion ? 1 : 0

  security_group_id        = aws_security_group.database.id
  type                     = "ingress"
  from_port                = var.db_port
  to_port                  = var.db_port
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.bastion[0].id
  description              = "Database access from bastion host"
}

# Security group for bastion host
resource "aws_security_group" "bastion" {
  count = var.create_bastion ? 1 : 0

  name        = "${var.environment}-bastion-sg"
  description = "Controls access to the bastion host"
  vpc_id      = var.vpc_id

  ingress {
    protocol    = "tcp"
    from_port   = 22
    to_port     = 22
    cidr_blocks = var.bastion_allowed_cidr
    description = "SSH from allowed CIDR blocks"
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = merge(local.common_tags, { Name = "${var.environment}-bastion-sg" })
}

# Variables
variable "environment" {
  description = "Deployment environment (development, staging, production)"
  type        = string
  default     = "development"
}

variable "vpc_id" {
  description = "ID of the VPC where security groups will be created"
  type        = string
}

variable "allowed_cidr_blocks" {
  description = "List of CIDR blocks allowed to access the ALB"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "backend_container_port" {
  description = "Port the backend container listens on"
  type        = number
  default     = 8000
}

variable "frontend_container_port" {
  description = "Port the frontend container listens on"
  type        = number
  default     = 80
}

variable "db_port" {
  description = "Port the PostgreSQL database listens on"
  type        = number
  default     = 5432
}

variable "redis_port" {
  description = "Port the Redis ElastiCache cluster listens on"
  type        = number
  default     = 6379
}

variable "create_bastion" {
  description = "Whether to create a bastion host security group"
  type        = bool
  default     = false
}

variable "bastion_allowed_cidr" {
  description = "List of CIDR blocks allowed to access the bastion host"
  type        = list(string)
  default     = []
}

# Outputs
output "alb_security_group_id" {
  description = "Security group ID for the Application Load Balancer"
  value       = aws_security_group.alb.id
  sensitive   = false
}

output "app_security_group_id" {
  description = "Security group ID for application containers"
  value       = aws_security_group.app.id
  sensitive   = false
}

output "database_security_group_id" {
  description = "Security group ID for the database"
  value       = aws_security_group.database.id
  sensitive   = false
}

output "elasticache_security_group_id" {
  description = "Security group ID for ElastiCache"
  value       = aws_security_group.elasticache.id
  sensitive   = false
}

output "bastion_security_group_id" {
  description = "Security group ID for the bastion host"
  value       = var.create_bastion ? aws_security_group.bastion[0].id : ""
  sensitive   = false
}