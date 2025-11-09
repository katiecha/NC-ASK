import types

import pytest


def test_supabase_client_singleton_and_admin(monkeypatch):
    """Mock supabase.create_client to test singleton and admin creation."""
    # Import after conftest has set environment variables
    import services.supabase_client as sc
    from services.supabase_client import SupabaseClient

    # Reset any existing singleton for a clean test
    SupabaseClient._instance = None

    called = {}

    def fake_create_client(url, key):
        # Return a simple object that records url/key
        obj = types.SimpleNamespace(url=url, key=key)
        called['last'] = (url, key)
        return obj

    monkeypatch.setattr(sc, 'create_client', fake_create_client)

    # Call get_client and verify singleton behavior
    client1 = SupabaseClient.get_client()
    assert client1.url == sc.settings.SUPABASE_URL
    assert client1.key == sc.settings.SUPABASE_ANON_KEY

    # Subsequent get_client should return same instance
    client2 = SupabaseClient.get_client()
    assert client1 is client2

    # get_admin_client should call create_client with service role key and return a new object
    admin = SupabaseClient.get_admin_client()
    assert admin.key == sc.settings.SUPABASE_SERVICE_ROLE_KEY


def test_get_supabase_convenience(monkeypatch):
    """Test the convenience function get_supabase returns client instance."""
    # Import after conftest has set environment variables
    import services.supabase_client as sc
    from services.supabase_client import SupabaseClient, get_supabase

    # Reset singleton
    SupabaseClient._instance = None

    # Create a fake client and ensure get_supabase returns it
    fake = object()

    def fake_create_client(url, key):
        return fake

    monkeypatch.setattr(sc, 'create_client', fake_create_client)

    client = get_supabase()
    assert client is fake
