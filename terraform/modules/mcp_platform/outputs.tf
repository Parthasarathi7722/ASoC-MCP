output "mcp_platform_id" {
  description = "ID of the MCP Platform EC2 instance"
  value       = aws_instance.mcp_platform.id
}

output "mcp_platform_url" {
  description = "URL of the MCP Platform"
  value       = "http://${aws_lb.mcp_platform.dns_name}"
}

output "mcp_platform_private_ip" {
  description = "Private IP of the MCP Platform EC2 instance"
  value       = aws_instance.mcp_platform.private_ip
} 