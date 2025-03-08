output "cluster_id" {
  description = "The ID of the ECS cluster"
  value       = aws_ecs_cluster.main.id
}

output "cluster_name" {
  description = "The name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_cluster_name" {
  description = "The name of the ECS cluster for monitoring purposes"
  value       = aws_ecs_cluster.main.name
}

output "alb_id" {
  description = "The ID of the Application Load Balancer"
  value       = aws_lb.main.id
}

output "alb_dns_name" {
  description = "The DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "alb_arn" {
  description = "The ARN of the Application Load Balancer"
  value       = aws_lb.main.arn
}

output "alb_arn_suffix" {
  description = "The ARN suffix of the Application Load Balancer for CloudWatch metrics"
  value       = aws_lb.main.arn_suffix
}

output "backend_service_name" {
  description = "The name of the backend ECS service"
  value       = aws_ecs_service.backend.name
}

output "frontend_service_name" {
  description = "The name of the frontend ECS service"
  value       = aws_ecs_service.frontend.name
}

output "backend_target_group_arn" {
  description = "The ARN of the backend target group"
  value       = aws_lb_target_group.backend.arn
}

output "frontend_target_group_arn" {
  description = "The ARN of the frontend target group"
  value       = aws_lb_target_group.frontend.arn
}