terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  required_version = ">= 1.0.0"
}

provider "aws" {
  region = var.aws_region
}

# VPC and Networking
module "vpc" {
  source = "./modules/vpc"

  vpc_cidr             = var.vpc_cidr
  availability_zones   = var.availability_zones
  environment          = var.environment
  project_name         = var.project_name
}

# Security Groups
module "security_groups" {
  source = "./modules/security_groups"

  vpc_id              = module.vpc.vpc_id
  environment         = var.environment
  project_name        = var.project_name
  deploy_wazuh        = var.deploy_wazuh
  deploy_mcp_platform = var.deploy_mcp_platform
}

# S3 Buckets for Logs
module "s3_buckets" {
  source = "./modules/s3_buckets"

  environment         = var.environment
  project_name        = var.project_name
  cloudtrail_bucket  = var.cloudtrail_bucket
  waf_logs_bucket    = var.waf_logs_bucket
  alb_logs_bucket    = var.alb_logs_bucket
  vpc_flow_logs_bucket = var.vpc_flow_logs_bucket
}

# Wazuh SIEM (Optional)
module "wazuh" {
  source = "./modules/wazuh"
  count  = var.deploy_wazuh ? 1 : 0

  vpc_id              = module.vpc.vpc_id
  private_subnet_ids  = module.vpc.private_subnet_ids
  public_subnet_ids   = module.vpc.public_subnet_ids
  security_group_ids  = module.security_groups.wazuh_security_group_ids
  environment         = var.environment
  project_name        = var.project_name
  instance_type       = var.wazuh_instance_type
  key_name            = var.key_name
  wazuh_admin_password = var.wazuh_admin_password
}

# MCP Platform (Optional)
module "mcp_platform" {
  source = "./modules/mcp_platform"
  count  = var.deploy_mcp_platform ? 1 : 0

  vpc_id              = module.vpc.vpc_id
  private_subnet_ids  = module.vpc.private_subnet_ids
  public_subnet_ids   = module.vpc.public_subnet_ids
  security_group_ids  = module.security_groups.mcp_security_group_ids
  environment         = var.environment
  project_name        = var.project_name
  instance_type       = var.mcp_instance_type
  key_name            = var.key_name
  openai_api_key      = var.openai_api_key
  jwt_secret          = var.jwt_secret
  wazuh_api_url       = var.deploy_wazuh ? module.wazuh[0].wazuh_api_url : ""
  wazuh_username      = var.deploy_wazuh ? module.wazuh[0].wazuh_username : ""
  wazuh_password      = var.deploy_wazuh ? module.wazuh[0].wazuh_password : ""
}

# CloudWatch Logs
module "cloudwatch" {
  source = "./modules/cloudwatch"

  environment         = var.environment
  project_name        = var.project_name
  cloudtrail_bucket  = var.cloudtrail_bucket
  waf_logs_bucket    = var.waf_logs_bucket
  alb_logs_bucket    = var.alb_logs_bucket
  vpc_flow_logs_bucket = var.vpc_flow_logs_bucket
}

# IAM Roles and Policies
module "iam" {
  source = "./modules/iam"

  environment         = var.environment
  project_name        = var.project_name
  cloudtrail_bucket  = var.cloudtrail_bucket
  waf_logs_bucket    = var.waf_logs_bucket
  alb_logs_bucket    = var.alb_logs_bucket
  vpc_flow_logs_bucket = var.vpc_flow_logs_bucket
}

# Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "wazuh_dashboard_url" {
  description = "URL of the Wazuh dashboard"
  value       = var.deploy_wazuh ? module.wazuh[0].wazuh_dashboard_url : ""
}

output "mcp_platform_url" {
  description = "URL of the MCP Platform"
  value       = var.deploy_mcp_platform ? module.mcp_platform[0].mcp_platform_url : ""
}

output "cloudtrail_bucket_name" {
  description = "Name of the CloudTrail S3 bucket"
  value       = module.s3_buckets.cloudtrail_bucket_name
}

output "waf_logs_bucket_name" {
  description = "Name of the WAF logs S3 bucket"
  value       = module.s3_buckets.waf_logs_bucket_name
}

output "alb_logs_bucket_name" {
  description = "Name of the ALB logs S3 bucket"
  value       = module.s3_buckets.alb_logs_bucket_name
}

output "vpc_flow_logs_bucket_name" {
  description = "Name of the VPC Flow logs S3 bucket"
  value       = module.s3_buckets.vpc_flow_logs_bucket_name
} 