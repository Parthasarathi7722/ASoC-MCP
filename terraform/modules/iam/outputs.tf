output "wazuh_role_arn" {
  description = "ARN of the Wazuh IAM role"
  value       = aws_iam_role.wazuh.arn
}

output "wazuh_instance_profile_name" {
  description = "Name of the Wazuh IAM instance profile"
  value       = aws_iam_instance_profile.wazuh.name
}

output "mcp_platform_role_arn" {
  description = "ARN of the MCP Platform IAM role"
  value       = aws_iam_role.mcp_platform.arn
}

output "mcp_platform_instance_profile_name" {
  description = "Name of the MCP Platform IAM instance profile"
  value       = aws_iam_instance_profile.mcp_platform.name
} 