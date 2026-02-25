"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client."""
    from src.api.main import app
    return TestClient(app)


class TestHealthEndpoints:
    """Tests for health check endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "notebooklm-api"
    
    def test_liveness_check(self, client):
        """Test liveness check endpoint."""
        response = client.get("/live")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"


class TestRootEndpoint:
    """Tests for root endpoint."""
    
    def test_root(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data


# Note: Tests for notebook endpoints require authentication
# and should be run with a valid NotebookLM session.
# These are placeholder tests that can be expanded.
