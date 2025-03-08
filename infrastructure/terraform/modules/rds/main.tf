# Terraform module for provisioning and configuring an AWS RDS PostgreSQL database instance
# for the loan management system.

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

# Generate a secure random password if one is not provided
resource "random_password" "db_password" {
  count            = var.password == "" ? 1 : 0
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
  min_special      = 2
  min_upper        = 2
  min_lower        = 2
  min_numeric      = 2
}

# Create a DB subnet group if not using an existing one
resource "aws_db_subnet_group" "main" {
  count       = var.use_existing_subnet_group ? 0 : 1
  name        = "${var.identifier}-subnet-group"
  subnet_ids  = var.subnet_ids
  description = "Subnet group for ${var.identifier} RDS instance"
  
  tags = {
    Name        = "${var.identifier}-subnet-group"
    Environment = var.environment
  }
}

# Create the DB parameter group
resource "aws_db_parameter_group" "main" {
  name        = "${var.identifier}-parameter-group"
  family      = var.family
  description = "Parameter group for ${var.identifier} RDS instance"
  
  dynamic "parameter" {
    for_each = var.parameters
    content {
      name         = parameter.value.name
      value        = parameter.value.value
      apply_method = lookup(parameter.value, "apply_method", "immediate")
    }
  }
  
  tags = {
    Name        = "${var.identifier}-parameter-group"
    Environment = var.environment
  }
}

# Create a security group for the RDS instance
resource "aws_security_group" "db" {
  name        = "${var.identifier}-sg"
  description = "Security group for ${var.identifier} RDS instance"
  vpc_id      = var.vpc_id
  
  ingress {
    from_port       = var.port
    to_port         = var.port
    protocol        = "tcp"
    security_groups = var.allowed_security_groups
    description     = "Allow database connections from specified security groups"
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
  
  tags = {
    Name        = "${var.identifier}-sg"
    Environment = var.environment
  }
}

# Create the main RDS instance
resource "aws_db_instance" "main" {
  identifier                          = var.identifier
  engine                              = var.engine
  engine_version                      = var.engine_version
  instance_class                      = var.instance_class
  allocated_storage                   = var.allocated_storage
  max_allocated_storage               = var.max_allocated_storage
  storage_type                        = var.storage_type
  storage_encrypted                   = var.storage_encrypted
  kms_key_id                          = var.kms_key_id != "" ? var.kms_key_id : null
  db_name                             = var.db_name
  username                            = var.username
  password                            = var.password == "" ? random_password.db_password[0].result : var.password
  port                                = var.port
  parameter_group_name                = aws_db_parameter_group.main.name
  db_subnet_group_name                = var.use_existing_subnet_group ? var.existing_subnet_group_name : aws_db_subnet_group.main[0].name
  vpc_security_group_ids              = [aws_security_group.db.id]
  backup_retention_period             = var.backup_retention_period
  backup_window                       = var.backup_window
  maintenance_window                  = var.maintenance_window
  multi_az                            = var.multi_az
  publicly_accessible                 = var.publicly_accessible
  skip_final_snapshot                 = var.skip_final_snapshot
  final_snapshot_identifier           = "${var.identifier}-final-snapshot-${formatdate("YYYYMMDDhhmmss", timestamp())}"
  copy_tags_to_snapshot               = var.copy_tags_to_snapshot
  deletion_protection                 = var.deletion_protection
  performance_insights_enabled        = var.performance_insights_enabled
  performance_insights_retention_period = var.performance_insights_enabled ? var.performance_insights_retention_period : null
  monitoring_interval                 = var.monitoring_interval
  monitoring_role_arn                 = var.monitoring_role_arn != "" ? var.monitoring_role_arn : null
  enabled_cloudwatch_logs_exports     = var.enabled_cloudwatch_logs_exports
  auto_minor_version_upgrade          = var.auto_minor_version_upgrade
  apply_immediately                   = var.apply_immediately
  
  tags = {
    Name        = var.identifier
    Environment = var.environment
  }
}

# Create a read replica if specified
resource "aws_db_instance" "replica" {
  count                               = var.create_replica ? 1 : 0
  identifier                          = "${var.identifier}-replica"
  replicate_source_db                 = aws_db_instance.main.identifier
  instance_class                      = var.replica_instance_class != "" ? var.replica_instance_class : var.instance_class
  parameter_group_name                = aws_db_parameter_group.main.name
  vpc_security_group_ids              = [aws_security_group.db.id]
  publicly_accessible                 = var.publicly_accessible
  skip_final_snapshot                 = true
  copy_tags_to_snapshot               = var.copy_tags_to_snapshot
  backup_retention_period             = 0
  deletion_protection                 = var.deletion_protection
  performance_insights_enabled        = var.performance_insights_enabled
  performance_insights_retention_period = var.performance_insights_enabled ? var.performance_insights_retention_period : null
  monitoring_interval                 = var.monitoring_interval
  monitoring_role_arn                 = var.monitoring_role_arn != "" ? var.monitoring_role_arn : null
  auto_minor_version_upgrade          = var.auto_minor_version_upgrade
  apply_immediately                   = var.apply_immediately
  
  tags = {
    Name        = "${var.identifier}-replica"
    Environment = var.environment
  }
}

# Create CloudWatch alarms for monitoring if specified
resource "aws_cloudwatch_metric_alarm" "cpu_utilization_too_high" {
  count               = var.create_cloudwatch_alarms ? 1 : 0
  alarm_name          = "${var.identifier}-cpu-utilization-too-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = var.cpu_utilization_threshold
  alarm_description   = "Average database CPU utilization is too high"
  alarm_actions       = var.alarm_actions
  ok_actions          = var.ok_actions
  
  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }
  
  tags = {
    Name        = "${var.identifier}-cpu-utilization-too-high"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "free_storage_space_too_low" {
  count               = var.create_cloudwatch_alarms ? 1 : 0
  alarm_name          = "${var.identifier}-free-storage-space-too-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 3
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = var.free_storage_threshold
  alarm_description   = "Average database free storage space is too low"
  alarm_actions       = var.alarm_actions
  ok_actions          = var.ok_actions
  
  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }
  
  tags = {
    Name        = "${var.identifier}-free-storage-space-too-low"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "free_memory_too_low" {
  count               = var.create_cloudwatch_alarms ? 1 : 0
  alarm_name          = "${var.identifier}-free-memory-too-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 3
  metric_name         = "FreeableMemory"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = var.free_memory_threshold
  alarm_description   = "Average database freeable memory is too low"
  alarm_actions       = var.alarm_actions
  ok_actions          = var.ok_actions
  
  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }
  
  tags = {
    Name        = "${var.identifier}-free-memory-too-low"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "high_connection_count" {
  count               = var.create_cloudwatch_alarms ? 1 : 0
  alarm_name          = "${var.identifier}-high-connection-count"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = var.connection_count_threshold
  alarm_description   = "Average database connection count is too high"
  alarm_actions       = var.alarm_actions
  ok_actions          = var.ok_actions
  
  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }
  
  tags = {
    Name        = "${var.identifier}-high-connection-count"
    Environment = var.environment
  }
}