# Model Context Protocol (MCP) Platform

## Overview

The **Model Context Protocol (MCP) Platform** is a microservices-based system for AI-driven cybersecurity operations. It coordinates multiple specialized services to ingest security logs, analyze them with AI (Large Language Models), and automate incident response workflows.

## Key Features

- **AI-Orchestrated Analysis:** LLM Orchestrator service manages interactions with Large Language Models
- **Specialized Security Agents:** Dedicated microservices for Triage, Investigation, Threat Intel, and Remediation
- **Memory and Context:** Fast in-memory data store for context retention
- **Automated Workflows:** Workflow Engine for executing security playbooks
- **Extensible Connectors:** Pluggable Data Source Connectors for various log sources
- **Secure and Modular:** Robust Authentication system with JWT, OAuth2, API keys

## Architecture

The platform consists of several microservices:

1. **Core Services:**
   - LLM Orchestrator
   - Agent Manager
   - Memory System (Redis)
   - Workflow Engine (Celery)

2. **Security Agents:**
   - Triage Agent
   - Investigation Agent
   - Threat Intel Agent
   - Remediation Agent

3. **Support Services:**
   - Authentication Service
   - Notifications Service
   - Data Source Connectors

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Required API keys (OpenAI, VirusTotal, etc.)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/MCP-Platform.git
   cd MCP-Platform
   ```

2. Create a `.env` file with required credentials:
   ```env
   JWT_SECRET=your-secret-key
   OPENAI_API_KEY=your-openai-key
   # Add other required API keys and credentials
   ```

3. Build and start the services:
   ```bash
   docker-compose up --build
   ```

## Quick Start Guide

### 1. Authentication

1. Create an admin user:
   ```bash
   curl -X POST http://localhost:8001/users -H "Content-Type: application/json" -d '{"username": "admin", "password": "secure-password", "email": "admin@example.com", "full_name": "Admin User", "role": "admin"}'
   ```

2. Obtain authentication token:
   ```bash
   curl -X POST http://localhost:8001/token -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin&password=secure-password"
   ```

### 2. Connecting Data Sources

Add a security data source:
```bash
curl -X POST http://localhost:8003/sources -H "Content-Type: application/json" -H "Authorization: Bearer YOUR_TOKEN" -d '{"name": "Security Logs", "type": "elasticsearch", "enabled": true, "config": {"hosts": ["http://elasticsearch:9200"], "username": "elastic", "password": "your-password"}, "description": "Security event logs", "tags": ["logs", "security"]}'
```

### 3. Alert Management

Submit a security alert:
```bash
curl -X POST http://localhost:8004/alerts -H "Content-Type: application/json" -H "Authorization: Bearer YOUR_TOKEN" -d '{"title": "Suspicious Login Attempt", "description": "Multiple failed login attempts from IP 192.168.1.100", "source": "IDS", "severity": "medium", "indicators": [{"type": "ip", "value": "192.168.1.100"}]}'
```

### 4. Investigation and Remediation

Initiate an investigation:
```bash
curl -X POST http://localhost:8004/alerts/YOUR_ALERT_ID/investigate -H "Authorization: Bearer YOUR_TOKEN"
```

Request remediation:
```bash
curl -X POST http://localhost:8004/alerts/YOUR_ALERT_ID/remediate -H "Authorization: Bearer YOUR_TOKEN" -d '{"actions": ["block_ip", "reset_password"]}'
```

## Real-World Use Cases

### Automated Alert Triage and Investigation
Configure data sources to feed alerts into the MCP Platform. The Triage Agent automatically analyzes and prioritizes alerts, while the Investigation Agent conducts initial analysis of high-priority alerts.

### Threat Intelligence Integration
Configure the Threat Intel Agent with your threat intelligence API keys. When an alert contains indicators (IPs, domains, hashes), the agent automatically enriches them to determine if the alert represents a real threat.

### Automated Remediation
Configure the Remediation Agent with your security tools. Define remediation playbooks for common scenarios. When an investigation confirms a threat, the agent automatically executes remediation actions.

## Development

### Adding New Connectors

1. Create a new connector in the `connectors/` directory
2. Implement the required interface
3. Add configuration to `docker-compose.yml`

### Modifying Playbooks

1. Update the Agent Manager's playbook definitions
2. Test the changes using the provided test endpoints

## For More Information

For detailed documentation, environment configuration examples, and advanced usage scenarios, please refer to the [MCP Platform README](MCP-Platform/README.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details. 