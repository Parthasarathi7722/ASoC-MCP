output "cloudtrail_bucket_name" {
  description = "Name of the CloudTrail S3 bucket"
  value       = var.cloudtrail_bucket == "" ? aws_s3_bucket.cloudtrail[0].id : var.cloudtrail_bucket
}

output "waf_logs_bucket_name" {
  description = "Name of the WAF logs S3 bucket"
  value       = var.waf_logs_bucket == "" ? aws_s3_bucket.waf_logs[0].id : var.waf_logs_bucket
}

output "alb_logs_bucket_name" {
  description = "Name of the ALB logs S3 bucket"
  value       = var.alb_logs_bucket == "" ? aws_s3_bucket.alb_logs[0].id : var.alb_logs_bucket
}

output "vpc_flow_logs_bucket_name" {
  description = "Name of the VPC flow logs S3 bucket"
  value       = var.vpc_flow_logs_bucket == "" ? aws_s3_bucket.vpc_flow_logs[0].id : var.vpc_flow_logs_bucket
}

output "cloudtrail_bucket_arn" {
  description = "ARN of the CloudTrail S3 bucket"
  value       = var.cloudtrail_bucket == "" ? aws_s3_bucket.cloudtrail[0].arn : "arn:aws:s3:::${var.cloudtrail_bucket}"
}

output "waf_logs_bucket_arn" {
  description = "ARN of the WAF logs S3 bucket"
  value       = var.waf_logs_bucket == "" ? aws_s3_bucket.waf_logs[0].arn : "arn:aws:s3:::${var.waf_logs_bucket}"
}

output "alb_logs_bucket_arn" {
  description = "ARN of the ALB logs S3 bucket"
  value       = var.alb_logs_bucket == "" ? aws_s3_bucket.alb_logs[0].arn : "arn:aws:s3:::${var.alb_logs_bucket}"
}

output "vpc_flow_logs_bucket_arn" {
  description = "ARN of the VPC flow logs S3 bucket"
  value       = var.vpc_flow_logs_bucket == "" ? aws_s3_bucket.vpc_flow_logs[0].arn : "arn:aws:s3:::${var.vpc_flow_logs_bucket}"
} 