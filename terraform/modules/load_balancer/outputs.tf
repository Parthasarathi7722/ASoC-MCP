output "wazuh_alb_dns_name" {
  description = "DNS name of the Wazuh ALB"
  value       = var.deploy_wazuh ? aws_lb.wazuh[0].dns_name : ""
}

output "wazuh_target_group_arn" {
  description = "ARN of the Wazuh target group"
  value       = var.deploy_wazuh ? aws_lb_target_group.wazuh[0].arn : ""
}

output "mcp_platform_alb_dns_name" {
  description = "DNS name of the MCP Platform ALB"
  value       = var.deploy_mcp_platform ? aws_lb.mcp_platform[0].dns_name : ""
}

output "mcp_platform_target_group_arn" {
  description = "ARN of the MCP Platform target group"
  value       = var.deploy_mcp_platform ? aws_lb_target_group.mcp_platform[0].arn : ""
} 