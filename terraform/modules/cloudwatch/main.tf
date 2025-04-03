# CloudTrail Log Group
resource "aws_cloudwatch_log_group" "cloudtrail" {
  count             = var.cloudtrail_bucket != "" ? 1 : 0
  name              = "/${var.project_name}/${var.environment}/cloudtrail"
  retention_in_days = 30

  tags = {
    Name        = "${var.project_name}-${var.environment}-cloudtrail-logs"
    Environment = var.environment
    Project     = var.project_name
  }
}

# WAF Logs Log Group
resource "aws_cloudwatch_log_group" "waf_logs" {
  count             = var.waf_logs_bucket != "" ? 1 : 0
  name              = "/${var.project_name}/${var.environment}/waf-logs"
  retention_in_days = 30

  tags = {
    Name        = "${var.project_name}-${var.environment}-waf-logs"
    Environment = var.environment
    Project     = var.project_name
  }
}

# ALB Logs Log Group
resource "aws_cloudwatch_log_group" "alb_logs" {
  count             = var.alb_logs_bucket != "" ? 1 : 0
  name              = "/${var.project_name}/${var.environment}/alb-logs"
  retention_in_days = 30

  tags = {
    Name        = "${var.project_name}-${var.environment}-alb-logs"
    Environment = var.environment
    Project     = var.project_name
  }
}

# VPC Flow Logs Log Group
resource "aws_cloudwatch_log_group" "vpc_flow_logs" {
  count             = var.vpc_flow_logs_bucket != "" ? 1 : 0
  name              = "/${var.project_name}/${var.environment}/vpc-flow-logs"
  retention_in_days = 30

  tags = {
    Name        = "${var.project_name}-${var.environment}-vpc-flow-logs"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Wazuh Logs Log Group
resource "aws_cloudwatch_log_group" "wazuh_logs" {
  name              = "/${var.project_name}/${var.environment}/wazuh-logs"
  retention_in_days = 30

  tags = {
    Name        = "${var.project_name}-${var.environment}-wazuh-logs"
    Environment = var.environment
    Project     = var.project_name
  }
}

# MCP Platform Logs Log Group
resource "aws_cloudwatch_log_group" "mcp_platform_logs" {
  name              = "/${var.project_name}/${var.environment}/mcp-platform-logs"
  retention_in_days = 30

  tags = {
    Name        = "${var.project_name}-${var.environment}-mcp-platform-logs"
    Environment = var.environment
    Project     = var.project_name
  }
} 