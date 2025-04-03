# IAM Role for Wazuh
resource "aws_iam_role" "wazuh" {
  name = "${var.project_name}-${var.environment}-wazuh-role"

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
  name = "${var.project_name}-${var.environment}-wazuh-profile"
  role = aws_iam_role.wazuh.name
}

# IAM Policy for Wazuh
resource "aws_iam_policy" "wazuh" {
  name        = "${var.project_name}-${var.environment}-wazuh-policy"
  description = "Policy for Wazuh SIEM"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Effect   = "Allow"
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
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Attach Policy to Role
resource "aws_iam_role_policy_attachment" "wazuh" {
  role       = aws_iam_role.wazuh.name
  policy_arn = aws_iam_policy.wazuh.arn
}

# IAM Role for MCP Platform
resource "aws_iam_role" "mcp_platform" {
  name = "${var.project_name}-${var.environment}-mcp-platform-role"

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
  name = "${var.project_name}-${var.environment}-mcp-platform-profile"
  role = aws_iam_role.mcp_platform.name
}

# IAM Policy for MCP Platform
resource "aws_iam_policy" "mcp_platform" {
  name        = "${var.project_name}-${var.environment}-mcp-platform-policy"
  description = "Policy for MCP Platform"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:ListBucket",
          "s3:PutObject"
        ]
        Effect   = "Allow"
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
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Attach Policy to Role
resource "aws_iam_role_policy_attachment" "mcp_platform" {
  role       = aws_iam_role.mcp_platform.name
  policy_arn = aws_iam_policy.mcp_platform.arn
} 