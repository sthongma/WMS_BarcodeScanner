"""
Tests for ScanLogRepository class

This module tests the scan log repository functionality including:
- Creating scan records
- Retrieving scan history
- Searching with filters
- Generating reports
- Duplicate checking
- Summary statistics
"""
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_db_manager():
    """Mock DatabaseManager for testing"""
    mock_db = MagicMock()
    mock_db.execute_query = MagicMock(return_value=[])
    mock_db.execute_non_query = MagicMock(return_value=1)
    return mock_db


@pytest.fixture
def scan_log_repo(mock_db_manager):
    """Create ScanLogRepository instance with mocked database"""
    from src.database.scan_log_repository import ScanLogRepository
    return ScanLogRepository(mock_db_manager)


@pytest.mark.unit
@pytest.mark.database
class TestScanLogRepositoryBasics:
    """Test basic ScanLogRepository functionality"""

    def test_table_name(self, scan_log_repo):
        """Test that table name is correct"""
        assert scan_log_repo.table_name == "scan_logs"

    def test_create_scan(self, scan_log_repo, mock_db_manager):
        """Test creating a new scan log"""
        mock_db_manager.execute_non_query.return_value = 1

        rowcount = scan_log_repo.create_scan(
            barcode='BC123',
            job_type='Inbound',
            user_id='user1',
            job_id=1,
            sub_job_id=2,
            notes='Test note'
        )

        assert rowcount == 1
        mock_db_manager.execute_non_query.assert_called_once()

        # Verify INSERT query
        call_args = mock_db_manager.execute_non_query.call_args[0]
        assert "INSERT INTO scan_logs" in call_args[0]
        assert "GETDATE()" in call_args[0]
        assert call_args[1] == ('BC123', 'Inbound', 'user1', 1, 2, 'Test note')

    def test_create_scan_without_sub_job(self, scan_log_repo, mock_db_manager):
        """Test creating scan without sub job"""
        mock_db_manager.execute_non_query.return_value = 1

        rowcount = scan_log_repo.create_scan(
            barcode='BC456',
            job_type='Outbound',
            user_id='user2',
            job_id=3
        )

        assert rowcount == 1
        call_args = mock_db_manager.execute_non_query.call_args[0]
        assert call_args[1] == ('BC456', 'Outbound', 'user2', 3, None, '')


@pytest.mark.unit
@pytest.mark.database
class TestScanLogRepositoryHistory:
    """Test scan history retrieval"""

    def test_get_recent_scans_with_sub_job_name(self, scan_log_repo, mock_db_manager):
        """Test getting recent scans with sub job name"""
        mock_db_manager.execute_query.return_value = [
            {'id': 1, 'barcode': 'BC123', 'sub_job_name': 'Receiving'},
            {'id': 2, 'barcode': 'BC456', 'sub_job_name': 'Putaway'}
        ]

        results = scan_log_repo.get_recent_scans(limit=50, include_sub_job_name=True)

        assert len(results) == 2
        assert results[0]['sub_job_name'] == 'Receiving'
        mock_db_manager.execute_query.assert_called_once()

        # Verify query includes JOIN
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "LEFT JOIN sub_job_types" in call_args[0]
        assert "TOP 50" in call_args[0]

    def test_get_recent_scans_without_sub_job_name(self, scan_log_repo, mock_db_manager):
        """Test getting recent scans without sub job name"""
        mock_db_manager.execute_query.return_value = [
            {'id': 1, 'barcode': 'BC123'},
            {'id': 2, 'barcode': 'BC456'}
        ]

        results = scan_log_repo.get_recent_scans(limit=100, include_sub_job_name=False)

        assert len(results) == 2

        # Verify query does NOT include JOIN
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "LEFT JOIN" not in call_args[0]
        assert "TOP 100" in call_args[0]

    def test_check_duplicate_found(self, scan_log_repo, mock_db_manager):
        """Test duplicate check when barcode exists"""
        mock_db_manager.execute_query.return_value = [
            {'id': 1, 'barcode': 'BC123', 'job_id': 1, 'scan_date': '2024-01-01'}
        ]

        result = scan_log_repo.check_duplicate('BC123', job_id=1, hours=24)

        assert result is not None
        assert result['barcode'] == 'BC123'
        mock_db_manager.execute_query.assert_called_once()

        # Verify query checks barcode, job_id, and time window
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "barcode = ?" in call_args[0]
        assert "job_id = ?" in call_args[0]
        assert "DATEADD(HOUR" in call_args[0]
        assert call_args[1] == ('BC123', 1, -24)

    def test_check_duplicate_not_found(self, scan_log_repo, mock_db_manager):
        """Test duplicate check when barcode not found"""
        mock_db_manager.execute_query.return_value = []

        result = scan_log_repo.check_duplicate('BC999', job_id=1)

        assert result is None


@pytest.mark.unit
@pytest.mark.database
class TestScanLogRepositorySearch:
    """Test scan log searching"""

    def test_search_history_all_filters(self, scan_log_repo, mock_db_manager):
        """Test searching with all filters"""
        mock_db_manager.execute_query.return_value = [
            {'id': 1, 'barcode': 'BC123'}
        ]

        results = scan_log_repo.search_history(
            barcode='BC',
            job_id=1,
            sub_job_id=2,
            user_id='user1',
            start_date='2024-01-01',
            end_date='2024-01-31',
            limit=50
        )

        assert len(results) == 1
        mock_db_manager.execute_query.assert_called_once()

        # Verify all filters are in the query
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "barcode LIKE ?" in call_args[0]
        assert "job_id = ?" in call_args[0]
        assert "sub_job_id = ?" in call_args[0]
        assert "user_id = ?" in call_args[0]
        assert "scan_date AS DATE) >= ?" in call_args[0]
        assert "scan_date AS DATE) <= ?" in call_args[0]
        assert "TOP 50" in call_args[0]

        # Verify parameters
        assert '%BC%' in call_args[1]
        assert 1 in call_args[1]
        assert 2 in call_args[1]
        assert 'user1' in call_args[1]
        assert '2024-01-01' in call_args[1]
        assert '2024-01-31' in call_args[1]

    def test_search_history_no_filters(self, scan_log_repo, mock_db_manager):
        """Test searching with no filters"""
        mock_db_manager.execute_query.return_value = []

        results = scan_log_repo.search_history()

        mock_db_manager.execute_query.assert_called_once()

        # Verify query has default WHERE clause
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "WHERE 1=1" in call_args[0]

    def test_search_history_partial_barcode(self, scan_log_repo, mock_db_manager):
        """Test searching with partial barcode match"""
        mock_db_manager.execute_query.return_value = []

        scan_log_repo.search_history(barcode='123')

        call_args = mock_db_manager.execute_query.call_args[0]
        assert '%123%' in call_args[1]


@pytest.mark.unit
@pytest.mark.database
class TestScanLogRepositoryReports:
    """Test report generation"""

    def test_get_report_with_sub_job(self, scan_log_repo, mock_db_manager):
        """Test getting report with sub job filter"""
        mock_db_manager.execute_query.return_value = [
            {'id': 1, 'barcode': 'BC123', 'sub_job_name': 'Receiving'}
        ]

        results = scan_log_repo.get_report_with_sub_job(
            start_date='2024-01-01',
            end_date='2024-01-31',
            job_id=1,
            sub_job_id=2
        )

        assert len(results) == 1
        mock_db_manager.execute_query.assert_called_once()

        # Verify query
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "BETWEEN ? AND ?" in call_args[0]
        assert "job_id = ?" in call_args[0]
        assert "sub_job_id = ?" in call_args[0]
        assert "LEFT JOIN sub_job_types" in call_args[0]
        assert call_args[1] == ('2024-01-01', '2024-01-31', 1, 2)

    def test_get_report_with_sub_job_no_filters(self, scan_log_repo, mock_db_manager):
        """Test getting report without job filters"""
        mock_db_manager.execute_query.return_value = []

        scan_log_repo.get_report_with_sub_job(
            start_date='2024-01-01',
            end_date='2024-01-31'
        )

        # Verify only date filter
        call_args = mock_db_manager.execute_query.call_args[0]
        assert call_args[1] == ('2024-01-01', '2024-01-31')

    def test_get_report_main_job_only(self, scan_log_repo, mock_db_manager):
        """Test getting report for main job only"""
        mock_db_manager.execute_query.return_value = [
            {'id': 1, 'barcode': 'BC123'}
        ]

        results = scan_log_repo.get_report_main_job_only(
            start_date='2024-01-01',
            end_date='2024-01-31',
            job_id=1
        )

        assert len(results) == 1
        mock_db_manager.execute_query.assert_called_once()

        # Verify query parameters
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "job_id = ?" in call_args[0]
        assert "BETWEEN ? AND ?" in call_args[0]
        assert call_args[1] == (1, '2024-01-01', '2024-01-31')


@pytest.mark.unit
@pytest.mark.database
class TestScanLogRepositoryCounts:
    """Test count and summary operations"""

    def test_get_today_summary_count_with_sub_job(self, scan_log_repo, mock_db_manager):
        """Test getting today's count with sub job"""
        mock_db_manager.execute_query.return_value = [{'total_count': 15}]

        count = scan_log_repo.get_today_summary_count(job_id=1, sub_job_id=2)

        assert count == 15
        mock_db_manager.execute_query.assert_called_once()

        # Verify query
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "job_id = ?" in call_args[0]
        assert "sub_job_id = ?" in call_args[0]
        assert "GETDATE()" in call_args[0]
        assert call_args[1] == (1, 2)

    def test_get_today_summary_count_main_job_only(self, scan_log_repo, mock_db_manager):
        """Test getting today's count without sub job"""
        mock_db_manager.execute_query.return_value = [{'total_count': 25}]

        count = scan_log_repo.get_today_summary_count(job_id=1)

        assert count == 25

        # Verify query does NOT filter by sub_job_id
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "job_id = ?" in call_args[0]
        assert "sub_job_id" not in call_args[0]
        assert call_args[1] == (1,)

    def test_get_count_by_job_with_dates(self, scan_log_repo, mock_db_manager):
        """Test getting count by job with date range"""
        mock_db_manager.execute_query.return_value = [{'count': 100}]

        count = scan_log_repo.get_count_by_job(
            job_id=1,
            start_date='2024-01-01',
            end_date='2024-01-31'
        )

        assert count == 100
        mock_db_manager.execute_query.assert_called_once()

        # Verify query
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "BETWEEN ? AND ?" in call_args[0]
        assert call_args[1] == (1, '2024-01-01', '2024-01-31')

    def test_get_count_by_job_no_dates(self, scan_log_repo, mock_db_manager):
        """Test getting count by job without dates"""
        mock_db_manager.execute_query.return_value = [{'count': 500}]

        count = scan_log_repo.get_count_by_job(job_id=1)

        assert count == 500

        # Verify simpler query
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "WHERE job_id = ?" in call_args[0]
        assert "BETWEEN" not in call_args[0]
        assert call_args[1] == (1,)

    def test_get_today_summary_count_no_results(self, scan_log_repo, mock_db_manager):
        """Test getting count when no results"""
        mock_db_manager.execute_query.return_value = []

        count = scan_log_repo.get_today_summary_count(job_id=1)

        assert count == 0


@pytest.mark.unit
@pytest.mark.database
class TestScanLogRepositoryTableManagement:
    """Test table and index creation"""

    def test_ensure_table_exists_success(self, scan_log_repo, mock_db_manager):
        """Test table creation succeeds"""
        mock_db_manager.execute_non_query.return_value = 0

        result = scan_log_repo.ensure_table_exists()

        assert result is True
        mock_db_manager.execute_non_query.assert_called_once()

        # Verify CREATE TABLE query
        call_args = mock_db_manager.execute_non_query.call_args[0]
        assert "CREATE TABLE scan_logs" in call_args[0]
        assert "barcode NVARCHAR(100)" in call_args[0]
        assert "FOREIGN KEY (job_id) REFERENCES job_types(id)" in call_args[0]

    def test_ensure_table_exists_failure(self, scan_log_repo, mock_db_manager):
        """Test table creation fails gracefully"""
        mock_db_manager.execute_non_query.side_effect = Exception("Database error")

        result = scan_log_repo.ensure_table_exists()

        assert result is False

    def test_ensure_indexes_exist_success(self, scan_log_repo, mock_db_manager):
        """Test index creation succeeds"""
        mock_db_manager.execute_non_query.return_value = 0

        result = scan_log_repo.ensure_indexes_exist()

        assert result is True
        # Should be called 6 times (one for each index)
        assert mock_db_manager.execute_non_query.call_count == 6

        # Verify index creation queries
        calls = mock_db_manager.execute_non_query.call_args_list
        index_names = ['barcode', 'scan_date', 'job_type', 'user_id', 'job_id', 'sub_job_id']
        for i, index_name in enumerate(index_names):
            assert f"idx_scan_logs_{index_name}" in calls[i][0][0]

    def test_ensure_indexes_exist_failure(self, scan_log_repo, mock_db_manager):
        """Test index creation fails gracefully"""
        mock_db_manager.execute_non_query.side_effect = Exception("Database error")

        result = scan_log_repo.ensure_indexes_exist()

        assert result is False
