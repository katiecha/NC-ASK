"""
Pytest configuration for NC-ASK tests.
"""
import sys
from pathlib import Path

import pytest

# Add backend directory to Python path so imports work
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


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
    monkeypatch.setenv("ENVIRONMENT", "test")


@pytest.fixture
def test_service_factory():
    """
    Fixture providing a ServiceFactory configured for testing.
    Uses in-memory vector store to avoid database calls.
    """
    from services.service_factory import create_test_factory

    return create_test_factory(use_in_memory_store=True)
