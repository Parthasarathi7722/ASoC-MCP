# ASoC-MCP Platform

## Overview
The ASoC-MCP (Advanced Security Operations Center - Model Context Protocol) Platform is a comprehensive security operations platform that combines the power of Wazuh SIEM with the MCP Platform for advanced security operations. This project provides a flexible deployment option, allowing users to deploy either the complete ASoC with MCP or just the MCP Platform alone.

## Architecture
The platform consists of the following components:

### Core Components
- **VPC with public and private subnets**: Secure network isolation
- **Security Groups**: Granular access control
- **S3 Buckets**: Log storage for CloudTrail, WAF, ALB, and VPC Flow logs
- **CloudWatch Logs**: Centralized logging
- **IAM Roles and Policies**: Least privilege access

### Optional Components
- **Wazuh SIEM**: Open-source security information and event management
- **MCP Platform**: AI-driven security operations platform

## Deployment Options

### Option 1: Complete ASoC with MCP
Deploy the full Advanced Security Operations Center with both Wazuh SIEM and MCP Platform.

### Option 2: MCP Platform Only
Deploy only the MCP Platform without Wazuh SIEM.

## Quick Start Guide

### Prerequisites
- AWS Account with appropriate permissions
- Terraform installed (version >= 1.0.0)
- AWS CLI configured with appropriate credentials
- SSH key pair for EC2 instance access

### Deployment
1. Clone the repository:
```bash
git clone https://github.com/your-org/ASoC-MCP.git
cd ASoC-MCP
```

2. Initialize Terraform:
```bash
cd terraform
terraform init
```

3. Create a `terraform.tfvars` file with your configuration:
```hcl
# Required variables
environment = "dev"
project_name = "asoc"
key_name = "your-key-name"

# Deployment options
deploy_wazuh = true        # Set to false to deploy only MCP Platform
deploy_mcp_platform = true # Set to false to deploy only Wazuh

# Wazuh configuration (if deploy_wazuh = true)
wazuh_admin_password = "your-secure-password"
wazuh_instance_type = "t3.large"

# MCP Platform configuration (if deploy_mcp_platform = true)
openai_api_key = "your-openai-api-key"
jwt_secret = "your-jwt-secret"
mcp_instance_type = "t3.large"

# S3 bucket configuration (optional)
cloudtrail_bucket = ""  # Leave empty to create new
waf_logs_bucket = ""    # Leave empty to create new
alb_logs_bucket = ""    # Leave empty to create new
vpc_flow_logs_bucket = "" # Leave empty to create new
```

4. Deploy the infrastructure:
```bash
terraform plan
terraform apply
```

## Component Configuration

### Wazuh Configuration
If you deployed Wazuh, you'll need to configure it. SSH into the Wazuh server and follow these steps:

1. Configure ossec.conf:
```bash
sudo nano /var/ossec/etc/ossec.conf
```

Add the following sections (modify as needed):
```xml
<ossec_config>
  <!-- Email notifications -->
  <global>
    <email_notification>yes</email_notification>
    <smtp_server>smtp.your-email-provider.com</smtp_server>
    <smtp_port>587</smtp_port>
    <smtp_user>your-email@domain.com</smtp_user>
    <smtp_password>your-email-password</smtp_password>
    <from>wazuh@your-domain.com</from>
  </global>

  <!-- Integration with MCP Platform -->
  <integration>
    <name>mcp</name>
    <api_url>https://your-mcp-platform-url/api/v1</api_url>
    <api_key>your-mcp-api-key</api_key>
  </integration>

  <!-- Add your custom rules and decoders here -->
</ossec_config>
```

2. Configure Wazuh Dashboard:
```bash
sudo nano /etc/wazuh-dashboard/wazuh_dashboard.yml
```

Update the following settings:
```yaml
server:
  host: "0.0.0.0"
  port: 443
  ssl:
    enabled: true
    certificate: /etc/wazuh-dashboard/certs/wazuh-dashboard.crt
    key: /etc/wazuh-dashboard/certs/wazuh-dashboard.key

wazuh:
  api:
    url: https://your-wazuh-manager:55000
    username: admin
    password: your-wazuh-admin-password
```

3. Restart Wazuh services:
```bash
sudo systemctl restart wazuh-manager
sudo systemctl restart wazuh-api
sudo systemctl restart wazuh-dashboard
```

### MCP Platform Configuration
If you deployed the MCP Platform, you'll need to configure it. SSH into the MCP Platform instance and follow these steps:

1. Access the MCP Platform API:
```bash
curl -X POST https://your-mcp-platform-url/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-admin-password"}'
```

2. Configure data source connectors:
```bash
curl -X POST https://your-mcp-platform-url/api/v1/connectors \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "wazuh",
    "type": "wazuh",
    "config": {
      "api_url": "https://your-wazuh-manager:55000",
      "username": "admin",
      "password": "your-wazuh-admin-password"
    }
  }'
```

## Documentation
For more detailed information, please refer to the following documentation:

- [MCP Platform Documentation](MCP-Platform/README.md): Detailed documentation for the MCP Platform
- [MCP Platform Deployment Guide](MCP-Platform/DEPLOYMENT.md): Step-by-step deployment guide for the MCP Platform
- [Wazuh Documentation](https://documentation.wazuh.com/): Official Wazuh documentation

## Security Considerations
1. Change default passwords immediately after deployment
2. Regularly update Wazuh and MCP Platform components
3. Monitor and rotate API keys and certificates
4. Implement proper network segmentation
5. Enable encryption for data at rest and in transit

## Troubleshooting
1. Check Wazuh service status:
```bash
sudo systemctl status wazuh-manager
sudo systemctl status wazuh-api
sudo systemctl status wazuh-dashboard
```

2. View Wazuh logs:
```bash
sudo tail -f /var/ossec/logs/ossec.log
```

3. Check MCP Platform logs:
```bash
docker logs mcp-platform
```

## Support
For issues and feature requests, please create a GitHub issue in this repository.

## License
This project is licensed under the MIT License - see the LICENSE file for details. 