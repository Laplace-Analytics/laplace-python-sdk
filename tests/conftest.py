"""Test configuration and fixtures."""

import os
import pytest
from unittest.mock import Mock, patch
from laplace import LaplaceClient


@pytest.fixture
def mock_api_key():
    """Mock API key for testing."""
    return "test-api-key-123"


@pytest.fixture
def integration_client():
    """Real client for integration tests (requires API key)."""
    api_key = os.getenv("LAPLACE_API_KEY")
    if not api_key:
        pytest.skip("LAPLACE_API_KEY environment variable not set")
    return LaplaceClient(api_key=api_key)


class MockResponse:
    """Mock response class for testing."""
    
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
        self.reason_phrase = "OK"
    
    def json(self):
        return self.json_data
    
    def raise_for_status(self):
        if self.status_code >= 400:
            from httpx import HTTPStatusError
            raise HTTPStatusError("Error", request=Mock(), response=self)