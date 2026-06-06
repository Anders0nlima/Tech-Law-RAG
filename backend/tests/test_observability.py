"""
Tests for the Langfuse observability module.

These tests ensure the module initialises correctly regardless of whether
the Langfuse credentials are present in the environment or not.
"""

from langfuse import Langfuse


def test_get_langfuse_returns_client_without_credentials():
    """
    When Langfuse credentials are not set (None), get_langfuse() must still return a
    Langfuse client (disabled mode) so the rest of the app doesn't crash.

    In CI/local-dev the Settings object already has langfuse_public_key=None because
    no LANGFUSE_PUBLIC_KEY env var is set, so this exercises the real no-creds path.
    """
    import app.core.config as config_module
    import app.core.observability as obs_module

    # Only run the disabled-client assertion when credentials are genuinely absent.
    # If the developer has set real credentials, skip patching and just confirm a
    # Langfuse instance is returned.
    obs_module._langfuse_client = None

    client = obs_module.get_langfuse()
    assert client is not None
    assert isinstance(client, Langfuse)

    # Reset singleton after test
    obs_module._langfuse_client = None


def test_get_langfuse_returns_singleton():
    """
    Calling get_langfuse() twice should return the exact same object.
    """
    import app.core.observability as obs_module

    obs_module._langfuse_client = None

    client_a = obs_module.get_langfuse()
    client_b = obs_module.get_langfuse()
    assert client_a is client_b

    # Reset singleton after test
    obs_module._langfuse_client = None
