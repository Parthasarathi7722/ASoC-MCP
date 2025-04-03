import pytest
import os
import sys
from unittest.mock import patch

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment variables for testing
os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6379"
os.environ["JWT_SECRET"] = "test_secret_key"
os.environ["JWT_ALGORITHM"] = "HS256"

# Mock Redis client for all tests
@pytest.fixture(autouse=True)
def mock_redis():
    with patch("app.redis_client") as mock:
        yield mock

# Mock authentication for all tests
@pytest.fixture(autouse=True)
def mock_auth():
    with patch("app.get_current_user", return_value="test-user"):
        yield 