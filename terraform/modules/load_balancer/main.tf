resource "aws_lb" "wazuh" {
  count              = var.deploy_wazuh ? 1 : 0
  name               = "${var.project_name}-${var.environment}-wazuh-alb"
  internal           = true
  load_balancer_type = "application"
  security_groups    = [var.wazuh_security_group_id]
  subnets            = var.private_subnet_ids

  tags = {
    Name        = "${var.project_name}-${var.environment}-wazuh-alb"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_lb_target_group" "wazuh" {
  count       = var.deploy_wazuh ? 1 : 0
  name        = "${var.project_name}-${var.environment}-wazuh-tg"
  port        = 443
  protocol    = "HTTPS"
  vpc_id      = var.vpc_id
  target_type = "instance"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher            = "200"
    path               = "/"
    port               = "traffic-port"
    protocol           = "HTTPS"
    timeout            = 5
    unhealthy_threshold = 2
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-wazuh-tg"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_lb_listener" "wazuh" {
  count             = var.deploy_wazuh ? 1 : 0
  load_balancer_arn = aws_lb.wazuh[0].arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = var.wazuh_certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.wazuh[0].arn
  }
}

resource "aws_lb" "mcp_platform" {
  count              = var.deploy_mcp_platform ? 1 : 0
  name               = "${var.project_name}-${var.environment}-mcp-alb"
  internal           = true
  load_balancer_type = "application"
  security_groups    = [var.mcp_security_group_id]
  subnets            = var.private_subnet_ids

  tags = {
    Name        = "${var.project_name}-${var.environment}-mcp-alb"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_lb_target_group" "mcp_platform" {
  count       = var.deploy_mcp_platform ? 1 : 0
  name        = "${var.project_name}-${var.environment}-mcp-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "instance"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher            = "200"
    path               = "/health"
    port               = "traffic-port"
    protocol           = "HTTP"
    timeout            = 5
    unhealthy_threshold = 2
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-mcp-tg"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_lb_listener" "mcp_platform" {
  count             = var.deploy_mcp_platform ? 1 : 0
  load_balancer_arn = aws_lb.mcp_platform[0].arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = var.mcp_certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.mcp_platform[0].arn
  }
} 