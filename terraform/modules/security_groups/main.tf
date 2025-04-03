# Wazuh Security Group
resource "aws_security_group" "wazuh" {
  count       = var.deploy_wazuh ? 1 : 0
  name        = "${var.project_name}-${var.environment}-wazuh-sg"
  description = "Security group for Wazuh SIEM"
  vpc_id      = var.vpc_id

  # SSH access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SSH access"
  }

  # Wazuh API access
  ingress {
    from_port   = 55000
    to_port     = 55000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Wazuh API access"
  }

  # Wazuh dashboard access
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Wazuh dashboard access"
  }

  # Wazuh cluster communication
  ingress {
    from_port   = 514
    to_port     = 514
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Wazuh cluster communication"
  }

  ingress {
    from_port   = 1514
    to_port     = 1514
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Wazuh cluster communication"
  }

  ingress {
    from_port   = 1515
    to_port     = 1515
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Wazuh cluster communication"
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-wazuh-sg"
    Environment = var.environment
    Project     = var.project_name
  }
}

# MCP Platform Security Group
resource "aws_security_group" "mcp_platform" {
  count       = var.deploy_mcp_platform ? 1 : 0
  name        = "${var.project_name}-${var.environment}-mcp-platform-sg"
  description = "Security group for MCP Platform"
  vpc_id      = var.vpc_id

  # SSH access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SSH access"
  }

  # MCP Platform API access
  ingress {
    from_port   = 8000
    to_port     = 8009
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "MCP Platform API access"
  }

  # Web interface access
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Web interface access (HTTP)"
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Web interface access (HTTPS)"
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-mcp-platform-sg"
    Environment = var.environment
    Project     = var.project_name
  }
} 