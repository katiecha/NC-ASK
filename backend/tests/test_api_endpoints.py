"""
Tests for API endpoints using FastAPI TestClient.
"""
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_client():
    """Create FastAPI test client."""
    # Import here to ensure fresh app instance for each test
    import api.routes
    # Reset the global RAG pipeline before each test
    api.routes._rag_pipeline = None

    from main import app
    return TestClient(app)


@pytest.fixture
def mock_rag_pipeline():
    """Create a mock RAG pipeline for testing."""
    mock_pipeline = Mock()
    mock_pipeline.process_query = AsyncMock()
    return mock_pipeline


class TestQueryEndpoint:
    """Tests for /api/query endpoint."""

    def test_query_endpoint_structure(self, test_client):
        """Test query endpoint returns expected response structure."""
        # Note: This test uses the real RAG pipeline which requires proper setup
        # In a CI environment, you'd want to mock the dependencies
        response = test_client.post(
            "/api/query",
            json={
                "query": "What is autism?",
                "session_id": "test-session-123",
                "view_type": "patient"
            }
        )

        # Verify response structure
        assert response.status_code == 200
        data = response.json()

        # Check all required fields are present
        assert "response" in data
        assert "citations" in data
        assert "crisis_detected" in data
        assert "crisis_severity" in data
        assert "crisis_resources" in data

        # Check types
        assert isinstance(data["response"], str)
        assert isinstance(data["citations"], list)
        assert isinstance(data["crisis_detected"], bool)
        assert isinstance(data["crisis_resources"], list)

    def test_query_endpoint_with_provider_view(self, test_client):
        """Test query endpoint accepts provider view type."""
        response = test_client.post(
            "/api/query",
            json={
                "query": "What is an IEP?",
                "view_type": "provider"
            }
        )

        # Should accept provider view type and return successful response
        assert response.status_code == 200
        data = response.json()
        assert "response" in data

    def test_query_endpoint_empty_query(self, test_client):
        """Test query endpoint with empty query."""
        response = test_client.post(
            "/api/query",
            json={
                "query": "",
                "view_type": "patient"
            }
        )

        # Should return validation error
        assert response.status_code == 422

    def test_query_endpoint_whitespace_only(self, test_client):
        """Test query endpoint with whitespace-only query."""
        response = test_client.post(
            "/api/query",
            json={
                "query": "   ",
                "view_type": "patient"
            }
        )

        # Should return validation error
        assert response.status_code == 422

    def test_query_endpoint_missing_query(self, test_client):
        """Test query endpoint without query field."""
        response = test_client.post(
            "/api/query",
            json={
                "view_type": "patient"
            }
        )

        # Should return validation error
        assert response.status_code == 422

    def test_query_endpoint_invalid_view_type(self, test_client):
        """Test query endpoint with invalid view type."""
        response = test_client.post(
            "/api/query",
            json={
                "query": "What is autism?",
                "view_type": "invalid_type"
            }
        )

        # Should return validation error
        assert response.status_code == 422

    def test_query_endpoint_accepts_session_id(self, test_client):
        """Test query endpoint accepts and handles session_id."""
        response = test_client.post(
            "/api/query",
            json={
                "query": "Test query",
                "session_id": "custom-session-id-123",
                "view_type": "patient"
            }
        )

        # Should accept session ID and return successful response
        assert response.status_code == 200
        data = response.json()
        assert "response" in data


class TestCrisisResourcesEndpoint:
    """Tests for /api/crisis-resources endpoint."""

    def test_crisis_resources_endpoint_success(self, test_client):
        """Test successful retrieval of crisis resources."""
        response = test_client.get("/api/crisis-resources")

        assert response.status_code == 200
        data = response.json()
        assert "resources" in data
        assert isinstance(data["resources"], list)

        # Check that resources have expected structure
        if len(data["resources"]) > 0:
            resource = data["resources"][0]
            assert "name" in resource
            assert "phone" in resource
            assert "description" in resource

    def test_crisis_resources_contains_988(self, test_client):
        """Test that crisis resources include the 988 lifeline."""
        response = test_client.get("/api/crisis-resources")

        assert response.status_code == 200
        data = response.json()

        # Verify 988 lifeline is in the resources
        phone_numbers = [r["phone"] for r in data["resources"]]
        assert "988" in phone_numbers

    def test_crisis_resources_error_handling(self, test_client):
        """Test crisis resources endpoint error handling."""
        # Mock the service factory to raise an exception
        with patch('api.routes.get_service_factory') as mock_factory:
            mock_factory.side_effect = Exception("Service factory error")

            response = test_client.get("/api/crisis-resources")

        # Should return 500 error
        assert response.status_code == 500
        assert "detail" in response.json()


class TestHealthEndpoint:
    """Tests for /api/health endpoint."""

    def test_health_endpoint(self, test_client):
        """Test health check endpoint."""
        response = test_client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "NC-ASK" in data["service"]

    def test_root_health_endpoint(self, test_client):
        """Test root health check endpoint."""
        response = test_client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_endpoint(self, test_client):
        """Test root endpoint returns basic info."""
        response = test_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"
