# Wazuh Server EC2 Instance
resource "aws_instance" "wazuh_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = var.private_subnet_ids[0]
  vpc_security_group_ids = var.security_group_ids
  key_name               = var.key_name

  root_block_device {
    volume_size = 100
    volume_type = "gp3"
    encrypted   = true
  }

  user_data = templatefile("${path.module}/templates/user_data.sh", {
    wazuh_admin_password = var.wazuh_admin_password
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-wazuh-server"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Wazuh Dashboard EC2 Instance
resource "aws_instance" "wazuh_dashboard" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = var.private_subnet_ids[0]
  vpc_security_group_ids = var.security_group_ids
  key_name               = var.key_name

  root_block_device {
    volume_size = 50
    volume_type = "gp3"
    encrypted   = true
  }

  user_data = templatefile("${path.module}/templates/dashboard_user_data.sh", {
    wazuh_admin_password = var.wazuh_admin_password
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-wazuh-dashboard"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Application Load Balancer for Wazuh Dashboard
resource "aws_lb" "wazuh_dashboard" {
  name               = "${var.project_name}-${var.environment}-wazuh-dashboard-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = var.security_group_ids
  subnets            = var.public_subnet_ids

  tags = {
    Name        = "${var.project_name}-${var.environment}-wazuh-dashboard-alb"
    Environment = var.environment
    Project     = var.project_name
  }
}

# ALB Target Group
resource "aws_lb_target_group" "wazuh_dashboard" {
  name     = "${var.project_name}-${var.environment}-wazuh-dashboard-tg"
  port     = 443
  protocol = "HTTPS"
  vpc_id   = var.vpc_id
  target_type = "instance"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/"
    port                = "traffic-port"
    protocol            = "HTTPS"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-wazuh-dashboard-tg"
    Environment = var.environment
    Project     = var.project_name
  }
}

# ALB Listener
resource "aws_lb_listener" "wazuh_dashboard" {
  load_balancer_arn = aws_lb.wazuh_dashboard.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = aws_acm_certificate.wazuh_dashboard.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.wazuh_dashboard.arn
  }
}

# ALB Listener for HTTP to HTTPS redirect
resource "aws_lb_listener" "wazuh_dashboard_http" {
  load_balancer_arn = aws_lb.wazuh_dashboard.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# ACM Certificate for Wazuh Dashboard
resource "aws_acm_certificate" "wazuh_dashboard" {
  domain_name       = "wazuh.${var.project_name}.${var.environment}.example.com"
  validation_method = "DNS"

  tags = {
    Name        = "${var.project_name}-${var.environment}-wazuh-dashboard-cert"
    Environment = var.environment
    Project     = var.project_name
  }

  lifecycle {
    create_before_destroy = true
  }
}

# ALB Target Group Attachment
resource "aws_lb_target_group_attachment" "wazuh_dashboard" {
  target_group_arn = aws_lb_target_group.wazuh_dashboard.arn
  target_id        = aws_instance.wazuh_dashboard.id
  port             = 443
}

# Data source for Ubuntu AMI
data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
} 