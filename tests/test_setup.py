"""
Basic setup verification tests

These tests verify that the test infrastructure is working correctly.
"""
import pytest


class TestSetup:
    """Verify test setup is working"""

    def test_pytest_working(self):
        """Verify pytest is installed and working"""
        assert True

    def test_basic_math(self):
        """Verify basic test functionality"""
        assert 1 + 1 == 2
        assert 2 * 3 == 6

    def test_string_operations(self):
        """Verify string operations work"""
        assert "hello".upper() == "HELLO"
        assert "WORLD".lower() == "world"


class TestFixtures:
    """Verify fixtures are working"""

    def test_mock_db_config_fixture(self, mock_db_config):
        """Verify mock_db_config fixture works"""
        assert isinstance(mock_db_config, dict)
        assert "server" in mock_db_config
        assert "database" in mock_db_config
        assert mock_db_config["server"] == "test-server"

    def test_mock_connection_string_fixture(self, mock_connection_string):
        """Verify mock_connection_string fixture works"""
        assert isinstance(mock_connection_string, str)
        assert "DRIVER=" in mock_connection_string
        assert "SERVER=" in mock_connection_string

    def test_sample_job_type_fixture(self, sample_job_type):
        """Verify sample_job_type fixture works"""
        assert isinstance(sample_job_type, dict)
        assert "id" in sample_job_type
        assert "job_name" in sample_job_type
        assert sample_job_type["job_name"] == "Receiving"

    def test_sample_scan_log_fixture(self, sample_scan_log):
        """Verify sample_scan_log fixture works"""
        assert isinstance(sample_scan_log, dict)
        assert "barcode" in sample_scan_log
        assert sample_scan_log["barcode"] == "TEST12345"

    def test_sample_barcodes_fixture(self, sample_barcodes):
        """Verify sample_barcodes fixture works"""
        assert isinstance(sample_barcodes, list)
        assert len(sample_barcodes) > 0
        assert "TEST12345" in sample_barcodes


@pytest.mark.unit
class TestMarkers:
    """Verify pytest markers are working"""

    def test_unit_marker(self):
        """Test marked as unit test"""
        assert True


@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
    (5, 10)
])
def test_parametrize(input, expected):
    """Verify parametrize decorator works"""
    assert input * 2 == expected
