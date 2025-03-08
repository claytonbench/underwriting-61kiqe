# AWS ECS Cluster configuration
# Terraform AWS provider version ~> 4.16
resource "aws_ecs_cluster" "main" {
  name = "${var.environment}-cluster"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  
  tags = {
    Name        = "${var.environment}-cluster"
    Environment = var.environment
  }
}

# Configure Fargate as the capacity provider for the ECS cluster
resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name = aws_ecs_cluster.main.name
  
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]
  
  default_capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 1
    base              = 1
  }
}

# Application Load Balancer for routing traffic to ECS services
resource "aws_lb" "main" {
  name               = "${var.environment}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.alb_security_group_id]
  subnets            = var.public_subnet_ids
  
  enable_deletion_protection = false
  enable_http2               = true
  idle_timeout               = 60
  
  tags = {
    Name        = "${var.environment}-alb"
    Environment = var.environment
  }
}

# Target group for the backend service
resource "aws_lb_target_group" "backend" {
  name        = "${var.environment}-backend-tg"
  port        = var.backend_container_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"
  
  deregistration_delay = 30
  
  health_check {
    enabled             = true
    path                = "/api/health/"
    port                = "traffic-port"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }
  
  tags = {
    Name        = "${var.environment}-backend-tg"
    Environment = var.environment
  }
}

# Target group for the frontend service
resource "aws_lb_target_group" "frontend" {
  name        = "${var.environment}-frontend-tg"
  port        = var.frontend_container_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"
  
  deregistration_delay = 30
  
  health_check {
    enabled             = true
    path                = "/"
    port                = "traffic-port"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }
  
  tags = {
    Name        = "${var.environment}-frontend-tg"
    Environment = var.environment
  }
}

# HTTP listener that redirects to HTTPS
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"
  
  default_action {
    type = "redirect"
    
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# HTTPS listener for secure traffic
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = var.certificate_arn
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend.arn
  }
}

# Listener rule to route API traffic to the backend service
resource "aws_lb_listener_rule" "backend_api" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 100
  
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }
  
  condition {
    path_pattern {
      values = ["/api/*"]
    }
  }
}

# Log group for backend container logs
resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/${var.environment}/backend"
  retention_in_days = 30
  
  tags = {
    Name        = "/ecs/${var.environment}/backend"
    Environment = var.environment
  }
}

# Log group for frontend container logs
resource "aws_cloudwatch_log_group" "frontend" {
  name              = "/ecs/${var.environment}/frontend"
  retention_in_days = 30
  
  tags = {
    Name        = "/ecs/${var.environment}/frontend"
    Environment = var.environment
  }
}

# Task definition for the backend service
resource "aws_ecs_task_definition" "backend" {
  family                   = "${var.environment}-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.backend_container_cpu
  memory                   = var.backend_container_memory
  execution_role_arn       = var.ecs_task_execution_role_arn
  task_role_arn            = var.ecs_task_role_arn
  
  container_definitions = jsonencode([
    {
      name      = "backend"
      image     = var.backend_container_image
      essential = true
      
      portMappings = [
        {
          containerPort = var.backend_container_port
          hostPort      = var.backend_container_port
          protocol      = "tcp"
        }
      ]
      
      environment = [
        { name = "ENVIRONMENT", value = var.environment },
        { name = "DB_HOST", value = var.db_host },
        { name = "DB_NAME", value = var.db_name },
        { name = "DB_USER", value = var.db_username },
        { name = "DB_PASSWORD", value = var.db_password },
        { name = "REDIS_HOST", value = var.redis_host },
        { name = "S3_BUCKET", value = var.document_bucket_name }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.environment}/backend"
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
      
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:${var.backend_container_port}/api/health/ || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])
  
  tags = {
    Name        = "${var.environment}-backend"
    Environment = var.environment
  }
}

# Task definition for the frontend service
resource "aws_ecs_task_definition" "frontend" {
  family                   = "${var.environment}-frontend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.frontend_container_cpu
  memory                   = var.frontend_container_memory
  execution_role_arn       = var.ecs_task_execution_role_arn
  task_role_arn            = var.ecs_task_role_arn
  
  container_definitions = jsonencode([
    {
      name      = "frontend"
      image     = var.frontend_container_image
      essential = true
      
      portMappings = [
        {
          containerPort = var.frontend_container_port
          hostPort      = var.frontend_container_port
          protocol      = "tcp"
        }
      ]
      
      environment = [
        { name = "ENVIRONMENT", value = var.environment },
        { name = "API_URL", value = "https://${aws_lb.main.dns_name}/api" }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.environment}/frontend"
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
      
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:${var.frontend_container_port}/ || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])
  
  tags = {
    Name        = "${var.environment}-frontend"
    Environment = var.environment
  }
}

# ECS service for the backend application
resource "aws_ecs_service" "backend" {
  name                               = "${var.environment}-backend"
  cluster                            = aws_ecs_cluster.main.id
  task_definition                    = aws_ecs_task_definition.backend.arn
  desired_count                      = var.backend_desired_count
  launch_type                        = "FARGATE"
  platform_version                   = "LATEST"
  health_check_grace_period_seconds  = var.health_check_grace_period_seconds
  deployment_maximum_percent         = var.deployment_maximum_percent
  deployment_minimum_healthy_percent = var.deployment_minimum_healthy_percent
  enable_execute_command             = var.enable_execute_command
  
  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.app_security_group_id]
    assign_public_ip = false
  }
  
  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "backend"
    container_port   = var.backend_container_port
  }
  
  deployment_controller {
    type = "ECS"
  }
  
  propagate_tags = "SERVICE"
  
  tags = {
    Name        = "${var.environment}-backend-service"
    Environment = var.environment
  }
}

# ECS service for the frontend application
resource "aws_ecs_service" "frontend" {
  name                               = "${var.environment}-frontend"
  cluster                            = aws_ecs_cluster.main.id
  task_definition                    = aws_ecs_task_definition.frontend.arn
  desired_count                      = var.frontend_desired_count
  launch_type                        = "FARGATE"
  platform_version                   = "LATEST"
  health_check_grace_period_seconds  = var.health_check_grace_period_seconds
  deployment_maximum_percent         = var.deployment_maximum_percent
  deployment_minimum_healthy_percent = var.deployment_minimum_healthy_percent
  enable_execute_command             = var.enable_execute_command
  
  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.app_security_group_id]
    assign_public_ip = false
  }
  
  load_balancer {
    target_group_arn = aws_lb_target_group.frontend.arn
    container_name   = "frontend"
    container_port   = var.frontend_container_port
  }
  
  deployment_controller {
    type = "ECS"
  }
  
  propagate_tags = "SERVICE"
  
  tags = {
    Name        = "${var.environment}-frontend-service"
    Environment = var.environment
  }
}

# Auto-scaling target for the backend service
resource "aws_appautoscaling_target" "backend" {
  service_namespace  = "ecs"
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.backend.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  min_capacity       = var.backend_desired_count
  max_capacity       = var.backend_max_count
}

# Auto-scaling target for the frontend service
resource "aws_appautoscaling_target" "frontend" {
  service_namespace  = "ecs"
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.frontend.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  min_capacity       = var.frontend_desired_count
  max_capacity       = var.frontend_max_count
}

# CPU-based auto-scaling policy for the backend service
resource "aws_appautoscaling_policy" "backend_cpu" {
  name               = "${var.environment}-backend-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.backend.resource_id
  scalable_dimension = aws_appautoscaling_target.backend.scalable_dimension
  service_namespace  = aws_appautoscaling_target.backend.service_namespace
  
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = var.backend_cpu_threshold
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

# CPU-based auto-scaling policy for the frontend service
resource "aws_appautoscaling_policy" "frontend_cpu" {
  name               = "${var.environment}-frontend-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.frontend.resource_id
  scalable_dimension = aws_appautoscaling_target.frontend.scalable_dimension
  service_namespace  = aws_appautoscaling_target.frontend.service_namespace
  
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = var.frontend_cpu_threshold
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

# Request count-based auto-scaling policy for the backend service
resource "aws_appautoscaling_policy" "backend_requests" {
  name               = "${var.environment}-backend-request-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.backend.resource_id
  scalable_dimension = aws_appautoscaling_target.backend.scalable_dimension
  service_namespace  = aws_appautoscaling_target.backend.service_namespace
  
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${aws_lb.main.arn_suffix}/${aws_lb_target_group.backend.arn_suffix}"
    }
    target_value       = 50
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

# Alarm for high CPU utilization in the backend service
resource "aws_cloudwatch_metric_alarm" "backend_high_cpu" {
  count               = var.alarm_sns_topic_arn != "" ? 1 : 0
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
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = aws_ecs_service.backend.name
  }
  
  alarm_actions = [var.alarm_sns_topic_arn]
  ok_actions    = [var.alarm_sns_topic_arn]
}

# Alarm for high CPU utilization in the frontend service
resource "aws_cloudwatch_metric_alarm" "frontend_high_cpu" {
  count               = var.alarm_sns_topic_arn != "" ? 1 : 0
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
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = aws_ecs_service.frontend.name
  }
  
  alarm_actions = [var.alarm_sns_topic_arn]
  ok_actions    = [var.alarm_sns_topic_arn]
}

# Output values for reference by other modules
output "cluster_id" {
  value = aws_ecs_cluster.main.id
}

output "cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "alb_id" {
  value = aws_lb.main.id
}

output "alb_dns_name" {
  value = aws_lb.main.dns_name
}

output "backend_service_name" {
  value = aws_ecs_service.backend.name
}

output "frontend_service_name" {
  value = aws_ecs_service.frontend.name
}