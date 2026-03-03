"""Simple MySQL database module demonstrating basic CRUD operations."""

import mysql.connector
from mysql.connector import Error


class Database:
    """Manages a MySQL database connection and CRUD operations on a users table."""

    def __init__(self, host: str, user: str, password: str, database: str):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        """Open a connection to the MySQL database."""
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
        )
        return self.connection

    def disconnect(self):
        """Close the database connection if it is open."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None

    def create_table(self):
        """Create the users table if it does not already exist."""
        query = (
            "CREATE TABLE IF NOT EXISTS users ("
            "id INT AUTO_INCREMENT PRIMARY KEY, "
            "name VARCHAR(100) NOT NULL, "
            "email VARCHAR(150) NOT NULL UNIQUE"
            ")"
        )
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            self.connection.commit()
        finally:
            cursor.close()

    def insert_user(self, name: str, email: str) -> int:
        """Insert a user and return the new row id."""
        query = "INSERT INTO users (name, email) VALUES (%s, %s)"
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (name, email))
            self.connection.commit()
            return cursor.lastrowid
        finally:
            cursor.close()

    def get_user(self, user_id: int) -> dict | None:
        """Return a user dict by id, or None if not found."""
        query = "SELECT id, name, email FROM users WHERE id = %s"
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(query, (user_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    def get_all_users(self) -> list[dict]:
        """Return all users as a list of dicts."""
        query = "SELECT id, name, email FROM users"
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()

    def update_user(self, user_id: int, name: str, email: str) -> int:
        """Update a user's name and email; return number of rows affected."""
        query = "UPDATE users SET name = %s, email = %s WHERE id = %s"
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (name, email, user_id))
            self.connection.commit()
            return cursor.rowcount
        finally:
            cursor.close()

    def delete_user(self, user_id: int) -> int:
        """Delete a user by id; return number of rows affected."""
        query = "DELETE FROM users WHERE id = %s"
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (user_id,))
            self.connection.commit()
            return cursor.rowcount
        finally:
            cursor.close()
