# MCP Platform Deployment Guide

This guide provides detailed instructions for deploying the Model Context Protocol (MCP) Platform in various environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Deployment](#local-development-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Production Deployment Considerations](#production-deployment-considerations)
6. [Monitoring and Logging](#monitoring-and-logging)
7. [Backup and Recovery](#backup-and-recovery)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying the MCP Platform, ensure you have the following:

- Docker and Docker Compose (for containerized deployment)
- Kubernetes cluster (for Kubernetes deployment)
- Redis instance
- Python 3.11+ (for local development)
- API keys for external services (OpenAI, Anthropic, etc.)
- SMTP server for email notifications
- Slack webhook URL for Slack notifications

## Local Development Deployment

### Setting Up the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mcp-platform.git
   cd mcp-platform
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies for each service:
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

4. Start Redis:
   ```bash
   docker run -d -p 6379:6379 redis:7.2-alpine
   ```

5. Configure environment variables:
   - Create `.env` files in each service directory with the necessary environment variables
   - Example for auth_service/.env:
     ```
     REDIS_HOST=localhost
     REDIS_PORT=6379
     JWT_SECRET=your_development_secret_key
     JWT_ALGORITHM=HS256
     ```

6. Run the services:
   ```bash
   # Start each service in a separate terminal
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

7. Access the services:
   - Authentication Service: http://localhost:8001
   - Notifications Service: http://localhost:8002
   - Data Source Connectors Service: http://localhost:8003
   - Agent Manager Service: http://localhost:8004
   - LLM Orchestrator Service: http://localhost:8005

## Docker Deployment

### Single-Host Deployment

1. Configure the environment variables:
   - Edit the `docker-compose.yml` file to update environment variables
   - Create a `.env` file in the root directory with sensitive information:
     ```
     JWT_SECRET=your_production_secret_key
     OPENAI_API_KEY=your_openai_api_key
     ANTHROPIC_API_KEY=your_anthropic_api_key
     SMTP_PASSWORD=your_smtp_password
     SLACK_WEBHOOK_URL=your_slack_webhook_url
     ```

2. Build the Docker images:
   ```bash
   docker-compose build
   ```

3. Start the services:
   ```bash
   docker-compose up -d
   ```

4. Check the logs:
   ```bash
   docker-compose logs -f
   ```

5. Access the services:
   - Authentication Service: http://localhost:8001
   - Notifications Service: http://localhost:8002
   - Data Source Connectors Service: http://localhost:8003
   - Agent Manager Service: http://localhost:8004
   - LLM Orchestrator Service: http://localhost:8005

### Multi-Host Deployment

For deploying across multiple hosts:

1. Set up a Docker Swarm:
   ```bash
   # On the manager node
   docker swarm init
   
   # On worker nodes
   docker swarm join --token <token> <manager-ip>:2377
   ```

2. Deploy the stack:
   ```bash
   docker stack deploy -c docker-compose.yml mcp
   ```

3. Check the service status:
   ```bash
   docker service ls
   ```

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.20+)
- Helm (3.0+)
- kubectl configured to access your cluster

### Deploying with Helm

1. Add the Helm repository:
   ```bash
   helm repo add mcp https://your-helm-repo.com/mcp
   helm repo update
   ```

2. Create a values file (`values.yaml`):
   ```yaml
   global:
     redis:
       host: redis
       port: 6379
     jwt:
       secret: your_production_secret_key
       algorithm: HS256
   
   auth:
     enabled: true
     replicas: 2
   
   notifications:
     enabled: true
     replicas: 2
     smtp:
       host: smtp.example.com
       port: 587
       username: your_smtp_username
       password: your_smtp_password
     slack:
       webhookUrl: your_slack_webhook_url
   
   dataConnectors:
     enabled: true
     replicas: 2
   
   agentManager:
     enabled: true
     replicas: 2
   
   llmOrchestrator:
     enabled: true
     replicas: 2
     openai:
       apiKey: your_openai_api_key
     anthropic:
       apiKey: your_anthropic_api_key
   
   agents:
     triage:
       enabled: true
       replicas: 2
     investigation:
       enabled: true
       replicas: 2
     threatIntel:
       enabled: true
       replicas: 2
     remediation:
       enabled: true
       replicas: 2
   ```

3. Install the Helm chart:
   ```bash
   helm install mcp mcp/mcp-platform -f values.yaml
   ```

4. Check the deployment status:
   ```bash
   kubectl get pods
   ```

### Manual Kubernetes Deployment

1. Create namespaces:
   ```bash
   kubectl create namespace mcp
   ```

2. Apply the Kubernetes manifests:
   ```bash
   kubectl apply -f k8s/redis.yaml
   kubectl apply -f k8s/auth-service.yaml
   kubectl apply -f k8s/notifications-service.yaml
   kubectl apply -f k8s/data-connectors-service.yaml
   kubectl apply -f k8s/agent-manager.yaml
   kubectl apply -f k8s/llm-orchestrator.yaml
   kubectl apply -f k8s/agents/
   ```

3. Check the deployment status:
   ```bash
   kubectl get pods -n mcp
   ```

## Production Deployment Considerations

### Security

1. **Authentication and Authorization**:
   - Use strong JWT secrets
   - Implement role-based access control
   - Enable OAuth2 for external authentication

2. **Network Security**:
   - Use TLS for all service communications
   - Implement network segmentation
   - Use a reverse proxy (e.g., Nginx, Traefik) with SSL termination

3. **Data Security**:
   - Encrypt sensitive data at rest
   - Use secure connections for all data sources
   - Implement proper access controls for data sources

4. **API Security**:
   - Rate limiting
   - Input validation
   - CORS configuration
   - API key rotation

### High Availability

1. **Service Redundancy**:
   - Deploy multiple replicas of each service
   - Use load balancers for service distribution

2. **Data Redundancy**:
   - Use Redis Sentinel or Redis Cluster for high availability
   - Implement proper backup and recovery procedures

3. **Failover**:
   - Configure health checks for all services
   - Implement automatic failover mechanisms

### Performance

1. **Resource Allocation**:
   - Allocate appropriate CPU and memory resources
   - Monitor resource usage and adjust as needed

2. **Caching**:
   - Implement caching for frequently accessed data
   - Use Redis for caching

3. **Scaling**:
   - Implement horizontal scaling for all services
   - Use auto-scaling based on load

## Monitoring and Logging

### Monitoring

1. **Service Health**:
   - Implement health check endpoints for all services
   - Use a monitoring tool (e.g., Prometheus, Datadog) to track service health

2. **Performance Metrics**:
   - Collect performance metrics (response time, throughput, error rate)
   - Set up alerts for performance issues

3. **Resource Usage**:
   - Monitor CPU, memory, and network usage
   - Set up alerts for resource constraints

### Logging

1. **Centralized Logging**:
   - Use a centralized logging solution (e.g., ELK Stack, Graylog)
   - Configure all services to send logs to the centralized system

2. **Log Levels**:
   - Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)
   - Configure log rotation to manage log size

3. **Log Analysis**:
   - Set up log analysis for security events
   - Configure alerts for suspicious activity

## Backup and Recovery

### Backup

1. **Data Backup**:
   - Regularly backup Redis data
   - Backup configuration files and environment variables

2. **Configuration Backup**:
   - Document all configuration changes
   - Version control configuration files

### Recovery

1. **Service Recovery**:
   - Document recovery procedures for each service
   - Test recovery procedures regularly

2. **Data Recovery**:
   - Implement data recovery procedures
   - Test data recovery regularly

## Troubleshooting

### Common Issues

1. **Service Not Starting**:
   - Check logs for error messages
   - Verify environment variables
   - Check dependencies

2. **Authentication Issues**:
   - Verify JWT configuration
   - Check user credentials
   - Verify Redis connection

3. **Data Source Connection Issues**:
   - Verify data source credentials
   - Check network connectivity
   - Verify data source configuration

### Debugging

1. **Enable Debug Logging**:
   - Set log level to DEBUG
   - Check logs for detailed information

2. **Service Inspection**:
   - Use Docker inspect or kubectl describe to inspect service configuration
   - Check service health endpoints

3. **Network Troubleshooting**:
   - Use tools like curl, telnet, or netcat to test connectivity
   - Check firewall rules and network policies 