import os
import importlib
import pytest
from unittest.mock import patch, MagicMock


# -------------------------------------------------
# Test 1: Environment variables exist
# -------------------------------------------------

def test_env_variables_exist():
    assert os.getenv("SUPABASE_URL") is not None
    assert os.getenv("SUPABASE_KEY") is not None


# -------------------------------------------------
# Test 2: Missing environment variables
# -------------------------------------------------

def test_missing_environment_variables():

    with patch.dict(os.environ, {}, clear=True):

        with pytest.raises(ValueError):
            import database.supabase_connection
            importlib.reload(database.supabase_connection)


# -------------------------------------------------
# Test 3: URL ending '/rest/v1/' is trimmed
# -------------------------------------------------

@patch("supabase.create_client")
def test_strip_rest_v1_slash(mock_create_client):

    mock_create_client.return_value = MagicMock()

    with patch.dict(os.environ, {
        "SUPABASE_URL": "https://demo.supabase.co/rest/v1/",
        "SUPABASE_KEY": "dummy-key"
    }):

        import database.supabase_connection
        importlib.reload(database.supabase_connection)

        assert database.supabase_connection.SUPABASE_URL == \
               "https://demo.supabase.co"


# -------------------------------------------------
# Test 4: URL ending '/rest/v1' is trimmed
# -------------------------------------------------

@patch("supabase.create_client")
def test_strip_rest_v1(mock_create_client):

    mock_create_client.return_value = MagicMock()

    with patch.dict(os.environ, {
        "SUPABASE_URL": "https://demo.supabase.co/rest/v1",
        "SUPABASE_KEY": "dummy-key"
    }):

        import database.supabase_connection
        importlib.reload(database.supabase_connection)

        assert database.supabase_connection.SUPABASE_URL == \
               "https://demo.supabase.co"


# -------------------------------------------------
# Test 5: URL without '/rest/v1' remains unchanged
# -------------------------------------------------

@patch("supabase.create_client")
def test_url_remains_same(mock_create_client):

    mock_create_client.return_value = MagicMock()

    with patch.dict(os.environ, {
        "SUPABASE_URL": "https://demo.supabase.co",
        "SUPABASE_KEY": "dummy-key"
    }):

        import database.supabase_connection
        importlib.reload(database.supabase_connection)

        assert database.supabase_connection.SUPABASE_URL == \
               "https://demo.supabase.co"


# -------------------------------------------------
# Test 6: create_client() called correctly
# -------------------------------------------------

@patch("supabase.create_client")
def test_create_client_called(mock_create_client):

    mock_client = MagicMock()

    mock_create_client.return_value = mock_client

    with patch.dict(os.environ, {
        "SUPABASE_URL": "https://demo.supabase.co",
        "SUPABASE_KEY": "dummy-key"
    }):

        import database.supabase_connection
        importlib.reload(database.supabase_connection)

        mock_create_client.assert_called_once_with(
            "https://demo.supabase.co",
            "dummy-key"
        )


# -------------------------------------------------
# Test 7: Supabase client object created
# -------------------------------------------------

@patch("supabase.create_client")
def test_supabase_client_created(mock_create_client):

    client = MagicMock()

    mock_create_client.return_value = client

    with patch.dict(os.environ, {
        "SUPABASE_URL": "https://demo.supabase.co",
        "SUPABASE_KEY": "dummy-key"
    }):

        import database.supabase_connection
        importlib.reload(database.supabase_connection)

        assert database.supabase_connection.supabase is not None


# -------------------------------------------------
# Test 8: Client has expected methods
# -------------------------------------------------

@patch("supabase.create_client")
def test_client_methods(mock_create_client):

    client = MagicMock()

    mock_create_client.return_value = client

    with patch.dict(os.environ, {
        "SUPABASE_URL": "https://demo.supabase.co",
        "SUPABASE_KEY": "dummy-key"
    }):

        import database.supabase_connection
        importlib.reload(database.supabase_connection)

        assert hasattr(database.supabase_connection.supabase, "table")