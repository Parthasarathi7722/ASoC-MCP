output "wazuh_security_group_id" {
  description = "ID of the Wazuh security group"
  value       = var.deploy_wazuh ? aws_security_group.wazuh[0].id : ""
}

output "mcp_security_group_id" {
  description = "ID of the MCP Platform security group"
  value       = var.deploy_mcp_platform ? aws_security_group.mcp_platform[0].id : ""
}

output "wazuh_security_group_ids" {
  description = "List of Wazuh security group IDs"
  value       = var.deploy_wazuh ? [aws_security_group.wazuh[0].id] : []
}

output "mcp_security_group_ids" {
  description = "List of MCP Platform security group IDs"
  value       = var.deploy_mcp_platform ? [aws_security_group.mcp_platform[0].id] : []
} 