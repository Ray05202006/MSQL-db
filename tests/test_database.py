"""TDD tests for the Database class using mocked MySQL connections."""

from unittest.mock import MagicMock, patch, PropertyMock
import pytest

from db.database import Database


@pytest.fixture
def db():
    return Database(
        host="localhost",
        user="root",
        password="password",
        database="test_db",
    )


@pytest.fixture
def mock_connection():
    conn = MagicMock()
    conn.is_connected.return_value = True
    return conn


class TestConnect:
    def test_connect_returns_connection(self, db):
        with patch("db.database.mysql.connector.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            result = db.connect()
            assert result is mock_conn
            mock_connect.assert_called_once_with(
                host="localhost",
                user="root",
                password="password",
                database="test_db",
            )

    def test_connect_stores_connection(self, db):
        with patch("db.database.mysql.connector.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            db.connect()
            assert db.connection is mock_conn


class TestDisconnect:
    def test_disconnect_closes_open_connection(self, db, mock_connection):
        db.connection = mock_connection
        db.disconnect()
        mock_connection.close.assert_called_once()
        assert db.connection is None

    def test_disconnect_does_nothing_when_not_connected(self, db, mock_connection):
        mock_connection.is_connected.return_value = False
        db.connection = mock_connection
        db.disconnect()
        mock_connection.close.assert_not_called()

    def test_disconnect_does_nothing_when_no_connection(self, db):
        db.connection = None
        db.disconnect()  # should not raise


class TestCreateTable:
    def test_create_table_executes_correct_sql(self, db, mock_connection):
        db.connection = mock_connection
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor

        db.create_table()

        sql = mock_cursor.execute.call_args[0][0]
        assert "CREATE TABLE IF NOT EXISTS users" in sql
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()


class TestInsertUser:
    def test_insert_user_returns_lastrowid(self, db, mock_connection):
        db.connection = mock_connection
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 42
        mock_connection.cursor.return_value = mock_cursor

        result = db.insert_user("Alice", "alice@example.com")

        assert result == 42
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            ("Alice", "alice@example.com"),
        )
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()


class TestGetUser:
    def test_get_user_returns_dict(self, db, mock_connection):
        db.connection = mock_connection
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"id": 1, "name": "Alice", "email": "alice@example.com"}
        mock_connection.cursor.return_value = mock_cursor

        result = db.get_user(1)

        assert result == {"id": 1, "name": "Alice", "email": "alice@example.com"}
        mock_cursor.execute.assert_called_once_with(
            "SELECT id, name, email FROM users WHERE id = %s", (1,)
        )
        mock_cursor.close.assert_called_once()

    def test_get_user_returns_none_when_not_found(self, db, mock_connection):
        db.connection = mock_connection
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_connection.cursor.return_value = mock_cursor

        result = db.get_user(999)

        assert result is None


class TestGetAllUsers:
    def test_get_all_users_returns_list(self, db, mock_connection):
        db.connection = mock_connection
        mock_cursor = MagicMock()
        users = [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
        ]
        mock_cursor.fetchall.return_value = users
        mock_connection.cursor.return_value = mock_cursor

        result = db.get_all_users()

        assert result == users
        mock_cursor.execute.assert_called_once_with("SELECT id, name, email FROM users")
        mock_cursor.close.assert_called_once()

    def test_get_all_users_returns_empty_list(self, db, mock_connection):
        db.connection = mock_connection
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_connection.cursor.return_value = mock_cursor

        assert db.get_all_users() == []


class TestUpdateUser:
    def test_update_user_returns_rowcount(self, db, mock_connection):
        db.connection = mock_connection
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_connection.cursor.return_value = mock_cursor

        result = db.update_user(1, "Alice Smith", "alice.smith@example.com")

        assert result == 1
        mock_cursor.execute.assert_called_once_with(
            "UPDATE users SET name = %s, email = %s WHERE id = %s",
            ("Alice Smith", "alice.smith@example.com", 1),
        )
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()

    def test_update_user_returns_zero_when_not_found(self, db, mock_connection):
        db.connection = mock_connection
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 0
        mock_connection.cursor.return_value = mock_cursor

        result = db.update_user(999, "Ghost", "ghost@example.com")

        assert result == 0


class TestDeleteUser:
    def test_delete_user_returns_rowcount(self, db, mock_connection):
        db.connection = mock_connection
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_connection.cursor.return_value = mock_cursor

        result = db.delete_user(1)

        assert result == 1
        mock_cursor.execute.assert_called_once_with(
            "DELETE FROM users WHERE id = %s", (1,)
        )
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()

    def test_delete_user_returns_zero_when_not_found(self, db, mock_connection):
        db.connection = mock_connection
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 0
        mock_connection.cursor.return_value = mock_cursor

        result = db.delete_user(999)

        assert result == 0
