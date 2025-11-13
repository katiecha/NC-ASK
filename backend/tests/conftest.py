"""
Pytest configuration for NC-ASK tests.
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add backend directory to Python path so imports work
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Mock heavy ML libraries before they get imported
sys.modules['sentence_transformers'] = MagicMock()
sys.modules['tensorflow'] = MagicMock()
sys.modules['torch'] = MagicMock()


@pytest.fixture(autouse=True, scope="session")
def setup_test_environment():
    """
    Set up test environment variables at session start.
    This runs before any imports happen.
    """
    import os
    os.environ["SUPABASE_URL"] = "https://test-project.supabase.co"
    os.environ["SUPABASE_ANON_KEY"] = "test-anon-key-12345"
    os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "test-service-key-12345"
    os.environ["GOOGLE_API_KEY"] = "test-google-api-key-12345"
    os.environ["OPENAI_API_KEY"] = "test-openai-api-key-12345"
    os.environ["ENVIRONMENT"] = "test"


@pytest.fixture(autouse=True)
def mock_environment_variables(monkeypatch):
    """
    Set mock environment variables for all tests.
    This prevents tests from trying to connect to real services.
    """
    # Set fake but valid-looking credentials to prevent real API calls
    monkeypatch.setenv("SUPABASE_URL", "https://test-project.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "test-anon-key-12345")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test-service-key-12345")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-google-api-key-12345")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-api-key-12345")
    monkeypatch.setenv("ENVIRONMENT", "test")


@pytest.fixture(autouse=True)
def mock_supabase_client():
    """Mock Supabase client creation to prevent real connections."""
    with patch("services.supabase_client.create_client") as mock_create:
        # Create a mock Supabase client
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.execute.return_value.data = []
        mock_create.return_value = mock_client

        # Reset the singleton before each test
        from services.supabase_client import SupabaseClient
        SupabaseClient._instance = None

        yield mock_client


@pytest.fixture(autouse=True)
def mock_gemini():
    """Mock Google Gemini API to prevent real API calls."""
    with patch("google.generativeai.configure") as mock_configure:
        with patch("google.generativeai.GenerativeModel") as mock_model_class:
            # Mock the model instance
            mock_model = MagicMock()
            mock_response = Mock()
            mock_response.text = "This is a test response from the AI assistant."
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            yield mock_model


@pytest.fixture
def test_service_factory():
    """
    Fixture providing a ServiceFactory configured for testing.
    Uses in-memory vector store to avoid database calls.
    """
    from services.service_factory import create_test_factory

    return create_test_factory(use_in_memory_store=True)
