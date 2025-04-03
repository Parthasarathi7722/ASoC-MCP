#!/bin/bash

# Update system
apt-get update
apt-get upgrade -y

# Install required packages
apt-get install -y curl apt-transport-https lsb-release gnupg2

# Add Wazuh repository
curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | apt-key add -
echo "deb https://packages.wazuh.com/4.x/apt/ stable main" | tee /etc/apt/sources.list.d/wazuh.list

# Update package list
apt-get update

# Install Wazuh manager
apt-get install -y wazuh-manager

# Start and enable Wazuh manager
systemctl daemon-reload
systemctl enable wazuh-manager
systemctl start wazuh-manager

# Install Wazuh API
apt-get install -y wazuh-api

# Start and enable Wazuh API
systemctl daemon-reload
systemctl enable wazuh-api
systemctl start wazuh-api

# Create admin user
/var/ossec/api/bin/wazuh-api-cli -u admin -p ${wazuh_admin_password}

# Note: Manual configuration required
# Please refer to the README for instructions on configuring ossec.conf 