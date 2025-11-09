"""
Tests for JobTypeRepository class

This module tests the job type repository functionality including:
- Getting all job types
- Finding job types by ID and name
- Creating new job types
- Deleting job types
- Validation and duplicate checking
"""
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_db_manager():
    """Mock DatabaseManager for testing"""
    mock_db = MagicMock()
    mock_db.execute_query = MagicMock(return_value=[])
    mock_db.execute_non_query = MagicMock(return_value=1)
    return mock_db


@pytest.fixture
def job_type_repo(mock_db_manager):
    """Create JobTypeRepository instance with mocked database"""
    from src.database.job_type_repository import JobTypeRepository
    return JobTypeRepository(mock_db_manager)


@pytest.mark.unit
@pytest.mark.database
class TestJobTypeRepositoryBasics:
    """Test basic JobTypeRepository functionality"""

    def test_table_name(self, job_type_repo):
        """Test that table name is correct"""
        assert job_type_repo.table_name == "job_types"

    def test_get_all_job_types(self, job_type_repo, mock_db_manager):
        """Test getting all job types"""
        mock_db_manager.execute_query.return_value = [
            {'id': 1, 'job_name': 'Inbound'},
            {'id': 2, 'job_name': 'Outbound'}
        ]

        results = job_type_repo.get_all_job_types()

        assert len(results) == 2
        assert results[0]['job_name'] == 'Inbound'
        mock_db_manager.execute_query.assert_called_once()

        # Verify query is correct
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "SELECT id, job_name FROM job_types" in call_args[0]
        assert "ORDER BY job_name" in call_args[0]

    def test_find_by_id(self, job_type_repo, mock_db_manager):
        """Test finding job type by ID"""
        mock_db_manager.execute_query.return_value = [
            {'id': 1, 'job_name': 'Inbound'}
        ]

        result = job_type_repo.find_by_id(1)

        assert result is not None
        assert result['job_name'] == 'Inbound'
        mock_db_manager.execute_query.assert_called_once_with(
            "SELECT * FROM job_types WHERE id = ?",
            (1,)
        )

    def test_find_by_id_not_found(self, job_type_repo, mock_db_manager):
        """Test finding job type by ID when not found"""
        mock_db_manager.execute_query.return_value = []

        result = job_type_repo.find_by_id(999)

        assert result is None

    def test_find_by_name(self, job_type_repo, mock_db_manager):
        """Test finding job type by name"""
        mock_db_manager.execute_query.return_value = [
            {'id': 1, 'job_name': 'Inbound'}
        ]

        result = job_type_repo.find_by_name('Inbound')

        assert result is not None
        assert result['id'] == 1
        mock_db_manager.execute_query.assert_called_once_with(
            "SELECT * FROM job_types WHERE job_name = ?",
            ('Inbound',)
        )

    def test_find_by_name_not_found(self, job_type_repo, mock_db_manager):
        """Test finding job type by name when not found"""
        mock_db_manager.execute_query.return_value = []

        result = job_type_repo.find_by_name('NonExistent')

        assert result is None


@pytest.mark.unit
@pytest.mark.database
class TestJobTypeRepositoryCreate:
    """Test job type creation"""

    def test_create_job_type(self, job_type_repo, mock_db_manager):
        """Test creating a new job type"""
        mock_db_manager.execute_non_query.return_value = 1

        rowcount = job_type_repo.create_job_type('Transfer')

        assert rowcount == 1
        mock_db_manager.execute_non_query.assert_called_once()

        # Verify the INSERT query
        call_args = mock_db_manager.execute_non_query.call_args[0]
        assert "INSERT INTO job_types" in call_args[0]
        assert "job_name" in call_args[0]
        assert call_args[1] == ('Transfer',)

    def test_job_name_exists_true(self, job_type_repo, mock_db_manager):
        """Test checking if job name exists (returns true)"""
        mock_db_manager.execute_query.return_value = [{'count': 1}]

        exists = job_type_repo.job_name_exists('Inbound')

        assert exists is True
        mock_db_manager.execute_query.assert_called_once_with(
            "SELECT COUNT(*) as count FROM job_types WHERE job_name = ?",
            ('Inbound',)
        )

    def test_job_name_exists_false(self, job_type_repo, mock_db_manager):
        """Test checking if job name exists (returns false)"""
        mock_db_manager.execute_query.return_value = [{'count': 0}]

        exists = job_type_repo.job_name_exists('NonExistent')

        assert exists is False

    def test_job_name_exists_exclude_id(self, job_type_repo, mock_db_manager):
        """Test checking if job name exists with ID exclusion"""
        mock_db_manager.execute_query.return_value = [{'count': 0}]

        exists = job_type_repo.job_name_exists('Inbound', exclude_id=1)

        assert exists is False
        mock_db_manager.execute_query.assert_called_once_with(
            "SELECT COUNT(*) as count FROM job_types WHERE job_name = ? AND id != ?",
            ('Inbound', 1)
        )


@pytest.mark.unit
@pytest.mark.database
class TestJobTypeRepositoryDelete:
    """Test job type deletion"""

    def test_delete_job_type(self, job_type_repo, mock_db_manager):
        """Test deleting a job type"""
        mock_db_manager.execute_non_query.return_value = 1

        rowcount = job_type_repo.delete_job_type(1)

        assert rowcount == 1
        mock_db_manager.execute_non_query.assert_called_once_with(
            "DELETE FROM job_types WHERE id = ?",
            (1,)
        )

    def test_delete_job_type_not_found(self, job_type_repo, mock_db_manager):
        """Test deleting a non-existent job type"""
        mock_db_manager.execute_non_query.return_value = 0

        rowcount = job_type_repo.delete_job_type(999)

        assert rowcount == 0


@pytest.mark.unit
@pytest.mark.database
class TestJobTypeRepositoryCount:
    """Test job type counting"""

    def test_get_job_type_count(self, job_type_repo, mock_db_manager):
        """Test getting total count of job types"""
        mock_db_manager.execute_query.return_value = [{'count': 5}]

        count = job_type_repo.get_job_type_count()

        assert count == 5
        mock_db_manager.execute_query.assert_called_once()

        # Verify COUNT query
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "SELECT COUNT(*)" in call_args[0]
        assert "FROM job_types" in call_args[0]

    def test_get_job_type_count_empty(self, job_type_repo, mock_db_manager):
        """Test getting count when table is empty"""
        mock_db_manager.execute_query.return_value = [{'count': 0}]

        count = job_type_repo.get_job_type_count()

        assert count == 0


@pytest.mark.unit
@pytest.mark.database
class TestJobTypeRepositoryTableManagement:
    """Test table creation and management"""

    def test_ensure_table_exists_success(self, job_type_repo, mock_db_manager):
        """Test table creation succeeds"""
        mock_db_manager.execute_non_query.return_value = 0

        result = job_type_repo.ensure_table_exists()

        assert result is True
        mock_db_manager.execute_non_query.assert_called_once()

        # Verify CREATE TABLE query
        call_args = mock_db_manager.execute_non_query.call_args[0]
        assert "CREATE TABLE job_types" in call_args[0]
        assert "id INT PRIMARY KEY IDENTITY" in call_args[0]
        assert "job_name NVARCHAR(100) NOT NULL UNIQUE" in call_args[0]

    def test_ensure_table_exists_failure(self, job_type_repo, mock_db_manager):
        """Test table creation fails gracefully"""
        mock_db_manager.execute_non_query.side_effect = Exception("Database error")

        result = job_type_repo.ensure_table_exists()

        assert result is False
