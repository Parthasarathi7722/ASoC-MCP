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

# Install Wazuh dashboard
apt-get install -y wazuh-dashboard

# Start and enable Wazuh dashboard
systemctl daemon-reload
systemctl enable wazuh-dashboard
systemctl start wazuh-dashboard

# Note: Manual configuration required
# Please refer to the README for instructions on configuring the dashboard 