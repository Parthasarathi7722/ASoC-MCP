variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name (e.g., dev, prod)"
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