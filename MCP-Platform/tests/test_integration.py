import unittest
import requests
import json
import os
from datetime import datetime

class TestParthasarathi7722MCPPlatformIntegration(unittest.TestCase):
    def setUp(self):
        self.base_url = os.getenv('MCP_PLATFORM_URL', 'http://localhost:8000')
        self.api_key = os.getenv('MCP_API_KEY', 'test-key')
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

    def test_health_check(self):
        response = requests.get(f'{self.base_url}/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'healthy')

    def test_authentication(self):
        # Test login
        login_data = {
            'username': 'admin',
            'password': 'admin'
        }
        response = requests.post(f'{self.base_url}/api/v1/auth/login', json=login_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json())
        token = response.json()['access_token']

        # Test protected endpoint
        headers = {**self.headers, 'Authorization': f'Bearer {token}'}
        response = requests.get(f'{self.base_url}/api/v1/users/me', headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_data_connectors(self):
        # Test creating a data connector
        connector_data = {
            'name': 'test-connector',
            'type': 'wazuh',
            'config': {
                'api_url': 'https://wazuh-manager:55000',
                'username': 'admin',
                'password': 'admin'
            }
        }
        response = requests.post(
            f'{self.base_url}/api/v1/connectors',
            headers=self.headers,
            json=connector_data
        )
        self.assertEqual(response.status_code, 201)
        connector_id = response.json()['id']

        # Test getting connector status
        response = requests.get(
            f'{self.base_url}/api/v1/connectors/{connector_id}/status',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)

        # Test deleting connector
        response = requests.delete(
            f'{self.base_url}/api/v1/connectors/{connector_id}',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 204)

    def test_incident_management(self):
        # Test creating an incident
        incident_data = {
            'title': 'Test Incident',
            'description': 'This is a test incident',
            'severity': 'high',
            'status': 'open'
        }
        response = requests.post(
            f'{self.base_url}/api/v1/incidents',
            headers=self.headers,
            json=incident_data
        )
        self.assertEqual(response.status_code, 201)
        incident_id = response.json()['id']

        # Test updating incident
        update_data = {
            'status': 'in_progress',
            'description': 'Updated description'
        }
        response = requests.patch(
            f'{self.base_url}/api/v1/incidents/{incident_id}',
            headers=self.headers,
            json=update_data
        )
        self.assertEqual(response.status_code, 200)

        # Test getting incident
        response = requests.get(
            f'{self.base_url}/api/v1/incidents/{incident_id}',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'in_progress')

        # Test deleting incident
        response = requests.delete(
            f'{self.base_url}/api/v1/incidents/{incident_id}',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 204)

    def test_agent_management(self):
        # Test registering an agent
        agent_data = {
            'name': 'test-agent',
            'type': 'wazuh',
            'config': {
                'group': 'test-group',
                'os': 'linux'
            }
        }
        response = requests.post(
            f'{self.base_url}/api/v1/agents',
            headers=self.headers,
            json=agent_data
        )
        self.assertEqual(response.status_code, 201)
        agent_id = response.json()['id']

        # Test getting agent status
        response = requests.get(
            f'{self.base_url}/api/v1/agents/{agent_id}/status',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)

        # Test updating agent
        update_data = {
            'config': {
                'group': 'updated-group',
                'os': 'linux'
            }
        }
        response = requests.patch(
            f'{self.base_url}/api/v1/agents/{agent_id}',
            headers=self.headers,
            json=update_data
        )
        self.assertEqual(response.status_code, 200)

        # Test deleting agent
        response = requests.delete(
            f'{self.base_url}/api/v1/agents/{agent_id}',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 204)

if __name__ == '__main__':
    unittest.main() 