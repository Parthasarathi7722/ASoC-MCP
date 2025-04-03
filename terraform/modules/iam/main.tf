# IAM Role for Wazuh
resource "aws_iam_role" "wazuh" {
  count = var.deploy_wazuh ? 1 : 0
  name  = "${var.project_name}-${var.environment}-wazuh-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-wazuh-role"
    Environment = var.environment
    Project     = var.project_name
  }
}

# IAM Instance Profile for Wazuh
resource "aws_iam_instance_profile" "wazuh" {
  count = var.deploy_wazuh ? 1 : 0
  name  = "${var.project_name}-${var.environment}-wazuh-profile"
  role  = aws_iam_role.wazuh[0].name
}

# Wazuh S3 Access Policy
resource "aws_iam_policy" "wazuh_s3" {
  count = var.deploy_wazuh ? 1 : 0
  name  = "${var.project_name}-${var.environment}-wazuh-s3-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.cloudtrail_bucket}",
          "arn:aws:s3:::${var.cloudtrail_bucket}/*",
          "arn:aws:s3:::${var.waf_logs_bucket}",
          "arn:aws:s3:::${var.waf_logs_bucket}/*",
          "arn:aws:s3:::${var.alb_logs_bucket}",
          "arn:aws:s3:::${var.alb_logs_bucket}/*",
          "arn:aws:s3:::${var.vpc_flow_logs_bucket}",
          "arn:aws:s3:::${var.vpc_flow_logs_bucket}/*"
        ]
      }
    ]
  })
}

# Wazuh CloudWatch Logs Policy
resource "aws_iam_policy" "wazuh_cloudwatch" {
  count = var.deploy_wazuh ? 1 : 0
  name  = "${var.project_name}-${var.environment}-wazuh-cloudwatch-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = [
          "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/wazuh/*"
        ]
      }
    ]
  })
}

# Wazuh KMS Policy for Encryption
resource "aws_iam_policy" "wazuh_kms" {
  count = var.deploy_wazuh ? 1 : 0
  name  = "${var.project_name}-${var.environment}-wazuh-kms-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = [var.kms_key_arn]
      }
    ]
  })
}

# Attach policies to Wazuh role
resource "aws_iam_role_policy_attachment" "wazuh_s3" {
  count      = var.deploy_wazuh ? 1 : 0
  role       = aws_iam_role.wazuh[0].name
  policy_arn = aws_iam_policy.wazuh_s3[0].arn
}

resource "aws_iam_role_policy_attachment" "wazuh_cloudwatch" {
  count      = var.deploy_wazuh ? 1 : 0
  role       = aws_iam_role.wazuh[0].name
  policy_arn = aws_iam_policy.wazuh_cloudwatch[0].arn
}

resource "aws_iam_role_policy_attachment" "wazuh_kms" {
  count      = var.deploy_wazuh ? 1 : 0
  role       = aws_iam_role.wazuh[0].name
  policy_arn = aws_iam_policy.wazuh_kms[0].arn
}

# IAM Role for MCP Platform
resource "aws_iam_role" "mcp_platform" {
  count = var.deploy_mcp_platform ? 1 : 0
  name  = "${var.project_name}-${var.environment}-mcp-platform-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-mcp-platform-role"
    Environment = var.environment
    Project     = var.project_name
  }
}

# IAM Instance Profile for MCP Platform
resource "aws_iam_instance_profile" "mcp_platform" {
  count = var.deploy_mcp_platform ? 1 : 0
  name  = "${var.project_name}-${var.environment}-mcp-platform-profile"
  role  = aws_iam_role.mcp_platform[0].name
}

# MCP Platform S3 Access Policy
resource "aws_iam_policy" "mcp_platform_s3" {
  count = var.deploy_mcp_platform ? 1 : 0
  name  = "${var.project_name}-${var.environment}-mcp-platform-s3-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket",
          "s3:PutObject"
        ]
        Resource = [
          "arn:aws:s3:::${var.cloudtrail_bucket}",
          "arn:aws:s3:::${var.cloudtrail_bucket}/*",
          "arn:aws:s3:::${var.waf_logs_bucket}",
          "arn:aws:s3:::${var.waf_logs_bucket}/*",
          "arn:aws:s3:::${var.alb_logs_bucket}",
          "arn:aws:s3:::${var.alb_logs_bucket}/*",
          "arn:aws:s3:::${var.vpc_flow_logs_bucket}",
          "arn:aws:s3:::${var.vpc_flow_logs_bucket}/*"
        ]
      }
    ]
  })
}

# MCP Platform CloudWatch Logs Policy
resource "aws_iam_policy" "mcp_platform_cloudwatch" {
  count = var.deploy_mcp_platform ? 1 : 0
  name  = "${var.project_name}-${var.environment}-mcp-platform-cloudwatch-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = [
          "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/mcp-platform/*"
        ]
      }
    ]
  })
}

# MCP Platform KMS Policy for Encryption
resource "aws_iam_policy" "mcp_platform_kms" {
  count = var.deploy_mcp_platform ? 1 : 0
  name  = "${var.project_name}-${var.environment}-mcp-platform-kms-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey",
          "kms:Encrypt"
        ]
        Resource = [var.kms_key_arn]
      }
    ]
  })
}

# Attach policies to MCP Platform role
resource "aws_iam_role_policy_attachment" "mcp_platform_s3" {
  count      = var.deploy_mcp_platform ? 1 : 0
  role       = aws_iam_role.mcp_platform[0].name
  policy_arn = aws_iam_policy.mcp_platform_s3[0].arn
}

resource "aws_iam_role_policy_attachment" "mcp_platform_cloudwatch" {
  count      = var.deploy_mcp_platform ? 1 : 0
  role       = aws_iam_role.mcp_platform[0].name
  policy_arn = aws_iam_policy.mcp_platform_cloudwatch[0].arn
}

resource "aws_iam_role_policy_attachment" "mcp_platform_kms" {
  count      = var.deploy_mcp_platform ? 1 : 0
  role       = aws_iam_role.mcp_platform[0].name
  policy_arn = aws_iam_policy.mcp_platform_kms[0].arn
}

# Data sources
data "aws_region" "current" {}
data "aws_caller_identity" "current" {} 