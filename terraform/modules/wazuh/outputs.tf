output "wazuh_server_id" {
  description = "ID of the Wazuh server EC2 instance"
  value       = aws_instance.wazuh_server.id
}

output "wazuh_dashboard_id" {
  description = "ID of the Wazuh dashboard EC2 instance"
  value       = aws_instance.wazuh_dashboard.id
}

output "wazuh_dashboard_url" {
  description = "URL of the Wazuh dashboard"
  value       = "https://wazuh.${var.project_name}.${var.environment}.example.com"
}

output "wazuh_api_url" {
  description = "URL of the Wazuh API"
  value       = "https://${aws_instance.wazuh_server.private_ip}:55000"
}

output "wazuh_username" {
  description = "Default username for Wazuh"
  value       = "admin"
}

output "wazuh_password" {
  description = "Password for Wazuh admin user"
  value       = var.wazuh_admin_password
  sensitive   = true
} 