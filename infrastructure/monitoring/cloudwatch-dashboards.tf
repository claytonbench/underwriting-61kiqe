# CloudWatch Dashboards for Loan Management System
# Creates comprehensive monitoring dashboards for various stakeholders

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }
}

# Variables for dashboard configuration
variable "environment" {
  type        = string
  description = "Deployment environment (development, staging, production)"
  default     = "development"
}

variable "region" {
  type        = string
  description = "AWS region where resources are deployed"
  default     = "us-east-1"
}

variable "ecs_cluster_name" {
  type        = string
  description = "Name of the ECS cluster"
  default     = ""
}

variable "backend_service_name" {
  type        = string
  description = "Name of the backend ECS service"
  default     = ""
}

variable "frontend_service_name" {
  type        = string
  description = "Name of the frontend ECS service"
  default     = ""
}

variable "db_instance_identifier" {
  type        = string
  description = "Identifier of the RDS database instance"
  default     = ""
}

variable "db_replica_identifier" {
  type        = string
  description = "Identifier of the RDS read replica instance"
  default     = ""
}

variable "redis_replication_group_id" {
  type        = string
  description = "ID of the ElastiCache Redis replication group"
  default     = ""
}

variable "alb_name" {
  type        = string
  description = "Name of the Application Load Balancer"
  default     = ""
}

variable "document_bucket_name" {
  type        = string
  description = "Name of the S3 bucket for document storage"
  default     = ""
}

# Common tags for resources
locals {
  common_tags = {
    Project     = "LoanManagementSystem"
    Environment = var.environment
    ManagedBy   = "Terraform"
    Component   = "Monitoring"
  }

  # System Overview Dashboard configuration
  system_overview_dashboard = {
    widgets = [
      {
        type = "metric"
        x    = 0
        y    = 0
        width = 24
        height = 6
        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ServiceName", "${var.backend_service_name}", "ClusterName", "${var.ecs_cluster_name}"],
            ["AWS/ECS", "CPUUtilization", "ServiceName", "${var.frontend_service_name}", "ClusterName", "${var.ecs_cluster_name}"],
            ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", "${var.db_instance_identifier}"],
            ["AWS/ElastiCache", "CPUUtilization", "ReplicationGroupId", "${var.redis_replication_group_id}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "System CPU Utilization"
          period = 300
          stat = "Average"
        }
      },
      {
        type = "metric"
        x    = 0
        y    = 6
        width = 24
        height = 6
        properties = {
          metrics = [
            ["AWS/ECS", "MemoryUtilization", "ServiceName", "${var.backend_service_name}", "ClusterName", "${var.ecs_cluster_name}"],
            ["AWS/ECS", "MemoryUtilization", "ServiceName", "${var.frontend_service_name}", "ClusterName", "${var.ecs_cluster_name}"],
            ["AWS/ElastiCache", "DatabaseMemoryUsagePercentage", "ReplicationGroupId", "${var.redis_replication_group_id}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "System Memory Utilization"
          period = 300
          stat = "Average"
        }
      },
      {
        type = "metric"
        x    = 0
        y    = 12
        width = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "HTTPCode_Target_2XX_Count", "LoadBalancer", "${var.alb_name}"],
            ["AWS/ApplicationELB", "HTTPCode_Target_4XX_Count", "LoadBalancer", "${var.alb_name}"],
            ["AWS/ApplicationELB", "HTTPCode_Target_5XX_Count", "LoadBalancer", "${var.alb_name}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "API Response Codes"
          period = 300
          stat = "Sum"
        }
      },
      {
        type = "metric"
        x    = 12
        y    = 12
        width = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", "${var.alb_name}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "API Response Time"
          period = 300
          stat = "p95"
        }
      },
      {
        type = "metric"
        x    = 0
        y    = 18
        width = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", "${var.db_instance_identifier}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "Database Connections"
          period = 300
          stat = "Average"
        }
      },
      {
        type = "metric"
        x    = 12
        y    = 18
        width = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ElastiCache", "CurrConnections", "ReplicationGroupId", "${var.redis_replication_group_id}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "Redis Connections"
          period = 300
          stat = "Average"
        }
      }
    ]
  }

  # Application Performance Dashboard configuration
  application_performance_dashboard = {
    widgets = [
      {
        type = "text"
        x    = 0
        y    = 0
        width = 24
        height = 1
        properties = {
          markdown = "# Application Performance Dashboard\nKey metrics for monitoring application performance and user experience."
        }
      },
      {
        type = "metric"
        x    = 0
        y    = 1
        width = 12
        height = 6
        properties = {
          metrics = [
            ["LoanManagementSystem", "ApiRequestCount", "Service", "backend", "Environment", "${var.environment}"],
            ["LoanManagementSystem", "ApiRequestCount", "Service", "frontend", "Environment", "${var.environment}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "API Request Volume"
          period = 60
          stat = "Sum"
        }
      },
      {
        type = "metric"
        x    = 12
        y    = 1
        width = 12
        height = 6
        properties = {
          metrics = [
            ["LoanManagementSystem", "ApiResponseTime", "Service", "backend", "Environment", "${var.environment}"],
            ["LoanManagementSystem", "ApiResponseTime", "Service", "frontend", "Environment", "${var.environment}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "API Response Time (ms)"
          period = 60
          stat = "p95"
        }
      },
      {
        type = "metric"
        x    = 0
        y    = 7
        width = 12
        height = 6
        properties = {
          metrics = [
            ["LoanManagementSystem", "ApiErrorRate", "Service", "backend", "Environment", "${var.environment}"],
            ["LoanManagementSystem", "ApiErrorRate", "Service", "frontend", "Environment", "${var.environment}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "API Error Rate (%)"
          period = 60
          stat = "Average"
        }
      },
      {
        type = "metric"
        x    = 12
        y    = 7
        width = 12
        height = 6
        properties = {
          metrics = [
            ["LoanManagementSystem", "DatabaseQueryTime", "Environment", "${var.environment}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "Database Query Time (ms)"
          period = 60
          stat = "p95"
        }
      },
      {
        type = "metric"
        x    = 0
        y    = 13
        width = 12
        height = 6
        properties = {
          metrics = [
            ["LoanManagementSystem", "DocumentGenerationTime", "Environment", "${var.environment}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "Document Generation Time (ms)"
          period = 60
          stat = "Average"
        }
      },
      {
        type = "metric"
        x    = 12
        y    = 13
        width = 12
        height = 6
        properties = {
          metrics = [
            ["LoanManagementSystem", "ActiveUsers", "UserType", "Borrower", "Environment", "${var.environment}"],
            ["LoanManagementSystem", "ActiveUsers", "UserType", "SchoolAdmin", "Environment", "${var.environment}"],
            ["LoanManagementSystem", "ActiveUsers", "UserType", "Underwriter", "Environment", "${var.environment}"],
            ["LoanManagementSystem", "ActiveUsers", "UserType", "QC", "Environment", "${var.environment}"],
            ["LoanManagementSystem", "ActiveUsers", "UserType", "SystemAdmin", "Environment", "${var.environment}"]
          ]
          view = "timeSeries"
          stacked = true
          region = "${var.region}"
          title = "Active Users by Role"
          period = 300
          stat = "Maximum"
        }
      }
    ]
  }

  # Infrastructure Metrics Dashboard configuration
  infrastructure_metrics_dashboard = {
    widgets = [
      {
        type = "text"
        x    = 0
        y    = 0
        width = 24
        height = 1
        properties = {
          markdown = "# Infrastructure Metrics Dashboard\nKey metrics for monitoring infrastructure health and performance."
        }
      },
      {
        type = "metric"
        x    = 0
        y    = 1
        width = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ServiceName", "${var.backend_service_name}", "ClusterName", "${var.ecs_cluster_name}"],
            ["AWS/ECS", "CPUUtilization", "ServiceName", "${var.frontend_service_name}", "ClusterName", "${var.ecs_cluster_name}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "ECS CPU Utilization"
          period = 300
          stat = "Average"
          annotations = {
            horizontal = [
              {
                label = "Warning"
                value = 70
                color = "#ff9900"
              },
              {
                label = "Critical"
                value = 85
                color = "#d13212"
              }
            ]
          }
        }
      },
      {
        type = "metric"
        x    = 12
        y    = 1
        width = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ECS", "MemoryUtilization", "ServiceName", "${var.backend_service_name}", "ClusterName", "${var.ecs_cluster_name}"],
            ["AWS/ECS", "MemoryUtilization", "ServiceName", "${var.frontend_service_name}", "ClusterName", "${var.ecs_cluster_name}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "ECS Memory Utilization"
          period = 300
          stat = "Average"
          annotations = {
            horizontal = [
              {
                label = "Warning"
                value = 70
                color = "#ff9900"
              },
              {
                label = "Critical"
                value = 85
                color = "#d13212"
              }
            ]
          }
        }
      },
      {
        type = "metric"
        x    = 0
        y    = 7
        width = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", "${var.db_instance_identifier}"],
            ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", "${var.db_replica_identifier}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "RDS CPU Utilization"
          period = 300
          stat = "Average"
          annotations = {
            horizontal = [
              {
                label = "Warning"
                value = 70
                color = "#ff9900"
              },
              {
                label = "Critical"
                value = 85
                color = "#d13212"
              }
            ]
          }
        }
      },
      {
        type = "metric"
        x    = 12
        y    = 7
        width = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/RDS", "FreeStorageSpace", "DBInstanceIdentifier", "${var.db_instance_identifier}"],
            ["AWS/RDS", "FreeStorageSpace", "DBInstanceIdentifier", "${var.db_replica_identifier}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "RDS Free Storage Space"
          period = 300
          stat = "Average"
        }
      },
      {
        type = "metric"
        x    = 0
        y    = 13
        width = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ElastiCache", "CPUUtilization", "ReplicationGroupId", "${var.redis_replication_group_id}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "ElastiCache CPU Utilization"
          period = 300
          stat = "Average"
          annotations = {
            horizontal = [
              {
                label = "Warning"
                value = 70
                color = "#ff9900"
              },
              {
                label = "Critical"
                value = 85
                color = "#d13212"
              }
            ]
          }
        }
      },
      {
        type = "metric"
        x    = 12
        y    = 13
        width = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ElastiCache", "DatabaseMemoryUsagePercentage", "ReplicationGroupId", "${var.redis_replication_group_id}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "ElastiCache Memory Usage"
          period = 300
          stat = "Average"
          annotations = {
            horizontal = [
              {
                label = "Warning"
                value = 70
                color = "#ff9900"
              },
              {
                label = "Critical"
                value = 85
                color = "#d13212"
              }
            ]
          }
        }
      },
      {
        type = "metric"
        x    = 0
        y    = 19
        width = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/S3", "BucketSizeBytes", "BucketName", "${var.document_bucket_name}", "StorageType", "StandardStorage"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "S3 Document Bucket Size"
          period = 86400
          stat = "Average"
        }
      },
      {
        type = "metric"
        x    = 12
        y    = 19
        width = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/S3", "NumberOfObjects", "BucketName", "${var.document_bucket_name}", "StorageType", "AllStorageTypes"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "S3 Document Object Count"
          period = 86400
          stat = "Average"
        }
      }
    ]
  }

  # Business Metrics Dashboard configuration
  business_metrics_dashboard = {
    widgets = [
      {
        type = "text"
        x    = 0
        y    = 0
        width = 24
        height = 1
        properties = {
          markdown = "# Business Metrics Dashboard\nKey business KPIs and SLA compliance metrics."
        }
      },
      {
        type = "metric"
        x    = 0
        y    = 1
        width = 12
        height = 6
        properties = {
          metrics = [
            ["LoanManagementSystem", "ApplicationSubmissionCount", "Status", "Submitted", "Environment", "${var.environment}"],
            ["LoanManagementSystem", "ApplicationSubmissionCount", "Status", "Approved", "Environment", "${var.environment}"],
            ["LoanManagementSystem", "ApplicationSubmissionCount", "Status", "Denied", "Environment", "${var.environment}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "Application Volume by Status"
          period = 86400
          stat = "Sum"
        }
      },
      {
        type = "metric"
        x    = 12
        y    = 1
        width = 12
        height = 6
        properties = {
          metrics = [
            ["LoanManagementSystem", "ApplicationSubmissionSuccessRate", "Environment", "${var.environment}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "Application Submission Success Rate (%)"
          period = 3600
          stat = "Average"
          annotations = {
            horizontal = [
              {
                label = "SLA Target"
                value = 99.5
                color = "#2ca02c"
              }
            ]
          }
        }
      },
      {
        type = "metric"
        x    = 0
        y    = 7
        width = 12
        height = 6
        properties = {
          metrics = [
            ["LoanManagementSystem", "TimeToDecision", "Environment", "${var.environment}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "Time to Decision (Hours)"
          period = 86400
          stat = "Average"
          annotations = {
            horizontal = [
              {
                label = "SLA Target"
                value = 48
                color = "#2ca02c"
              }
            ]
          }
        }
      },
      {
        type = "metric"
        x    = 12
        y    = 7
        width = 12
        height = 6
        properties = {
          metrics = [
            ["LoanManagementSystem", "UnderwritingDecisionComplianceRate", "Environment", "${var.environment}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "Underwriting Decision Compliance Rate (%)"
          period = 86400
          stat = "Average"
          annotations = {
            horizontal = [
              {
                label = "SLA Target"
                value = 90
                color = "#2ca02c"
              }
            ]
          }
        }
      },
      {
        type = "metric"
        x    = 0
        y    = 13
        width = 12
        height = 6
        properties = {
          metrics = [
            ["LoanManagementSystem", "DocumentGenerationComplianceRate", "Environment", "${var.environment}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "Document Generation Compliance Rate (%)"
          period = 3600
          stat = "Average"
          annotations = {
            horizontal = [
              {
                label = "SLA Target"
                value = 99
                color = "#2ca02c"
              }
            ]
          }
        }
      },
      {
        type = "metric"
        x    = 12
        y    = 13
        width = 12
        height = 6
        properties = {
          metrics = [
            ["LoanManagementSystem", "DocumentSignatureCompletionRate", "Environment", "${var.environment}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "Document Signature Completion Rate (%)"
          period = 86400
          stat = "Average"
          annotations = {
            horizontal = [
              {
                label = "SLA Target"
                value = 80
                color = "#2ca02c"
              }
            ]
          }
        }
      },
      {
        type = "metric"
        x    = 0
        y    = 19
        width = 12
        height = 6
        properties = {
          metrics = [
            ["LoanManagementSystem", "FundingDisbursementComplianceRate", "Environment", "${var.environment}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "Funding Disbursement Compliance Rate (%)"
          period = 86400
          stat = "Average"
          annotations = {
            horizontal = [
              {
                label = "SLA Target"
                value = 95
                color = "#2ca02c"
              }
            ]
          }
        }
      },
      {
        type = "metric"
        x    = 12
        y    = 19
        width = 12
        height = 6
        properties = {
          metrics = [
            ["LoanManagementSystem", "FundingVolume", "Environment", "${var.environment}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "Funding Volume ($)"
          period = 86400
          stat = "Sum"
        }
      }
    ]
  }

  # Executive Summary Dashboard configuration
  executive_summary_dashboard = {
    widgets = [
      {
        type = "text"
        x    = 0
        y    = 0
        width = 24
        height = 1
        properties = {
          markdown = "# Executive Summary Dashboard\nHigh-level overview of system health and key business metrics."
        }
      },
      {
        type = "metric"
        x    = 0
        y    = 1
        width = 8
        height = 6
        properties = {
          metrics = [
            ["LoanManagementSystem", "SystemHealthScore", "Environment", "${var.environment}"]
          ]
          view = "gauge"
          region = "${var.region}"
          title = "System Health"
          period = 300
          stat = "Average"
          yAxis = {
            left = {
              min = 0
              max = 100
            }
          }
          gauge = {
            percentageMode = true
            minValue = 0
            maxValue = 100
          }
        }
      },
      {
        type = "metric"
        x    = 8
        y    = 1
        width = 8
        height = 6
        properties = {
          metrics = [
            ["LoanManagementSystem", "SLAComplianceScore", "Environment", "${var.environment}"]
          ]
          view = "gauge"
          region = "${var.region}"
          title = "SLA Compliance"
          period = 300
          stat = "Average"
          yAxis = {
            left = {
              min = 0
              max = 100
            }
          }
          gauge = {
            percentageMode = true
            minValue = 0
            maxValue = 100
          }
        }
      },
      {
        type = "metric"
        x    = 16
        y    = 1
        width = 8
        height = 6
        properties = {
          metrics = [
            ["LoanManagementSystem", "UserSatisfactionScore", "Environment", "${var.environment}"]
          ]
          view = "gauge"
          region = "${var.region}"
          title = "User Satisfaction"
          period = 300
          stat = "Average"
          yAxis = {
            left = {
              min = 0
              max = 100
            }
          }
          gauge = {
            percentageMode = true
            minValue = 0
            maxValue = 100
          }
        }
      },
      {
        type = "metric"
        x    = 0
        y    = 7
        width = 24
        height = 6
        properties = {
          metrics = [
            ["LoanManagementSystem", "ApplicationSubmissionCount", "Status", "Submitted", "Environment", "${var.environment}"],
            ["LoanManagementSystem", "ApplicationSubmissionCount", "Status", "Approved", "Environment", "${var.environment}"],
            ["LoanManagementSystem", "ApplicationSubmissionCount", "Status", "Denied", "Environment", "${var.environment}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "Application Volume Trend"
          period = 86400
          stat = "Sum"
        }
      },
      {
        type = "metric"
        x    = 0
        y    = 13
        width = 12
        height = 6
        properties = {
          metrics = [
            ["LoanManagementSystem", "ApprovalRate", "Environment", "${var.environment}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "Approval Rate (%)"
          period = 86400
          stat = "Average"
        }
      },
      {
        type = "metric"
        x    = 12
        y    = 13
        width = 12
        height = 6
        properties = {
          metrics = [
            ["LoanManagementSystem", "FundingVolume", "Environment", "${var.environment}"]
          ]
          view = "timeSeries"
          stacked = false
          region = "${var.region}"
          title = "Funding Volume ($)"
          period = 86400
          stat = "Sum"
        }
      },
      {
        type = "metric"
        x    = 0
        y    = 19
        width = 24
        height = 6
        properties = {
          metrics = [
            ["LoanManagementSystem", "ActiveUsers", "UserType", "Borrower", "Environment", "${var.environment}"],
            ["LoanManagementSystem", "ActiveUsers", "UserType", "SchoolAdmin", "Environment", "${var.environment}"],
            ["LoanManagementSystem", "ActiveUsers", "UserType", "Underwriter", "Environment", "${var.environment}"],
            ["LoanManagementSystem", "ActiveUsers", "UserType", "QC", "Environment", "${var.environment}"],
            ["LoanManagementSystem", "ActiveUsers", "UserType", "SystemAdmin", "Environment", "${var.environment}"]
          ]
          view = "timeSeries"
          stacked = true
          region = "${var.region}"
          title = "System Usage by Role"
          period = 86400
          stat = "Maximum"
        }
      }
    ]
  }
}

# Create CloudWatch dashboards 
resource "aws_cloudwatch_dashboard" "system_overview" {
  dashboard_name = "${var.environment}-system-overview"
  dashboard_body = jsonencode(local.system_overview_dashboard)
  
  tags = {
    Environment = var.environment
    Component   = "Monitoring"
    ManagedBy   = "Terraform"
  }
}

resource "aws_cloudwatch_dashboard" "application_performance" {
  dashboard_name = "${var.environment}-application-performance"
  dashboard_body = jsonencode(local.application_performance_dashboard)
  
  tags = {
    Environment = var.environment
    Component   = "Monitoring"
    ManagedBy   = "Terraform"
  }
}

resource "aws_cloudwatch_dashboard" "infrastructure_metrics" {
  dashboard_name = "${var.environment}-infrastructure-metrics"
  dashboard_body = jsonencode(local.infrastructure_metrics_dashboard)
  
  tags = {
    Environment = var.environment
    Component   = "Monitoring"
    ManagedBy   = "Terraform"
  }
}

resource "aws_cloudwatch_dashboard" "business_metrics" {
  dashboard_name = "${var.environment}-business-metrics"
  dashboard_body = jsonencode(local.business_metrics_dashboard)
  
  tags = {
    Environment = var.environment
    Component   = "Monitoring"
    ManagedBy   = "Terraform"
  }
}

resource "aws_cloudwatch_dashboard" "executive_summary" {
  dashboard_name = "${var.environment}-executive-summary"
  dashboard_body = jsonencode(local.executive_summary_dashboard)
  
  tags = {
    Environment = var.environment
    Component   = "Monitoring"
    ManagedBy   = "Terraform"
  }
}

# Outputs the ARNs of created dashboards
output "dashboard_arns" {
  description = "Map of CloudWatch dashboard ARNs for reference"
  value = {
    system_overview        = aws_cloudwatch_dashboard.system_overview.dashboard_arn
    application_performance = aws_cloudwatch_dashboard.application_performance.dashboard_arn
    infrastructure_metrics = aws_cloudwatch_dashboard.infrastructure_metrics.dashboard_arn
    business_metrics       = aws_cloudwatch_dashboard.business_metrics.dashboard_arn
    executive_summary      = aws_cloudwatch_dashboard.executive_summary.dashboard_arn
  }
}