variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs"
  type        = list(string)
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs"
  type        = list(string)
}

variable "security_group_ids" {
  description = "List of security group IDs"
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

variable "instance_type" {
  description = "EC2 instance type for MCP Platform"
  type        = string
  default     = "t3.large"
}

variable "key_name" {
  description = "Name of the SSH key pair to use for EC2 instances"
  type        = string
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
  default     = ""
}

variable "wazuh_api_url" {
  description = "URL of the Wazuh API"
  type        = string
  default     = ""
}

variable "wazuh_username" {
  description = "Username for Wazuh API"
  type        = string
  default     = ""
}

variable "wazuh_password" {
  description = "Password for Wazuh API"
  type        = string
  sensitive   = true
  default     = ""
} 