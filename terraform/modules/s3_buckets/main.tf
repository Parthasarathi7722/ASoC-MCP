# CloudTrail S3 Bucket
resource "aws_s3_bucket" "cloudtrail" {
  count  = var.cloudtrail_bucket == "" ? 1 : 0
  bucket = "${var.project_name}-${var.environment}-cloudtrail-logs"

  tags = {
    Name        = "${var.project_name}-${var.environment}-cloudtrail-logs"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_s3_bucket_versioning" "cloudtrail" {
  count  = var.cloudtrail_bucket == "" ? 1 : 0
  bucket = aws_s3_bucket.cloudtrail[0].id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "cloudtrail" {
  count  = var.cloudtrail_bucket == "" ? 1 : 0
  bucket = aws_s3_bucket.cloudtrail[0].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_rule" "cloudtrail" {
  count  = var.cloudtrail_bucket == "" ? 1 : 0
  bucket = aws_s3_bucket.cloudtrail[0].id

  id      = "log-expiration"
  enabled = true

  expiration {
    days = 90
  }
}

# WAF Logs S3 Bucket
resource "aws_s3_bucket" "waf_logs" {
  count  = var.waf_logs_bucket == "" ? 1 : 0
  bucket = "${var.project_name}-${var.environment}-waf-logs"

  tags = {
    Name        = "${var.project_name}-${var.environment}-waf-logs"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_s3_bucket_versioning" "waf_logs" {
  count  = var.waf_logs_bucket == "" ? 1 : 0
  bucket = aws_s3_bucket.waf_logs[0].id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "waf_logs" {
  count  = var.waf_logs_bucket == "" ? 1 : 0
  bucket = aws_s3_bucket.waf_logs[0].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_rule" "waf_logs" {
  count  = var.waf_logs_bucket == "" ? 1 : 0
  bucket = aws_s3_bucket.waf_logs[0].id

  id      = "log-expiration"
  enabled = true

  expiration {
    days = 90
  }
}

# ALB Logs S3 Bucket
resource "aws_s3_bucket" "alb_logs" {
  count  = var.alb_logs_bucket == "" ? 1 : 0
  bucket = "${var.project_name}-${var.environment}-alb-logs"

  tags = {
    Name        = "${var.project_name}-${var.environment}-alb-logs"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_s3_bucket_versioning" "alb_logs" {
  count  = var.alb_logs_bucket == "" ? 1 : 0
  bucket = aws_s3_bucket.alb_logs[0].id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "alb_logs" {
  count  = var.alb_logs_bucket == "" ? 1 : 0
  bucket = aws_s3_bucket.alb_logs[0].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_rule" "alb_logs" {
  count  = var.alb_logs_bucket == "" ? 1 : 0
  bucket = aws_s3_bucket.alb_logs[0].id

  id      = "log-expiration"
  enabled = true

  expiration {
    days = 90
  }
}

# VPC Flow Logs S3 Bucket
resource "aws_s3_bucket" "vpc_flow_logs" {
  count  = var.vpc_flow_logs_bucket == "" ? 1 : 0
  bucket = "${var.project_name}-${var.environment}-vpc-flow-logs"

  tags = {
    Name        = "${var.project_name}-${var.environment}-vpc-flow-logs"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_s3_bucket_versioning" "vpc_flow_logs" {
  count  = var.vpc_flow_logs_bucket == "" ? 1 : 0
  bucket = aws_s3_bucket.vpc_flow_logs[0].id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "vpc_flow_logs" {
  count  = var.vpc_flow_logs_bucket == "" ? 1 : 0
  bucket = aws_s3_bucket.vpc_flow_logs[0].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_rule" "vpc_flow_logs" {
  count  = var.vpc_flow_logs_bucket == "" ? 1 : 0
  bucket = aws_s3_bucket.vpc_flow_logs[0].id

  id      = "log-expiration"
  enabled = true

  expiration {
    days = 90
  }
} 