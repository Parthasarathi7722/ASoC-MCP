# Model Context Protocol (MCP) Platform

The Model Context Protocol (MCP) Platform is a comprehensive security automation solution that leverages AI agents to analyze, investigate, and respond to security alerts. The platform uses a modular architecture with specialized agents that work together to provide end-to-end security incident management.

## Architecture

The MCP Platform consists of the following components:

### Core Services

1. **Authentication Service**: Handles user authentication and authorization
2. **Notifications Service**: Manages notifications via email and Slack
3. **Data Source Connectors Service**: Provides a unified interface for connecting to various security data sources
4. **Agent Manager Service**: Orchestrates the workflow between agents
5. **LLM Orchestrator Service**: Manages interactions with language models

### Security Agents

1. **Triage Agent**: Analyzes security alerts, determines severity, and extracts indicators
2. **Investigation Agent**: Conducts detailed analysis using the LLM Orchestrator and generates findings
3. **Threat Intel Agent**: Enriches indicators with threat intelligence and provides risk assessments
4. **Remediation Agent**: Executes remediation actions based on investigations and provides status updates

## Features

- **Automated Alert Triage**: Quickly analyze and prioritize security alerts
- **Intelligent Investigation**: Conduct thorough investigations using AI-powered analysis
- **Threat Intelligence Integration**: Enrich alerts with contextual threat intelligence
- **Automated Remediation**: Execute remediation actions based on investigation findings
- **Multi-Channel Notifications**: Send notifications via email and Slack
- **Data Source Integration**: Connect to various security data sources (Elasticsearch, MongoDB, PostgreSQL, MySQL, Splunk, Tenable.io, Rapid7)
- **Role-Based Access Control**: Secure access to the platform based on user roles
- **API-First Design**: All functionality available via RESTful APIs

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Redis

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mcp-platform.git
   cd mcp-platform
   ```

2. Configure the environment variables:
   - Copy the sample configuration files in each service directory
   - Update the configuration with your credentials and settings

3. Build and start the services:
   ```bash
   docker-compose up -d
   ```

4. Access the services:
   - Authentication Service: http://localhost:8001
   - Notifications Service: http://localhost:8002
   - Data Source Connectors Service: http://localhost:8003
   - Agent Manager Service: http://localhost:8004
   - LLM Orchestrator Service: http://localhost:8005

### Development Setup

1. Install dependencies for each service:
   ```bash
   cd auth_service && pip install -r requirements.txt
   cd ../notifications && pip install -r requirements.txt
   cd ../data_connectors && pip install -r requirements.txt
   cd ../agent_manager && pip install -r requirements.txt
   cd ../llm_orchestrator && pip install -r requirements.txt
   cd ../agents/triage_agent && pip install -r requirements.txt
   cd ../agents/investigation_agent && pip install -r requirements.txt
   cd ../agents/threat_intel_agent && pip install -r requirements.txt
   cd ../agents/remediation_agent && pip install -r requirements.txt
   ```

2. Run the services locally:
   ```bash
   # Start Redis
   docker run -d -p 6379:6379 redis:7.2-alpine
   
   # Start each service
   cd auth_service && uvicorn app:app --reload --port 8001
   cd ../notifications && uvicorn app:app --reload --port 8002
   cd ../data_connectors && uvicorn app:app --reload --port 8003
   cd ../agent_manager && uvicorn app:app --reload --port 8004
   cd ../llm_orchestrator && uvicorn app:app --reload --port 8005
   cd ../agents/triage_agent && uvicorn app:app --reload --port 8006
   cd ../agents/investigation_agent && uvicorn app:app --reload --port 8007
   cd ../agents/threat_intel_agent && uvicorn app:app --reload --port 8008
   cd ../agents/remediation_agent && uvicorn app:app --reload --port 8009
   ```

## Usage

### Authentication

1. Create a user:
   ```bash
   curl -X POST http://localhost:8001/users -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin123", "email": "admin@example.com", "full_name": "Admin User", "role": "admin"}'
   ```

2. Get a token:
   ```bash
   curl -X POST http://localhost:8001/token -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin&password=admin123"
   ```

### Data Sources

1. Create a data source:
   ```bash
   curl -X POST http://localhost:8003/sources -H "Content-Type: application/json" -H "Authorization: Bearer YOUR_TOKEN" -d '{"name": "Elasticsearch", "type": "elasticsearch", "enabled": true, "config": {"hosts": ["http://elasticsearch:9200"], "username": "elastic", "password": "changeme"}, "description": "Elasticsearch for security logs", "tags": ["logs", "security"]}'
   ```

2. List data sources:
   ```bash
   curl -X GET http://localhost:8003/sources -H "Authorization: Bearer YOUR_TOKEN"
   ```

3. Query a data source:
   ```bash
   curl -X POST http://localhost:8003/sources/YOUR_SOURCE_ID/query -H "Content-Type: application/json" -H "Authorization: Bearer YOUR_TOKEN" -d '{"source_id": "YOUR_SOURCE_ID", "query_type": "search", "parameters": {"index": "security-events", "query": {"query_string": {"query": "severity:high"}}}, "limit": 10, "timeout": 30}'
   ```

### Alerts

1. Submit an alert:
   ```bash
   curl -X POST http://localhost:8004/alerts -H "Content-Type: application/json" -H "Authorization: Bearer YOUR_TOKEN" -d '{"title": "Suspicious Login Attempt", "description": "Multiple failed login attempts from IP 192.168.1.100", "source": "IDS", "severity": "medium", "indicators": [{"type": "ip", "value": "192.168.1.100"}]}'
   ```

2. Get alert status:
   ```bash
   curl -X GET http://localhost:8004/alerts/YOUR_ALERT_ID -H "Authorization: Bearer YOUR_TOKEN"
   ```

## Testing

Run the test suite for each service:

```bash
# Authentication Service
cd auth_service && pytest

# Notifications Service
cd ../notifications && pytest

# Data Source Connectors Service
cd ../data_connectors && pytest

# Agent Manager Service
cd ../agent_manager && pytest

# LLM Orchestrator Service
cd ../llm_orchestrator && pytest

# Agents
cd ../agents/triage_agent && pytest
cd ../agents/investigation_agent && pytest
cd ../agents/threat_intel_agent && pytest
cd ../agents/remediation_agent && pytest
```

## Deployment

### Docker Deployment

1. Build the images:
   ```bash
   docker-compose build
   ```

2. Start the services:
   ```bash
   docker-compose up -d
   ```

3. Check the logs:
   ```bash
   docker-compose logs -f
   ```

### Kubernetes Deployment

1. Apply the Kubernetes manifests:
   ```bash
   kubectl apply -f k8s/
   ```

2. Check the deployment status:
   ```bash
   kubectl get pods
   ```

## Security Considerations

- Change all default passwords and API keys
- Use strong JWT secrets in production
- Enable SSL/TLS for all services
- Implement network segmentation
- Regularly update dependencies
- Monitor service logs for suspicious activity

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 