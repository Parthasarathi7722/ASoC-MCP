import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import json
import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, get_connector, DataSourceConfig, DataQuery

client = TestClient(app)

# Mock data
MOCK_ELASTICSEARCH_CONFIG = {
    "name": "Test Elasticsearch",
    "type": "elasticsearch",
    "enabled": True,
    "config": {
        "hosts": ["http://elasticsearch:9200"],
        "username": "elastic",
        "password": "changeme",
        "verify_certs": False,
        "timeout": 30
    },
    "description": "Test Elasticsearch instance",
    "tags": ["test", "elasticsearch"]
}

MOCK_MONGODB_CONFIG = {
    "name": "Test MongoDB",
    "type": "mongodb",
    "enabled": True,
    "config": {
        "uri": "mongodb://mongodb:27017",
        "database": "security_data",
        "username": "admin",
        "password": "changeme",
        "auth_source": "admin"
    },
    "description": "Test MongoDB instance",
    "tags": ["test", "mongodb"]
}

MOCK_QUERY = {
    "source_id": "test-source-id",
    "query_type": "search",
    "parameters": {
        "index": "security-events",
        "query": {
            "query_string": {
                "query": "severity:high"
            }
        }
    },
    "limit": 10,
    "timeout": 30
}

# Mock token for authentication
MOCK_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXIiLCJleHAiOjE3MTk5OTk5OTl9.1234567890"

# Mock headers for authenticated requests
MOCK_HEADERS = {"Authorization": f"Bearer {MOCK_TOKEN}"}

# Mock Redis client
class MockRedis:
    def __init__(self):
        self.data = {}
    
    def set(self, key, value, ex=None):
        self.data[key] = value
    
    def get(self, key):
        return self.data.get(key)
    
    def delete(self, key):
        if key in self.data:
            del self.data[key]
            return 1
        return 0

# Mock connector classes
class MockElasticsearchConnector:
    def __init__(self, config):
        self.config = config
        self.client = None
        self.connected = False
        self.last_sync = None
        self.error = None
        self.metrics = {}
    
    async def connect(self):
        self.connected = True
        self.last_sync = datetime.now().isoformat()
        return True
    
    async def disconnect(self):
        self.connected = False
        return True
    
    async def test_connection(self):
        return True
    
    async def query(self, query_type, parameters, limit=100, timeout=30):
        return [
            {"id": "1", "severity": "high", "source": "test"},
            {"id": "2", "severity": "high", "source": "test"}
        ]
    
    async def get_metrics(self):
        return {
            "cluster_name": "test-cluster",
            "node_count": 1,
            "document_count": 100,
            "storage_size": 1024
        }

class MockMongoDBConnector:
    def __init__(self, config):
        self.config = config
        self.client = None
        self.connected = False
        self.last_sync = None
        self.error = None
        self.metrics = {}
    
    async def connect(self):
        self.connected = True
        self.last_sync = datetime.now().isoformat()
        return True
    
    async def disconnect(self):
        self.connected = False
        return True
    
    async def test_connection(self):
        return True
    
    async def query(self, query_type, parameters, limit=100, timeout=30):
        return [
            {"_id": "1", "severity": "high", "source": "test"},
            {"_id": "2", "severity": "high", "source": "test"}
        ]
    
    async def get_metrics(self):
        return {
            "connections": {"current": 1},
            "opcounters": {"insert": 10, "query": 20},
            "mem": {"resident": 1024}
        }

# Tests
@pytest.fixture
def mock_redis():
    with patch("app.redis_client", MockRedis()):
        yield

@pytest.fixture
def mock_connectors():
    with patch("app.get_connector") as mock_get_connector:
        mock_get_connector.side_effect = lambda source_type, config: {
            "elasticsearch": MockElasticsearchConnector(config),
            "mongodb": MockMongoDBConnector(config)
        }.get(source_type)
        yield mock_get_connector

@pytest.fixture
def mock_auth():
    with patch("app.get_current_user", return_value="test-user"):
        yield

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_data_source_elasticsearch(mock_redis, mock_connectors, mock_auth):
    response = client.post(
        "/sources",
        json=MOCK_ELASTICSEARCH_CONFIG,
        headers=MOCK_HEADERS
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == MOCK_ELASTICSEARCH_CONFIG["name"]
    assert data["type"] == MOCK_ELASTICSEARCH_CONFIG["type"]
    assert data["status"] == "connected"
    assert "source_id" in data
    assert "metrics" in data

def test_create_data_source_mongodb(mock_redis, mock_connectors, mock_auth):
    response = client.post(
        "/sources",
        json=MOCK_MONGODB_CONFIG,
        headers=MOCK_HEADERS
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == MOCK_MONGODB_CONFIG["name"]
    assert data["type"] == MOCK_MONGODB_CONFIG["type"]
    assert data["status"] == "connected"
    assert "source_id" in data
    assert "metrics" in data

def test_list_data_sources(mock_redis, mock_connectors, mock_auth):
    # First create a data source
    client.post(
        "/sources",
        json=MOCK_ELASTICSEARCH_CONFIG,
        headers=MOCK_HEADERS
    )
    
    # Then list all data sources
    response = client.get("/sources", headers=MOCK_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == MOCK_ELASTICSEARCH_CONFIG["name"]
    assert data[0]["type"] == MOCK_ELASTICSEARCH_CONFIG["type"]

def test_get_data_source(mock_redis, mock_connectors, mock_auth):
    # First create a data source
    create_response = client.post(
        "/sources",
        json=MOCK_ELASTICSEARCH_CONFIG,
        headers=MOCK_HEADERS
    )
    source_id = create_response.json()["source_id"]
    
    # Then get the data source
    response = client.get(f"/sources/{source_id}", headers=MOCK_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["source_id"] == source_id
    assert data["name"] == MOCK_ELASTICSEARCH_CONFIG["name"]
    assert data["type"] == MOCK_ELASTICSEARCH_CONFIG["type"]

def test_delete_data_source(mock_redis, mock_connectors, mock_auth):
    # First create a data source
    create_response = client.post(
        "/sources",
        json=MOCK_ELASTICSEARCH_CONFIG,
        headers=MOCK_HEADERS
    )
    source_id = create_response.json()["source_id"]
    
    # Then delete the data source
    response = client.delete(f"/sources/{source_id}", headers=MOCK_HEADERS)
    assert response.status_code == 200
    assert response.json() == {"message": "Data source deleted successfully"}
    
    # Verify it's deleted
    get_response = client.get(f"/sources/{source_id}", headers=MOCK_HEADERS)
    assert get_response.status_code == 404

def test_query_data_source(mock_redis, mock_connectors, mock_auth):
    # First create a data source
    create_response = client.post(
        "/sources",
        json=MOCK_ELASTICSEARCH_CONFIG,
        headers=MOCK_HEADERS
    )
    source_id = create_response.json()["source_id"]
    
    # Then query the data source
    query = MOCK_QUERY.copy()
    query["source_id"] = source_id
    
    response = client.post(
        f"/sources/{source_id}/query",
        json=query,
        headers=MOCK_HEADERS
    )
    assert response.status_code == 200
    data = response.json()
    assert data["source_id"] == source_id
    assert data["status"] == "completed"
    assert "results" in data
    assert len(data["results"]) == 2
    assert "query_id" in data

def test_get_query_result(mock_redis, mock_connectors, mock_auth):
    # First create a data source and execute a query
    create_response = client.post(
        "/sources",
        json=MOCK_ELASTICSEARCH_CONFIG,
        headers=MOCK_HEADERS
    )
    source_id = create_response.json()["source_id"]
    
    query = MOCK_QUERY.copy()
    query["source_id"] = source_id
    
    query_response = client.post(
        f"/sources/{source_id}/query",
        json=query,
        headers=MOCK_HEADERS
    )
    query_id = query_response.json()["query_id"]
    
    # Then get the query result
    response = client.get(f"/queries/{query_id}", headers=MOCK_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["query_id"] == query_id
    assert data["source_id"] == source_id
    assert data["status"] == "completed"
    assert "results" in data
    assert len(data["results"]) == 2

def test_unauthorized_access():
    # Try to access an endpoint without authentication
    response = client.get("/sources")
    assert response.status_code == 401 