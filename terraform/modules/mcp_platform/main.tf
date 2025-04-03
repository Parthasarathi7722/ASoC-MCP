# MCP Platform EC2 Instance
resource "aws_instance" "mcp_platform" {
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

  user_data = templatefile("${path.module}/templates/user_data.sh", {
    openai_api_key = var.openai_api_key
    jwt_secret     = var.jwt_secret
    wazuh_api_url  = var.wazuh_api_url
    wazuh_username = var.wazuh_username
    wazuh_password = var.wazuh_password
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-mcp-platform"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Application Load Balancer for MCP Platform
resource "aws_lb" "mcp_platform" {
  name               = "${var.project_name}-${var.environment}-mcp-platform-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = var.security_group_ids
  subnets            = var.public_subnet_ids

  tags = {
    Name        = "${var.project_name}-${var.environment}-mcp-platform-alb"
    Environment = var.environment
    Project     = var.project_name
  }
}

# ALB Target Group
resource "aws_lb_target_group" "mcp_platform" {
  name     = "${var.project_name}-${var.environment}-mcp-platform-tg"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = var.vpc_id
  target_type = "instance"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-mcp-platform-tg"
    Environment = var.environment
    Project     = var.project_name
  }
}

# ALB Listener
resource "aws_lb_listener" "mcp_platform" {
  load_balancer_arn = aws_lb.mcp_platform.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.mcp_platform.arn
  }
}

# ALB Target Group Attachment
resource "aws_lb_target_group_attachment" "mcp_platform" {
  target_group_arn = aws_lb_target_group.mcp_platform.arn
  target_id        = aws_instance.mcp_platform.id
  port             = 8000
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