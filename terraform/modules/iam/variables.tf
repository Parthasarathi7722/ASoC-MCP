variable "environment" {
  description = "Environment name (e.g., dev, prod)"
  type        = string
}

variable "project_name" {
  description = "Name of the project"
  type        = string
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

variable "kms_key_arn" {
  description = "ARN of the KMS key used for encryption"
  type        = string
} 