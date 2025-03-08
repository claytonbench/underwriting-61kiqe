# WAF Rules for Loan Management System
# This file defines AWS WAF (Web Application Firewall) rules to protect the application
# from common web vulnerabilities, SQL injection, and rate-based attacks.

# Local variables for common tags
locals {
  common_tags = {
    Project   = "LoanManagementSystem"
    ManagedBy = "Terraform"
  }
}

# Regex pattern set for detecting sensitive data like SSNs and credit card numbers
resource "aws_wafv2_regex_pattern_set" "sensitive_data_patterns" {
  name        = "${var.environment}-sensitive-data-patterns"
  description = "Patterns to detect sensitive data like SSNs, credit card numbers, etc."
  scope       = "REGIONAL"

  regular_expression {
    regex_string = "\\b\\d{3}-\\d{2}-\\d{4}\\b"  # SSN format: XXX-XX-XXXX
  }

  regular_expression {
    regex_string = "\\b\\d{9}\\b"  # SSN without dashes
  }

  regular_expression {
    regex_string = "\\b(?:\\d[ -]*?){13,16}\\b"  # Credit card numbers (13-16 digits)
  }

  tags = {
    Name        = "${var.environment}-sensitive-data-patterns"
    Environment = var.environment
  }
}

# Main WAF Web ACL
resource "aws_wafv2_web_acl" "main" {
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

  # AWS Managed Rules SQL Injection Rule Set
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

  # AWS Managed Rules Known Bad Inputs Rule Set
  rule {
    name     = "AWSManagedRulesKnownBadInputsRuleSet"
    priority = 30

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesKnownBadInputsRuleSet"
      sampled_requests_enabled   = true
    }
  }

  # Rate-based rule
  rule {
    name     = "RateBasedRule"
    priority = 40

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

  # Sensitive data protection rule
  rule {
    name     = "SensitiveDataProtection"
    priority = 50

    action {
      block {}
    }

    statement {
      or_statement {
        statement {
          regex_pattern_set_reference_statement {
            arn = aws_wafv2_regex_pattern_set.sensitive_data_patterns.arn
            field_to_match {
              uri_path {}
            }
            text_transformation {
              priority = 0
              type     = "NONE"
            }
          }
        }

        statement {
          regex_pattern_set_reference_statement {
            arn = aws_wafv2_regex_pattern_set.sensitive_data_patterns.arn
            field_to_match {
              query_string {}
            }
            text_transformation {
              priority = 0
              type     = "NONE"
            }
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "SensitiveDataProtection"
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

# Associate WAF with Application Load Balancer
resource "aws_wafv2_web_acl_association" "alb_association" {
  count = var.alb_arn != "" ? 1 : 0

  resource_arn = var.alb_arn
  web_acl_arn  = aws_wafv2_web_acl.main.arn
}

# CloudWatch alarm for high number of requests blocked by WAF
resource "aws_cloudwatch_metric_alarm" "waf_blocked_requests_high" {
  count = var.sns_topic_arn != "" ? 1 : 0

  alarm_name          = "${var.environment}-waf-blocked-requests-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "BlockedRequests"
  namespace           = "AWS/WAFV2"
  period              = 300
  statistic           = "Sum"
  threshold           = var.waf_blocked_requests_threshold
  alarm_description   = "This metric monitors the number of requests blocked by WAF"

  dimensions = {
    WebACL  = aws_wafv2_web_acl.main.name
    Region  = var.region
    Rule    = "ALL"
  }

  alarm_actions = [var.sns_topic_arn]
  ok_actions    = [var.sns_topic_arn]

  tags = {
    Environment = var.environment
    Component   = "WAF"
  }
}

# Variables
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

variable "alb_arn" {
  type        = string
  description = "ARN of the Application Load Balancer to associate with WAF"
  default     = ""
}

variable "waf_rate_limit" {
  type        = number
  description = "Request rate limit for WAF rate-based rules"
  default     = 1000
}

variable "waf_blocked_requests_threshold" {
  type        = number
  description = "Threshold for WAF blocked requests alarm"
  default     = 100
}

variable "sns_topic_arn" {
  type        = string
  description = "ARN of the SNS topic for alarm notifications"
  default     = ""
}

# Output variables
output "web_acl_arn" {
  description = "ARN of the WAF Web ACL"
  value       = aws_wafv2_web_acl.main.arn
}

output "web_acl_id" {
  description = "ID of the WAF Web ACL"
  value       = aws_wafv2_web_acl.main.id
}