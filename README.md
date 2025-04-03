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

### Usage

1. Access the API documentation at `http://localhost:8000/docs`
2. Obtain an authentication token from `http://localhost:8001/token`
3. Use the token to interact with the MCP Platform APIs

## Development

### Adding New Connectors

1. Create a new connector in the `connectors/` directory
2. Implement the required interface
3. Add configuration to `docker-compose.yml`

### Modifying Playbooks

1. Update the Agent Manager's playbook definitions
2. Test the changes using the provided test endpoints

## License

This project is licensed under the MIT License - see the LICENSE file for details. 