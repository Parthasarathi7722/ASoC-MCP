#!/bin/bash

# Update system
apt-get update
apt-get upgrade -y

# Install required packages
apt-get install -y docker.io docker-compose git

# Start and enable Docker
systemctl start docker
systemctl enable docker

# Clone MCP Platform repository
git clone https://github.com/your-org/MCP-Platform.git /opt/mcp-platform
cd /opt/mcp-platform

# Create .env file
cat > .env << EOF
# Authentication Service
JWT_SECRET=${jwt_secret}
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600

# OpenAI API
OPENAI_API_KEY=${openai_api_key}

# Wazuh Integration (if provided)
WAZUH_API_URL=${wazuh_api_url}
WAZUH_USERNAME=${wazuh_username}
WAZUH_PASSWORD=${wazuh_password}
EOF

# Start MCP Platform
docker-compose up -d

# Note: Manual configuration may be required
# Please refer to the README for instructions on configuring the MCP Platform 