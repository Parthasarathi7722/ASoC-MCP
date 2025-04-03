variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
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