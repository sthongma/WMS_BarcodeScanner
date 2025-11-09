"""
Pytest Configuration and Fixtures

This file contains shared pytest fixtures and configuration for all tests.
"""
import os
import sys
from typing import Dict, Any, Optional
from unittest.mock import Mock, MagicMock
import pytest

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture
def mock_db_config() -> Dict[str, Any]:
    """Provide mock database configuration for testing."""
    return {
        "server": "test-server",
        "database": "test-database",
        "username": "test-user",
        "password": "test-password",
        "driver": "ODBC Driver 17 for SQL Server",
        "trusted_connection": False
    }


@pytest.fixture
def mock_connection_string(mock_db_config: Dict[str, Any]) -> str:
    """Provide mock connection string for testing."""
    config = mock_db_config
    return (
        f"DRIVER={{{config['driver']}}};"
        f"SERVER={config['server']};"
        f"DATABASE={config['database']};"
        f"UID={config['username']};"
        f"PWD={config['password']}"
    )


@pytest.fixture
def mock_database_manager(mock_db_config: Dict[str, Any]):
    """Provide a mocked DatabaseManager instance."""
    mock_db = MagicMock()
    mock_db.config = mock_db_config
    mock_db.connection_string = (
        f"DRIVER={{{mock_db_config['driver']}}};"
        f"SERVER={mock_db_config['server']};"
        f"DATABASE={mock_db_config['database']};"
        f"UID={mock_db_config['username']};"
        f"PWD={mock_db_config['password']}"
    )
    mock_db.current_user = "test_user"
    mock_db.execute_query = MagicMock(return_value=[])
    mock_db.execute_non_query = MagicMock(return_value=True)
    mock_db.execute_scalar = MagicMock(return_value=None)
    return mock_db


@pytest.fixture
def mock_db_cursor():
    """Provide a mocked database cursor."""
    cursor = MagicMock()
    cursor.description = None
    cursor.fetchall = MagicMock(return_value=[])
    cursor.fetchone = MagicMock(return_value=None)
    cursor.rowcount = 0
    cursor.execute = MagicMock()
    cursor.commit = MagicMock()
    cursor.close = MagicMock()
    return cursor


@pytest.fixture
def mock_db_connection(mock_db_cursor):
    """Provide a mocked database connection."""
    connection = MagicMock()
    connection.cursor = MagicMock(return_value=mock_db_cursor)
    connection.commit = MagicMock()
    connection.rollback = MagicMock()
    connection.close = MagicMock()
    return connection


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def sample_job_type() -> Dict[str, Any]:
    """Provide sample job type data for testing."""
    return {
        "id": 1,
        "job_name": "Receiving",
        "is_active": True,
        "created_at": "2025-01-01 10:00:00",
        "notes": "Test job type"
    }


@pytest.fixture
def sample_sub_job_type() -> Dict[str, Any]:
    """Provide sample sub job type data for testing."""
    return {
        "id": 1,
        "sub_job_name": "Quality Check",
        "main_job_id": 1,
        "is_active": True,
        "created_at": "2025-01-01 10:00:00"
    }


@pytest.fixture
def sample_scan_log() -> Dict[str, Any]:
    """Provide sample scan log data for testing."""
    return {
        "id": 1,
        "barcode": "TEST12345",
        "scan_date": "2025-01-01 12:00:00",
        "job_type": "Receiving",
        "sub_job_name": "Quality Check",
        "user_id": "test_user",
        "notes": "Test scan"
    }


@pytest.fixture
def sample_dependency() -> Dict[str, Any]:
    """Provide sample job dependency data for testing."""
    return {
        "job_id": 2,
        "required_job_id": 1,
        "job_name": "Putaway",
        "required_job_name": "Receiving"
    }


@pytest.fixture
def sample_barcodes() -> list:
    """Provide a list of sample barcodes for testing."""
    return [
        "BARCODE001",
        "BARCODE002",
        "BARCODE003",
        "TEST12345",
        "ITEM-9999"
    ]


# ============================================================================
# File & Path Fixtures
# ============================================================================

@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory for testing."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def temp_sql_config(temp_config_dir, mock_db_config):
    """Create a temporary SQL config file for testing."""
    import json
    config_file = temp_config_dir / "sql_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(mock_db_config, f, indent=4)
    return config_file


# ============================================================================
# Mock UI Fixtures (for GUI testing)
# ============================================================================

@pytest.fixture
def mock_tk_root():
    """Provide a mocked Tkinter root window."""
    mock_root = MagicMock()
    mock_root.title = MagicMock()
    mock_root.geometry = MagicMock()
    mock_root.protocol = MagicMock()
    mock_root.mainloop = MagicMock()
    return mock_root


@pytest.fixture
def mock_messagebox():
    """Provide mocked messagebox functions."""
    return {
        'showinfo': MagicMock(),
        'showwarning': MagicMock(),
        'showerror': MagicMock(),
        'askyesno': MagicMock(return_value=True),
        'askokcancel': MagicMock(return_value=True)
    }


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "ui: mark test as UI test"
    )
    config.addinivalue_line(
        "markers", "database: mark test as database test"
    )
    config.addinivalue_line(
        "markers", "services: mark test as service layer test"
    )


# ============================================================================
# Cleanup
# ============================================================================

@pytest.fixture(autouse=True)
def reset_mocks():
    """Automatically reset all mocks after each test."""
    yield
    # Cleanup happens after test
