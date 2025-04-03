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
   - Create `.env` files for each service as described in the [Environment Configuration](#environment-configuration) section
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

## Environment Configuration

The MCP Platform uses environment variables for configuration. Below are examples of `.env` files for each service.

### Root .env File (for Docker Compose)

Create a `.env` file in the root directory for Docker Compose:

```
# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# JWT Configuration
JWT_SECRET=your-secure-secret-key-change-in-production
JWT_ALGORITHM=HS256

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password

# Slack Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Anthropic Configuration
ANTHROPIC_API_KEY=your-anthropic-api-key

# Data Source Credentials
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=changeme
MONGODB_USERNAME=admin
MONGODB_PASSWORD=changeme
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changeme
MYSQL_USER=root
MYSQL_PASSWORD=changeme
SPLUNK_USERNAME=admin
SPLUNK_PASSWORD=changeme
TENABLE_API_KEY=your-tenable-api-key
RAPID7_API_KEY=your-rapid7-api-key
VIRUSTOTAL_API_KEY=your-virustotal-api-key
ALIENVAULT_OTX_API_KEY=your-alienvault-otx-api-key
SHODAN_API_KEY=your-shodan-api-key
```

### Authentication Service (.env)

Create a `.env` file in the `auth_service` directory:

```
# Redis Configuration
MEMORY_URL=redis://redis:6379

# JWT Configuration
SECRET_KEY=your-secure-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Service Configuration
SERVICE_PORT=8000
SERVICE_HOST=0.0.0.0
```

### Notifications Service (.env)

Create a `.env` file in the `notifications` directory:

```
# Redis Configuration
MEMORY_URL=redis://redis:6379

# JWT Configuration
SECRET_KEY=your-secure-secret-key-change-in-production
JWT_ALGORITHM=HS256

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
EMAIL_FROM=notifications@example.com

# Slack Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# Service Configuration
SERVICE_PORT=8000
SERVICE_HOST=0.0.0.0
```

### Data Connectors Service (.env)

Create a `.env` file in the `data_connectors` directory:

```
# Redis Configuration
MEMORY_URL=redis://redis:6379

# JWT Configuration
SECRET_KEY=your-secure-secret-key-change-in-production
JWT_ALGORITHM=HS256

# Elasticsearch Configuration
ELASTICSEARCH_HOST=http://elasticsearch:9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=changeme

# MongoDB Configuration
MONGODB_URI=mongodb://mongodb:27017
MONGODB_USERNAME=admin
MONGODB_PASSWORD=changeme
MONGODB_AUTH_SOURCE=admin

# PostgreSQL Configuration
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=security_data
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changeme

# MySQL Configuration
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_DATABASE=security_data
MYSQL_USER=root
MYSQL_PASSWORD=changeme

# Splunk Configuration
SPLUNK_HOST=splunk
SPLUNK_PORT=8089
SPLUNK_USERNAME=admin
SPLUNK_PASSWORD=changeme

# Tenable.io Configuration
TENABLE_API_KEY=your-tenable-api-key

# Rapid7 Configuration
RAPID7_API_KEY=your-rapid7-api-key

# Service Configuration
SERVICE_PORT=8000
SERVICE_HOST=0.0.0.0
```

### Agent Manager Service (.env)

Create a `.env` file in the `agent_manager` directory:

```
# Redis Configuration
MEMORY_URL=redis://redis:6379

# JWT Configuration
SECRET_KEY=your-secure-secret-key-change-in-production
JWT_ALGORITHM=HS256

# Service URLs
AUTH_SERVICE_URL=http://auth-service:8000
NOTIFICATIONS_SERVICE_URL=http://notifications-service:8000
DATA_CONNECTORS_SERVICE_URL=http://data-connectors-service:8000
LLM_ORCHESTRATOR_URL=http://llm-orchestrator:8000
TRIAGE_AGENT_URL=http://triage-agent:8000
INVESTIGATION_AGENT_URL=http://investigation-agent:8000
THREAT_INTEL_AGENT_URL=http://threat-intel-agent:8000
REMEDIATION_AGENT_URL=http://remediation-agent:8000

# Service Configuration
SERVICE_PORT=8000
SERVICE_HOST=0.0.0.0
```

### LLM Orchestrator Service (.env)

Create a `.env` file in the `llm_orchestrator` directory:

```
# Redis Configuration
MEMORY_URL=redis://redis:6379

# JWT Configuration
SECRET_KEY=your-secure-secret-key-change-in-production
JWT_ALGORITHM=HS256

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Anthropic Configuration (if used)
ANTHROPIC_API_KEY=your-anthropic-api-key

# Service Configuration
SERVICE_PORT=8000
SERVICE_HOST=0.0.0.0
```

### Triage Agent (.env)

Create a `.env` file in the `agents/triage_agent` directory:

```
# Redis Configuration
MEMORY_URL=redis://redis:6379

# JWT Configuration
SECRET_KEY=your-secure-secret-key-change-in-production
JWT_ALGORITHM=HS256

# LLM Orchestrator Configuration
LLM_ORCHESTRATOR_URL=http://llm-orchestrator:8000

# Service Configuration
SERVICE_PORT=8000
SERVICE_HOST=0.0.0.0
```

### Investigation Agent (.env)

Create a `.env` file in the `agents/investigation_agent` directory:

```
# Redis Configuration
MEMORY_URL=redis://redis:6379

# JWT Configuration
SECRET_KEY=your-secure-secret-key-change-in-production
JWT_ALGORITHM=HS256

# LLM Orchestrator Configuration
LLM_ORCHESTRATOR_URL=http://llm-orchestrator:8000

# Data Connectors Configuration
DATA_CONNECTORS_URL=http://data-connectors-service:8000

# Service Configuration
SERVICE_PORT=8000
SERVICE_HOST=0.0.0.0
```

### Threat Intel Agent (.env)

Create a `.env` file in the `agents/threat_intel_agent` directory:

```
# Redis Configuration
MEMORY_URL=redis://redis:6379

# JWT Configuration
SECRET_KEY=your-secure-secret-key-change-in-production
JWT_ALGORITHM=HS256

# LLM Orchestrator Configuration
LLM_ORCHESTRATOR_URL=http://llm-orchestrator:8000

# Data Connectors Configuration
DATA_CONNECTORS_URL=http://data-connectors-service:8000

# Threat Intel API Keys
VIRUSTOTAL_API_KEY=your-virustotal-api-key
ALIENVAULT_OTX_API_KEY=your-alienvault-otx-api-key
SHODAN_API_KEY=your-shodan-api-key

# Service Configuration
SERVICE_PORT=8000
SERVICE_HOST=0.0.0.0
```

### Remediation Agent (.env)

Create a `.env` file in the `agents/remediation_agent` directory:

```
# Redis Configuration
MEMORY_URL=redis://redis:6379

# JWT Configuration
SECRET_KEY=your-secure-secret-key-change-in-production
JWT_ALGORITHM=HS256

# LLM Orchestrator Configuration
LLM_ORCHESTRATOR_URL=http://llm-orchestrator:8000

# Data Connectors Configuration
DATA_CONNECTORS_URL=http://data-connectors-service:8000

# Notifications Configuration
NOTIFICATIONS_URL=http://notifications-service:8000

# Service Configuration
SERVICE_PORT=8000
SERVICE_HOST=0.0.0.0
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