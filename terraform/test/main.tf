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
  region = "us-east-1"
}

module "vpc" {
  source = "../modules/vpc"

  vpc_cidr           = "10.0.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b"]
  environment        = "test"
  project_name       = "parthasarathi7722-asoc-test"
}

module "security_groups" {
  source = "../modules/security_groups"

  vpc_id              = module.vpc.vpc_id
  environment         = "test"
  project_name        = "parthasarathi7722-asoc-test"
  deploy_wazuh        = true
  deploy_mcp_platform = true
}

module "s3_buckets" {
  source = "../modules/s3_buckets"

  environment         = "test"
  project_name        = "parthasarathi7722-asoc-test"
  cloudtrail_bucket  = ""
  waf_logs_bucket    = ""
  alb_logs_bucket    = ""
  vpc_flow_logs_bucket = ""
}

module "kms" {
  source = "../modules/kms"

  environment  = "test"
  project_name = "parthasarathi7722-asoc-test"
}

module "iam" {
  source = "../modules/iam"

  environment         = "test"
  project_name        = "parthasarathi7722-asoc-test"
  cloudtrail_bucket  = module.s3_buckets.cloudtrail_bucket_name
  waf_logs_bucket    = module.s3_buckets.waf_logs_bucket_name
  alb_logs_bucket    = module.s3_buckets.alb_logs_bucket_name
  vpc_flow_logs_bucket = module.s3_buckets.vpc_flow_logs_bucket_name
  deploy_wazuh        = true
  deploy_mcp_platform = true
  kms_key_arn         = module.kms.kms_key_arn
}

module "load_balancer" {
  source = "../modules/load_balancer"

  vpc_id              = module.vpc.vpc_id
  private_subnet_ids  = module.vpc.private_subnet_ids
  environment         = "test"
  project_name        = "parthasarathi7722-asoc-test"
  deploy_wazuh        = true
  deploy_mcp_platform = true
  wazuh_security_group_id = module.security_groups.wazuh_security_group_id
  mcp_security_group_id   = module.security_groups.mcp_security_group_id
  wazuh_certificate_arn   = "arn:aws:acm:us-east-1:123456789012:certificate/test-cert"
  mcp_certificate_arn     = "arn:aws:acm:us-east-1:123456789012:certificate/test-cert"
}

module "wazuh" {
  source = "../modules/wazuh"

  vpc_id              = module.vpc.vpc_id
  private_subnet_ids  = module.vpc.private_subnet_ids
  public_subnet_ids   = module.vpc.public_subnet_ids
  security_group_ids  = module.security_groups.wazuh_security_group_ids
  environment         = "test"
  project_name        = "parthasarathi7722-asoc-test"
  instance_type       = "t3.micro"
  key_name            = "test-key"
  wazuh_admin_password = "Test123!"
}

module "mcp_platform" {
  source = "../modules/mcp_platform"

  vpc_id              = module.vpc.vpc_id
  private_subnet_ids  = module.vpc.private_subnet_ids
  public_subnet_ids   = module.vpc.public_subnet_ids
  security_group_ids  = module.security_groups.mcp_security_group_ids
  environment         = "test"
  project_name        = "parthasarathi7722-asoc-test"
  instance_type       = "t3.micro"
  key_name            = "test-key"
  openai_api_key      = "test-key"
  jwt_secret          = "test-secret"
  wazuh_api_url       = module.wazuh.wazuh_api_url
  wazuh_username      = module.wazuh.wazuh_username
  wazuh_password      = module.wazuh.wazuh_password
} 