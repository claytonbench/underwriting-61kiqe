# Terraform module for security resources in the loan management system
# This module creates and manages:
# - Security groups for application components
# - KMS encryption keys for data protection
# - IAM roles and policies for secure access
# - WAF configurations for application protection

#--------------------------------------------------------------
# Provider and Locals
#--------------------------------------------------------------

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

locals {
  common_tags = {
    Environment = var.environment
    Terraform   = "true"
    Project     = "LoanManagementSystem"
  }
}

# Get current AWS account ID for IAM policies
data "aws_caller_identity" "current" {}

# Get current AWS region
data "aws_region" "current" {}

#--------------------------------------------------------------
# Security Groups
#--------------------------------------------------------------

# Security group for the Application Load Balancer
resource "aws_security_group" "alb" {
  name        = "${var.environment}-alb-sg"
  description = "Controls access to the Application Load Balancer"
  vpc_id      = var.vpc_id

  # Allow HTTP from specified CIDR blocks
  ingress {
    protocol    = "tcp"
    from_port   = 80
    to_port     = 80
    cidr_blocks = var.allowed_cidr_blocks
    description = "HTTP from allowed CIDR blocks"
  }

  # Allow HTTPS from specified CIDR blocks
  ingress {
    protocol    = "tcp"
    from_port   = 443
    to_port     = 443
    cidr_blocks = var.allowed_cidr_blocks
    description = "HTTPS from allowed CIDR blocks"
  }

  # Allow all outbound traffic
  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name        = "${var.environment}-alb-sg"
    Environment = var.environment
  }
}

# Security group for application containers
resource "aws_security_group" "app" {
  name        = "${var.environment}-app-sg"
  description = "Controls access to the application containers"
  vpc_id      = var.vpc_id

  # Allow traffic from ALB to backend container port
  ingress {
    protocol        = "tcp"
    from_port       = var.backend_container_port
    to_port         = var.backend_container_port
    security_groups = [aws_security_group.alb.id]
    description     = "Backend container port from ALB"
  }

  # Allow traffic from ALB to frontend container port
  ingress {
    protocol        = "tcp"
    from_port       = var.frontend_container_port
    to_port         = var.frontend_container_port
    security_groups = [aws_security_group.alb.id]
    description     = "Frontend container port from ALB"
  }

  # Allow all outbound traffic
  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name        = "${var.environment}-app-sg"
    Environment = var.environment
  }
}

# Allow communication between application containers in the same security group
resource "aws_security_group_rule" "app_to_app" {
  security_group_id        = aws_security_group.app.id
  type                     = "ingress"
  from_port                = 0
  to_port                  = 65535
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.app.id
  description              = "Allow all traffic between application containers"
}

# Security group for RDS database
resource "aws_security_group" "database" {
  name        = "${var.environment}-db-sg"
  description = "Controls access to the PostgreSQL database"
  vpc_id      = var.vpc_id

  # Allow PostgreSQL traffic from application
  ingress {
    protocol        = "tcp"
    from_port       = var.db_port
    to_port         = var.db_port
    security_groups = [aws_security_group.app.id]
    description     = "PostgreSQL from application"
  }

  # Allow all outbound traffic
  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name        = "${var.environment}-db-sg"
    Environment = var.environment
  }
}

# Security group for ElastiCache Redis
resource "aws_security_group" "elasticache" {
  name        = "${var.environment}-redis-sg"
  description = "Controls access to ElastiCache Redis"
  vpc_id      = var.vpc_id

  # Allow Redis traffic from application
  ingress {
    protocol        = "tcp"
    from_port       = var.redis_port
    to_port         = var.redis_port
    security_groups = [aws_security_group.app.id]
    description     = "Redis from application"
  }

  # Allow all outbound traffic
  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name        = "${var.environment}-redis-sg"
    Environment = var.environment
  }
}

#--------------------------------------------------------------
# KMS Key Configuration
#--------------------------------------------------------------

# Define KMS key policy
data "aws_iam_policy_document" "kms_key_policy" {
  statement {
    sid    = "EnableIAMUserPermissions"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions   = ["kms:*"]
    resources = ["*"]
  }

  statement {
    sid    = "AllowECSTaskExecution"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
    actions = [
      "kms:Decrypt",
      "kms:DescribeKey",
      "kms:Encrypt",
      "kms:GenerateDataKey*",
      "kms:ReEncrypt*"
    ]
    resources = ["*"]
  }
}

# Create KMS key for encrypting sensitive data
resource "aws_kms_key" "main" {
  description             = "KMS key for the loan management system"
  deletion_window_in_days = var.kms_key_deletion_window
  enable_key_rotation     = var.kms_key_rotation_enabled
  policy                  = data.aws_iam_policy_document.kms_key_policy.json

  tags = {
    Name        = "${var.environment}-kms-key"
    Environment = var.environment
  }
}

# Create an alias for the KMS key
resource "aws_kms_alias" "main" {
  name          = "alias/${var.environment}-loan-management-key"
  target_key_id = aws_kms_key.main.key_id
}

#--------------------------------------------------------------
# IAM Roles and Policies
#--------------------------------------------------------------

# Define ECS assume role policy
data "aws_iam_policy_document" "ecs_assume_role_policy" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

# Create ECS task execution role
resource "aws_iam_role" "ecs_task_execution_role" {
  name               = "${var.environment}-ecs-task-execution-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_role_policy.json

  tags = {
    Name        = "${var.environment}-ecs-task-execution-role"
    Environment = var.environment
  }
}

# Attach the AWS managed ECS task execution role policy
resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Define policy for accessing secrets and parameters
data "aws_iam_policy_document" "ecs_task_execution_secrets" {
  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue",
      "ssm:GetParameters",
      "ssm:GetParameter",
      "ssm:GetParametersByPath"
    ]
    resources = [
      "arn:aws:secretsmanager:*:${data.aws_caller_identity.current.account_id}:secret:${var.environment}/*",
      "arn:aws:ssm:*:${data.aws_caller_identity.current.account_id}:parameter/${var.ssm_parameter_prefix}/*"
    ]
  }

  statement {
    effect    = "Allow"
    actions   = ["kms:Decrypt"]
    resources = [aws_kms_key.main.arn]
  }
}

# Attach policy for accessing secrets and parameters to task execution role
resource "aws_iam_role_policy" "ecs_task_execution_secrets" {
  name   = "${var.environment}-ecs-task-execution-secrets"
  role   = aws_iam_role.ecs_task_execution_role.id
  policy = data.aws_iam_policy_document.ecs_task_execution_secrets.json
}

# Create ECS task role for application containers
resource "aws_iam_role" "ecs_task_role" {
  name               = "${var.environment}-ecs-task-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_role_policy.json

  tags = {
    Name        = "${var.environment}-ecs-task-role"
    Environment = var.environment
  }
}

# Define policy for backend ECS tasks
data "aws_iam_policy_document" "backend_task_policy" {
  statement {
    effect = "Allow"
    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:DeleteObject",
      "s3:ListBucket",
      "s3:GetObjectVersion"
    ]
    resources = [
      "arn:aws:s3:::${var.document_bucket_name}-${var.environment}/*",
      "arn:aws:s3:::${var.document_bucket_name}-${var.environment}"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "kms:Decrypt",
      "kms:GenerateDataKey",
      "kms:DescribeKey"
    ]
    resources = [aws_kms_key.main.arn]
  }

  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogStreams"
    ]
    resources = [
      "arn:aws:logs:*:${data.aws_caller_identity.current.account_id}:log-group:/ecs/${var.environment}/backend:*",
      "arn:aws:logs:*:${data.aws_caller_identity.current.account_id}:log-group:/ecs/${var.environment}/backend:log-stream:*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "sqs:SendMessage",
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "sqs:GetQueueUrl"
    ]
    resources = ["arn:aws:sqs:*:${data.aws_caller_identity.current.account_id}:${var.environment}-*"]
  }
}

# Attach policy to backend task role
resource "aws_iam_role_policy" "backend_task_policy" {
  name   = "${var.environment}-backend-task-policy"
  role   = aws_iam_role.ecs_task_role.id
  policy = data.aws_iam_policy_document.backend_task_policy.json
}

# Define policy for frontend ECS tasks
data "aws_iam_policy_document" "frontend_task_policy" {
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:ListBucket"
    ]
    resources = [
      "arn:aws:s3:::${var.document_bucket_name}-${var.environment}/*",
      "arn:aws:s3:::${var.document_bucket_name}-${var.environment}"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogStreams"
    ]
    resources = [
      "arn:aws:logs:*:${data.aws_caller_identity.current.account_id}:log-group:/ecs/${var.environment}/frontend:*",
      "arn:aws:logs:*:${data.aws_caller_identity.current.account_id}:log-group:/ecs/${var.environment}/frontend:log-stream:*"
    ]
  }
}

# Attach policy to frontend task role
resource "aws_iam_role_policy" "frontend_task_policy" {
  name   = "${var.environment}-frontend-task-policy"
  role   = aws_iam_role.ecs_task_role.id
  policy = data.aws_iam_policy_document.frontend_task_policy.json
}

#--------------------------------------------------------------
# WAF Configuration
#--------------------------------------------------------------

# Create WAF Web ACL if enabled
resource "aws_wafv2_web_acl" "main" {
  count = var.enable_waf ? 1 : 0

  name        = "${var.environment}-loan-management-waf"
  description = "WAF rules for loan management system"
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  # AWS Managed Rules Common Rule Set
  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 10

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesCommonRuleSet"
      sampled_requests_enabled   = true
    }
  }

  # AWS Managed Rules SQL Injection Prevention Rule Set
  rule {
    name     = "AWSManagedRulesSQLiRuleSet"
    priority = 20

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesSQLiRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesSQLiRuleSet"
      sampled_requests_enabled   = true
    }
  }

  # Rate-based rule to prevent DDoS attacks
  rule {
    name     = "RateBasedRule"
    priority = 30

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = var.waf_rate_limit
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateBasedRule"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.environment}-loan-management-waf"
    sampled_requests_enabled   = true
  }

  tags = {
    Name        = "${var.environment}-loan-management-waf"
    Environment = var.environment
  }
}

# Associate WAF Web ACL with ALB if WAF is enabled and ALB ARN is provided
resource "aws_wafv2_web_acl_association" "main" {
  count = var.enable_waf && var.alb_arn != "" ? 1 : 0

  resource_arn = var.alb_arn
  web_acl_arn  = aws_wafv2_web_acl.main[0].arn
}

#--------------------------------------------------------------
# Outputs
#--------------------------------------------------------------

output "alb_security_group_id" {
  description = "ID of the security group for the Application Load Balancer"
  value       = aws_security_group.alb.id
}

output "app_security_group_id" {
  description = "ID of the security group for application containers"
  value       = aws_security_group.app.id
}

output "database_security_group_id" {
  description = "ID of the security group for the database"
  value       = aws_security_group.database.id
}

output "elasticache_security_group_id" {
  description = "ID of the security group for ElastiCache"
  value       = aws_security_group.elasticache.id
}

output "ecs_task_execution_role_arn" {
  description = "ARN of the IAM role for ECS task execution"
  value       = aws_iam_role.ecs_task_execution_role.arn
}

output "ecs_task_role_arn" {
  description = "ARN of the IAM role for ECS tasks"
  value       = aws_iam_role.ecs_task_role.arn
}

output "kms_key_id" {
  description = "ID of the KMS key for encryption"
  value       = aws_kms_key.main.key_id
}

output "kms_key_arn" {
  description = "ARN of the KMS key for encryption"
  value       = aws_kms_key.main.arn
}

output "web_acl_arn" {
  description = "ARN of the WAF Web ACL"
  value       = var.enable_waf ? aws_wafv2_web_acl.main[0].arn : null
}