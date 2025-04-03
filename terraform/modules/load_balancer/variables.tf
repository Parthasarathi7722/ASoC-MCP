variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs"
  type        = list(string)
}

variable "environment" {
  description = "Environment name (e.g., dev, prod)"
  type        = string
}

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "deploy_wazuh" {
  description = "Whether to deploy Wazuh SIEM"
  type        = bool
  default     = true
}

variable "deploy_mcp_platform" {
  description = "Whether to deploy MCP Platform"
  type        = bool
  default     = true
}

variable "wazuh_security_group_id" {
  description = "Security group ID for Wazuh ALB"
  type        = string
}

variable "mcp_security_group_id" {
  description = "Security group ID for MCP Platform ALB"
  type        = string
}

variable "wazuh_certificate_arn" {
  description = "ARN of the SSL certificate for Wazuh ALB"
  type        = string
}

variable "mcp_certificate_arn" {
  description = "ARN of the SSL certificate for MCP Platform ALB"
  type        = string
} 