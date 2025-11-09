"""
Tests for DependencyRepository class

This module tests the dependency repository functionality including:
- Getting required jobs
- Adding/removing dependencies
- Checking scan status
- Validating circular dependencies
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
def dependency_repo(mock_db_manager):
    """Create DependencyRepository instance with mocked database"""
    from src.database.dependency_repository import DependencyRepository
    return DependencyRepository(mock_db_manager)


@pytest.mark.unit
@pytest.mark.database
class TestDependencyRepositoryBasics:
    """Test basic DependencyRepository functionality"""

    def test_table_name(self, dependency_repo):
        """Test that table name is correct"""
        assert dependency_repo.table_name == "job_dependencies"

    def test_get_required_jobs(self, dependency_repo, mock_db_manager):
        """Test getting required jobs for a job"""
        mock_db_manager.execute_query.return_value = [
            {'required_job_id': 1, 'job_name': 'Inbound'},
            {'required_job_id': 2, 'job_name': 'QC'}
        ]

        results = dependency_repo.get_required_jobs(job_id=3)

        assert len(results) == 2
        assert results[0]['job_name'] == 'Inbound'
        mock_db_manager.execute_query.assert_called_once()

        # Verify query joins job_types
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "JOIN job_types" in call_args[0]
        assert "WHERE jd.job_id = ?" in call_args[0]
        assert call_args[1] == (3,)

    def test_get_required_jobs_none(self, dependency_repo, mock_db_manager):
        """Test getting required jobs when none exist"""
        mock_db_manager.execute_query.return_value = []

        results = dependency_repo.get_required_jobs(job_id=1)

        assert len(results) == 0


@pytest.mark.unit
@pytest.mark.database
class TestDependencyRepositoryScanStatus:
    """Test scan status checking"""

    def test_get_required_job_with_scan_status_today(self, dependency_repo, mock_db_manager):
        """Test getting required jobs with today's scan status"""
        mock_db_manager.execute_query.return_value = [
            {'required_job_id': 1, 'job_name': 'Inbound', 'scan_count': 5},
            {'required_job_id': 2, 'job_name': 'QC', 'scan_count': 0}
        ]

        results = dependency_repo.get_required_job_with_scan_status(
            job_id=3,
            check_today_only=True
        )

        assert len(results) == 2
        assert results[0]['scan_count'] == 5
        assert results[1]['scan_count'] == 0

        # Verify query checks today's date
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "CAST(scan_date AS DATE) = CAST(GETDATE() AS DATE)" in call_args[0]

    def test_get_required_job_with_scan_status_all_time(self, dependency_repo, mock_db_manager):
        """Test getting required jobs with all-time scan status"""
        mock_db_manager.execute_query.return_value = []

        dependency_repo.get_required_job_with_scan_status(
            job_id=1,
            check_today_only=False
        )

        # Verify query does NOT check date
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "CAST(GETDATE() AS DATE)" not in call_args[0]

    def test_check_required_job_scanned_today(self, dependency_repo, mock_db_manager):
        """Test checking if required job was scanned today"""
        mock_db_manager.execute_query.return_value = [{'count': 10}]

        count = dependency_repo.check_required_job_scanned(
            required_job_id=1,
            today_only=True
        )

        assert count == 10
        mock_db_manager.execute_query.assert_called_once()

        # Verify query checks today's scans
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "FROM scan_logs" in call_args[0]
        assert "job_id = ?" in call_args[0]
        assert "GETDATE()" in call_args[0]
        assert call_args[1] == (1,)

    def test_check_required_job_scanned_all_time(self, dependency_repo, mock_db_manager):
        """Test checking if required job was ever scanned"""
        mock_db_manager.execute_query.return_value = [{'count': 100}]

        count = dependency_repo.check_required_job_scanned(
            required_job_id=1,
            today_only=False
        )

        assert count == 100

        # Verify query does NOT filter by date
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "GETDATE()" not in call_args[0]

    def test_check_required_job_scanned_no_results(self, dependency_repo, mock_db_manager):
        """Test checking scan count when no results"""
        mock_db_manager.execute_query.return_value = []

        count = dependency_repo.check_required_job_scanned(required_job_id=1)

        assert count == 0


@pytest.mark.unit
@pytest.mark.database
class TestDependencyRepositoryManagement:
    """Test adding/removing dependencies"""

    def test_add_dependency(self, dependency_repo, mock_db_manager):
        """Test adding a new dependency"""
        mock_db_manager.execute_non_query.return_value = 1

        rowcount = dependency_repo.add_dependency(job_id=3, required_job_id=1)

        assert rowcount == 1
        mock_db_manager.execute_non_query.assert_called_once()

        # Verify INSERT query
        call_args = mock_db_manager.execute_non_query.call_args[0]
        assert "INSERT INTO job_dependencies" in call_args[0]
        assert "GETDATE()" in call_args[0]
        assert call_args[1] == (3, 1)

    def test_remove_dependency(self, dependency_repo, mock_db_manager):
        """Test removing a specific dependency"""
        mock_db_manager.execute_non_query.return_value = 1

        rowcount = dependency_repo.remove_dependency(job_id=3, required_job_id=1)

        assert rowcount == 1
        mock_db_manager.execute_non_query.assert_called_once()

        # Verify DELETE query
        call_args = mock_db_manager.execute_non_query.call_args[0]
        assert "DELETE FROM job_dependencies" in call_args[0]
        assert "job_id = ?" in call_args[0]
        assert "required_job_id = ?" in call_args[0]
        assert call_args[1] == (3, 1)

    def test_remove_all_dependencies(self, dependency_repo, mock_db_manager):
        """Test removing all dependencies for a job"""
        mock_db_manager.execute_non_query.return_value = 3

        rowcount = dependency_repo.remove_all_dependencies(job_id=3)

        assert rowcount == 3
        mock_db_manager.execute_non_query.assert_called_once()

        # Verify DELETE query only filters by job_id
        call_args = mock_db_manager.execute_non_query.call_args[0]
        assert "WHERE job_id = ?" in call_args[0]
        assert "required_job_id" not in call_args[0]
        assert call_args[1] == (3,)

    def test_remove_where_required(self, dependency_repo, mock_db_manager):
        """Test removing all dependencies where a job is required"""
        mock_db_manager.execute_non_query.return_value = 2

        rowcount = dependency_repo.remove_where_required(required_job_id=5)

        assert rowcount == 2
        mock_db_manager.execute_non_query.assert_called_once()

        # Verify DELETE query filters by required_job_id
        call_args = mock_db_manager.execute_non_query.call_args[0]
        assert "DELETE FROM job_dependencies" in call_args[0]
        assert "WHERE required_job_id = ?" in call_args[0]
        assert call_args[1] == (5,)

    def test_dependency_exists_true(self, dependency_repo, mock_db_manager):
        """Test checking if dependency exists (returns true)"""
        mock_db_manager.execute_query.return_value = [{'count': 1}]

        exists = dependency_repo.dependency_exists(job_id=3, required_job_id=1)

        assert exists is True
        mock_db_manager.execute_query.assert_called_once()

        # Verify query
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "job_id = ?" in call_args[0]
        assert "required_job_id = ?" in call_args[0]
        assert call_args[1] == (3, 1)

    def test_dependency_exists_false(self, dependency_repo, mock_db_manager):
        """Test checking if dependency exists (returns false)"""
        mock_db_manager.execute_query.return_value = [{'count': 0}]

        exists = dependency_repo.dependency_exists(job_id=3, required_job_id=1)

        assert exists is False


@pytest.mark.unit
@pytest.mark.database
class TestDependencyRepositoryCount:
    """Test counting dependencies"""

    def test_get_dependencies_count(self, dependency_repo, mock_db_manager):
        """Test getting count of dependencies"""
        mock_db_manager.execute_query.return_value = [{'count': 3}]

        count = dependency_repo.get_dependencies_count(job_id=5)

        assert count == 3
        mock_db_manager.execute_query.assert_called_once()

        # Verify COUNT query filters by job_id
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "COUNT(*)" in call_args[0]
        assert "job_dependencies" in call_args[0]


@pytest.mark.unit
@pytest.mark.database
class TestDependencyRepositoryListAll:
    """Test listing all dependencies"""

    def test_get_all_dependencies(self, dependency_repo, mock_db_manager):
        """Test getting all dependencies with job names"""
        mock_db_manager.execute_query.return_value = [
            {
                'id': 1,
                'job_id': 3,
                'job_name': 'Outbound',
                'required_job_id': 1,
                'required_job_name': 'Inbound',
                'created_date': '2024-01-01'
            },
            {
                'id': 2,
                'job_id': 3,
                'job_name': 'Outbound',
                'required_job_id': 2,
                'required_job_name': 'QC',
                'created_date': '2024-01-01'
            }
        ]

        results = dependency_repo.get_all_dependencies()

        assert len(results) == 2
        assert results[0]['job_name'] == 'Outbound'
        assert results[0]['required_job_name'] == 'Inbound'

        # Verify query joins job_types twice
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "JOIN job_types jt1" in call_args[0]
        assert "JOIN job_types jt2" in call_args[0]


@pytest.mark.unit
@pytest.mark.database
class TestDependencyRepositoryValidation:
    """Test dependency validation"""

    def test_validate_no_circular_dependency_valid(self, dependency_repo, mock_db_manager):
        """Test validation when no circular dependency exists"""
        # No reverse dependency found
        mock_db_manager.execute_query.return_value = [{'count': 0}]

        is_valid = dependency_repo.validate_no_circular_dependency(
            job_id=1,
            required_job_id=2
        )

        assert is_valid is True
        mock_db_manager.execute_query.assert_called_once()

        # Verify it checks for reverse dependency
        call_args = mock_db_manager.execute_query.call_args[0]
        assert call_args[1] == (2, 1)  # Reversed order

    def test_validate_no_circular_dependency_invalid(self, dependency_repo, mock_db_manager):
        """Test validation when circular dependency would be created"""
        # Reverse dependency exists
        mock_db_manager.execute_query.return_value = [{'count': 1}]

        is_valid = dependency_repo.validate_no_circular_dependency(
            job_id=1,
            required_job_id=2
        )

        assert is_valid is False


@pytest.mark.unit
@pytest.mark.database
class TestDependencyRepositoryTableManagement:
    """Test table creation"""

    def test_ensure_table_exists_success(self, dependency_repo, mock_db_manager):
        """Test table creation succeeds"""
        mock_db_manager.execute_non_query.return_value = 0

        result = dependency_repo.ensure_table_exists()

        assert result is True
        mock_db_manager.execute_non_query.assert_called_once()

        # Verify CREATE TABLE query
        call_args = mock_db_manager.execute_non_query.call_args[0]
        assert "CREATE TABLE job_dependencies" in call_args[0]
        assert "FOREIGN KEY (job_id) REFERENCES job_types(id)" in call_args[0]
        assert "FOREIGN KEY (required_job_id) REFERENCES job_types(id)" in call_args[0]
        assert "CONSTRAINT unique_job_dependency UNIQUE" in call_args[0]

    def test_ensure_table_exists_failure(self, dependency_repo, mock_db_manager):
        """Test table creation fails gracefully"""
        mock_db_manager.execute_non_query.side_effect = Exception("Database error")

        result = dependency_repo.ensure_table_exists()

        assert result is False
