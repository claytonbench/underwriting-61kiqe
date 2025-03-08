#--------------------------------------------------------------
# Security Module Outputs
# 
# These outputs expose security resources created by this module
# for use by other Terraform modules or the root configuration.
# They include security groups, IAM roles, KMS keys, and WAF resources.
#--------------------------------------------------------------

output "alb_security_group_id" {
  description = "Security group ID for the Application Load Balancer"
  value       = aws_security_group.alb.id
}

output "app_security_group_id" {
  description = "Security group ID for application containers"
  value       = aws_security_group.app.id
}

output "database_security_group_id" {
  description = "Security group ID for the database"
  value       = aws_security_group.database.id
}

output "elasticache_security_group_id" {
  description = "Security group ID for ElastiCache"
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
  value       = var.enable_waf ? aws_wafv2_web_acl.main[0].arn : ""
}