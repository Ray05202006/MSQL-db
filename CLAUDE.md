# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests with coverage
pytest tests/ -v --cov=db --cov-report=term-missing

# Run a single test file
pytest tests/test_database.py -v

# Run a single test by name
pytest tests/test_database.py::TestInsertUser::test_insert_user_returns_lastrowid -v
```

Python version: 3.12

## Architecture

This is a Python library (not a standalone application) providing a `Database` class in `db/database.py` that wraps `mysql-connector-python` for CRUD operations on a `users` table. There is no application entry point — the class is meant to be imported.

All database methods use parameterized queries (`%s` placeholders) and manage cursors via `try/finally` for cleanup.

## Testing

Tests live in `tests/` and use pytest with `unittest.mock` to mock all MySQL connections — no real database is needed. Tests are organized as one class per Database method (e.g., `TestConnect`, `TestInsertUser`, `TestDeleteUser`), with a shared `db` fixture for the Database instance and a `mock_connection` fixture for the mocked MySQL connection.
