import sqlite3
from pathlib import Path
import pytest

from database.db_connection import (
    get_db_connection,
    DB_PATH,
)


# ---------------------------------------
# Test 1: Database file exists
# ---------------------------------------

def test_database_file_exists():
    assert DB_PATH.exists(), f"Database not found at {DB_PATH}"


# ---------------------------------------
# Test 2: Connection object is created
# ---------------------------------------

def test_get_db_connection_returns_connection():
    connection = get_db_connection()

    assert isinstance(connection, sqlite3.Connection)

    connection.close()


# ---------------------------------------
# Test 3: Connection is open
# ---------------------------------------

def test_connection_is_open():
    connection = get_db_connection()

    cursor = connection.cursor()
    cursor.execute("SELECT 1")

    result = cursor.fetchone()

    assert result[0] == 1

    connection.close()


# ---------------------------------------
# Test 4: Foreign key support enabled
# ---------------------------------------

def test_foreign_keys_enabled():

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute("PRAGMA foreign_keys")

    result = cursor.fetchone()[0]

    assert result == 1

    connection.close()


# ---------------------------------------
# Test 5: Row factory returns sqlite3.Row
# ---------------------------------------

def test_row_factory():

    connection = get_db_connection()

    assert connection.row_factory == sqlite3.Row

    connection.close()


# ---------------------------------------
# Test 6: Cursor can execute SQL
# ---------------------------------------

def test_cursor_executes_query():

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute("SELECT sqlite_version()")

    version = cursor.fetchone()[0]

    assert version is not None

    connection.close()


# ---------------------------------------
# Test 7: Multiple connections allowed
# ---------------------------------------

def test_multiple_connections():

    conn1 = get_db_connection()
    conn2 = get_db_connection()

    assert conn1 is not None
    assert conn2 is not None
    assert conn1 != conn2

    conn1.close()
    conn2.close()


# ---------------------------------------
# Test 8: Connection closes correctly
# ---------------------------------------

def test_connection_close():

    connection = get_db_connection()

    connection.close()

    with pytest.raises(sqlite3.ProgrammingError):
        connection.execute("SELECT 1")