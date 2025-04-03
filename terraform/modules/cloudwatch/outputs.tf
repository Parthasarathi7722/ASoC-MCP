output "cloudtrail_log_group_name" {
  description = "Name of the CloudTrail CloudWatch log group"
  value       = var.cloudtrail_bucket != "" ? aws_cloudwatch_log_group.cloudtrail[0].name : ""
}

output "waf_logs_log_group_name" {
  description = "Name of the WAF logs CloudWatch log group"
  value       = var.waf_logs_bucket != "" ? aws_cloudwatch_log_group.waf_logs[0].name : ""
}

output "alb_logs_log_group_name" {
  description = "Name of the ALB logs CloudWatch log group"
  value       = var.alb_logs_bucket != "" ? aws_cloudwatch_log_group.alb_logs[0].name : ""
}

output "vpc_flow_logs_log_group_name" {
  description = "Name of the VPC Flow logs CloudWatch log group"
  value       = var.vpc_flow_logs_bucket != "" ? aws_cloudwatch_log_group.vpc_flow_logs[0].name : ""
}

output "wazuh_logs_log_group_name" {
  description = "Name of the Wazuh CloudWatch log group"
  value       = aws_cloudwatch_log_group.wazuh_logs.name
}

output "mcp_platform_logs_log_group_name" {
  description = "Name of the MCP Platform CloudWatch log group"
  value       = aws_cloudwatch_log_group.mcp_platform_logs.name
} 