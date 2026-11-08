from datetime import date
from unittest.mock import MagicMock, patch
from scripts.load_postgres import get_postgres_connection

import pytest

from scripts.load_postgres import (
    save_records_to_postgres,
    validate_persisted_records,
)


def test_validate_persisted_records_with_all_records(monkeypatch):
    monkeypatch.setenv("BCB_POSTGRES_HOST", "postgres_bcb")
    monkeypatch.setenv("BCB_POSTGRES_DB", "bcb")
    monkeypatch.setenv("BCB_POSTGRES_USER", "bcb")
    monkeypatch.setenv("BCB_POSTGRES_PASSWORD", "bcb")
    expected_keys = {
        (432, date(2026, 10, 1)),
        (11, date(2026, 10, 1)),
    }

    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = list(expected_keys)

    mock_conn = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    with patch(
        "scripts.load_postgres.psycopg.connect",
        return_value=mock_conn
    ):
        validate_persisted_records(expected_keys)


def test_validate_persisted_records_with_missing_record(monkeypatch):
    monkeypatch.setenv("BCB_POSTGRES_HOST", "postgres_bcb")
    monkeypatch.setenv("BCB_POSTGRES_DB", "bcb")
    monkeypatch.setenv("BCB_POSTGRES_USER", "bcb")
    monkeypatch.setenv("BCB_POSTGRES_PASSWORD", "bcb")
    expected_keys = {
        (432, date(2026, 10, 1)),
        (11, date(2026, 10, 1)),
    }

    persisted_keys = [
        (432, date(2026, 10, 1)),
    ]

    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = persisted_keys

    mock_conn = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    with patch(
        "scripts.load_postgres.psycopg.connect",
        return_value=mock_conn
    ):
        with pytest.raises(
            ValueError,
            match="Missing records in the database"
        ):
            validate_persisted_records(expected_keys)


def test_save_records_to_postgres_propagates_database_error(monkeypatch):
    monkeypatch.setenv("BCB_POSTGRES_HOST", "postgres_bcb")
    monkeypatch.setenv("BCB_POSTGRES_DB", "bcb")
    monkeypatch.setenv("BCB_POSTGRES_USER", "bcb")
    monkeypatch.setenv("BCB_POSTGRES_PASSWORD", "bcb")
    normalized_data = [
        {
            "series_code": 432,
            "series_name": "Test series",
            "reference_date": date(2026, 10, 18),
            "indicator_value": 10,
        }
    ]

    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = RuntimeError("database error")

    mock_conn = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    with patch(
        "scripts.load_postgres.psycopg.connect",
        return_value=mock_conn,
    ):
        with pytest.raises(RuntimeError, match="database error"):
            save_records_to_postgres(normalized_data)


def test_get_postgres_connection_fails_when_required_env_is_missing(monkeypatch):
    monkeypatch.setenv("BCB_POSTGRES_HOST", "postgres_bcb")
    monkeypatch.setenv("BCB_POSTGRES_DB", "bcb")
    monkeypatch.setenv("BCB_POSTGRES_USER", "bcb")
    monkeypatch.delenv("BCB_POSTGRES_PASSWORD", raising=False)

    with pytest.raises(KeyError, match="BCB_POSTGRES_PASSWORD"):
        get_postgres_connection()
