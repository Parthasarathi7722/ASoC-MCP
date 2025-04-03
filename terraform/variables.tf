variable "aws_region" {
  description = "AWS region for resource deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (e.g., dev, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "asoc"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "key_name" {
  description = "Name of the SSH key pair for EC2 instances"
  type        = string
  default     = "asoc-key"
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

variable "wazuh_instance_type" {
  description = "EC2 instance type for Wazuh server"
  type        = string
  default     = "t3.large"
}

variable "mcp_instance_type" {
  description = "EC2 instance type for MCP Platform"
  type        = string
  default     = "t3.large"
}

variable "wazuh_admin_password" {
  description = "Admin password for Wazuh"
  type        = string
  sensitive   = true
  default     = "ChangeMe123!"
}

variable "openai_api_key" {
  description = "OpenAI API key for MCP Platform"
  type        = string
  sensitive   = true
  default     = ""
}

variable "jwt_secret" {
  description = "JWT secret for MCP Platform"
  type        = string
  sensitive   = true
  default     = "ChangeMe123!"
}

variable "cloudtrail_bucket" {
  description = "Name of existing CloudTrail S3 bucket (leave empty to create new)"
  type        = string
  default     = ""
}

variable "waf_logs_bucket" {
  description = "Name of existing WAF logs S3 bucket (leave empty to create new)"
  type        = string
  default     = ""
}

variable "alb_logs_bucket" {
  description = "Name of existing ALB logs S3 bucket (leave empty to create new)"
  type        = string
  default     = ""
}

variable "vpc_flow_logs_bucket" {
  description = "Name of existing VPC flow logs S3 bucket (leave empty to create new)"
  type        = string
  default     = ""
} 