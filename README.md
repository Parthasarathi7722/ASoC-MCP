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
- **KMS**: Encryption for data at rest
- **Load Balancers**: Application load balancers for Wazuh and MCP Platform

### Optional Components
- **Wazuh SIEM**: Open-source security information and event management
- **MCP Platform**: AI-driven security operations platform

## Deployment Options

### Option 1: Complete ASoC with MCP
Deploy the full Advanced Security Operations Center with both Wazuh SIEM and MCP Platform.

### Option 2: MCP Platform Only
Deploy only the MCP Platform without Wazuh SIEM.

### Option 3: Containerized Deployment
Deploy the entire platform using Docker Compose or Kubernetes for simplified management and scalability.

## Quick Start Guide

### Prerequisites
- AWS Account with appropriate permissions
- Terraform installed (version >= 1.0.0)
- AWS CLI configured with appropriate credentials
- SSH key pair for EC2 instance access
- SSL certificates for load balancers
- Docker and Docker Compose (for containerized deployment)
- Kubernetes cluster (for Kubernetes deployment)
- Helm (optional, for monitoring)

### Deployment
1. Clone the repository:
```bash
git clone https://github.com/Parthasarathi7722/ASoC-MCP.git
cd ASoC-MCP
```

2. Choose your deployment method:

#### A. Traditional Deployment (Terraform)
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

#### B. Docker Compose Deployment
```bash
# Make the deployment script executable
chmod +x deploy.sh

# Deploy using Docker Compose
./deploy.sh docker-compose
```

#### C. Kubernetes Deployment
```bash
# Make the deployment script executable
chmod +x deploy.sh

# Deploy to Kubernetes
./deploy.sh kubernetes
```

3. Create a `terraform.tfvars` file with your configuration (for Terraform deployment):
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
wazuh_certificate_arn = "arn:aws:acm:region:account:certificate/your-cert"

# MCP Platform configuration (if deploy_mcp_platform = true)
openai_api_key = "your-openai-api-key"
jwt_secret = "your-jwt-secret"
mcp_instance_type = "t3.large"
mcp_certificate_arn = "arn:aws:acm:region:account:certificate/your-cert"

# S3 bucket configuration (optional)
cloudtrail_bucket = ""  # Leave empty to create new
waf_logs_bucket = ""    # Leave empty to create new
alb_logs_bucket = ""    # Leave empty to create new
vpc_flow_logs_bucket = "" # Leave empty to create new
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

## Containerized Deployment

### Docker Compose
The project includes a Docker Compose configuration for local development and testing. The configuration includes:

- Wazuh Manager and Dashboard
- MCP Platform
- Terraform container for infrastructure deployment
- Persistent volumes for data storage
- Network configuration for secure communication

### Kubernetes
For production deployments, the project includes Kubernetes manifests:

- Namespace isolation
- ConfigMaps for application configuration
- Secrets for sensitive data
- StatefulSet for Wazuh Manager
- Deployment for MCP Platform
- Services for internal communication
- Ingress for external access
- PersistentVolumeClaims for data storage
- Network policies for pod-to-pod communication
- Monitoring with Prometheus and Grafana
- Automated backups with S3 integration

## Monitoring and Backup

### Monitoring
The Kubernetes deployment includes monitoring with Prometheus and Grafana:

1. Service monitors for Wazuh and MCP Platform
2. Alert rules for critical events
3. Grafana dashboards for visualization

### Backup and Restore
The project includes automated backup and restore procedures:

1. Daily backups of all persistent data
2. S3 integration for secure storage
3. Retention policy (7 days by default)
4. Restore functionality for disaster recovery

To restore from a backup:
```bash
./deploy.sh restore kubernetes
```

## Testing

### Infrastructure Testing
The project includes a test configuration in the `terraform/test` directory. To run the tests:

1. Navigate to the test directory:
```bash
cd terraform/test
```

2. Initialize and apply the test configuration:
```bash
terraform init
terraform plan
terraform apply
```

### MCP Platform Testing
The MCP Platform includes integration tests. To run the tests:

1. Install the test dependencies:
```bash
cd MCP-Platform
pip install -r requirements-dev.txt
```

2. Set up the test environment:
```bash
export MCP_PLATFORM_URL="https://your-mcp-platform-url"
export MCP_API_KEY="your-api-key"
```

3. Run the tests:
```bash
python -m pytest tests/
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
6. Use KMS for managing encryption keys
7. Implement least privilege IAM policies
8. Use load balancers with SSL/TLS termination
9. Apply network policies to restrict pod-to-pod communication
10. Use security contexts to run containers with non-root users
11. Regularly backup data and test restore procedures

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

4. Check load balancer health:
```bash
aws elbv2 describe-target-health --target-group-arn your-target-group-arn
```

5. For Kubernetes deployments:
```bash
# Check pod status
kubectl get pods -n asoc-mcp

# View pod logs
kubectl logs -n asoc-mcp <pod-name>

# Check service status
kubectl get services -n asoc-mcp

# Check ingress status
kubectl get ingress -n asoc-mcp
```

## Support
For issues and feature requests, please create a GitHub issue in this repository.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Author
- **Parthasarathi7722** - [GitHub Profile](https://github.com/Parthasarathi7722) 