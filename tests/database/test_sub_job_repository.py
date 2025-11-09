"""
Tests for SubJobRepository class

This module tests the sub job repository functionality including:
- Getting sub jobs by main job
- Finding sub jobs by ID and name
- Creating new sub jobs
- Soft deleting sub jobs
- Duplicate checking
- Activation/deactivation
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
def sub_job_repo(mock_db_manager):
    """Create SubJobRepository instance with mocked database"""
    from src.database.sub_job_repository import SubJobRepository
    return SubJobRepository(mock_db_manager)


@pytest.mark.unit
@pytest.mark.database
class TestSubJobRepositoryBasics:
    """Test basic SubJobRepository functionality"""

    def test_table_name(self, sub_job_repo):
        """Test that table name is correct"""
        assert sub_job_repo.table_name == "sub_job_types"

    def test_get_by_main_job_active_only(self, sub_job_repo, mock_db_manager):
        """Test getting active sub jobs for a main job"""
        mock_db_manager.execute_query.return_value = [
            {'id': 1, 'sub_job_name': 'Receiving'},
            {'id': 2, 'sub_job_name': 'Putaway'}
        ]

        results = sub_job_repo.get_by_main_job(1, active_only=True)

        assert len(results) == 2
        assert results[0]['sub_job_name'] == 'Receiving'
        mock_db_manager.execute_query.assert_called_once()

        # Verify query includes is_active = 1
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "main_job_id = ?" in call_args[0]
        assert "is_active = 1" in call_args[0]
        assert call_args[1] == (1,)

    def test_get_by_main_job_include_inactive(self, sub_job_repo, mock_db_manager):
        """Test getting all sub jobs including inactive ones"""
        mock_db_manager.execute_query.return_value = [
            {'id': 1, 'sub_job_name': 'Active', 'is_active': 1},
            {'id': 2, 'sub_job_name': 'Inactive', 'is_active': 0}
        ]

        results = sub_job_repo.get_by_main_job(1, active_only=False)

        assert len(results) == 2
        # Verify query does NOT filter by is_active
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "main_job_id = ?" in call_args[0]
        # Should not have is_active filter but should include it in SELECT
        assert "is_active" in call_args[0]

    def test_find_by_name(self, sub_job_repo, mock_db_manager):
        """Test finding sub job by name within main job"""
        mock_db_manager.execute_query.return_value = [
            {'id': 1, 'main_job_id': 1, 'sub_job_name': 'Receiving'}
        ]

        result = sub_job_repo.find_by_name(1, 'Receiving')

        assert result is not None
        assert result['sub_job_name'] == 'Receiving'
        mock_db_manager.execute_query.assert_called_once()

        # Verify query filters by both main_job_id and sub_job_name
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "main_job_id = ?" in call_args[0]
        assert "sub_job_name = ?" in call_args[0]
        assert "is_active = 1" in call_args[0]
        assert call_args[1] == (1, 'Receiving')

    def test_find_by_name_not_found(self, sub_job_repo, mock_db_manager):
        """Test finding sub job by name when not found"""
        mock_db_manager.execute_query.return_value = []

        result = sub_job_repo.find_by_name(1, 'NonExistent')

        assert result is None

    def test_get_details(self, sub_job_repo, mock_db_manager):
        """Test getting detailed sub job information"""
        mock_db_manager.execute_query.return_value = [{
            'id': 1,
            'main_job_id': 1,
            'sub_job_name': 'Receiving',
            'description': 'Receive goods',
            'created_date': '2024-01-01',
            'updated_date': '2024-01-01',
            'is_active': 1
        }]

        result = sub_job_repo.get_details(1)

        assert result is not None
        assert result['description'] == 'Receive goods'
        assert 'created_date' in result
        assert 'updated_date' in result


@pytest.mark.unit
@pytest.mark.database
class TestSubJobRepositoryCreate:
    """Test sub job creation"""

    def test_create_sub_job(self, sub_job_repo, mock_db_manager):
        """Test creating a new sub job"""
        mock_db_manager.execute_non_query.return_value = 1

        rowcount = sub_job_repo.create_sub_job(1, 'Receiving', 'Receive goods')

        assert rowcount == 1
        mock_db_manager.execute_non_query.assert_called_once()

        # Verify INSERT query
        call_args = mock_db_manager.execute_non_query.call_args[0]
        assert "INSERT INTO sub_job_types" in call_args[0]
        assert "GETDATE()" in call_args[0]
        assert call_args[1] == (1, 'Receiving', 'Receive goods')

    def test_create_sub_job_without_description(self, sub_job_repo, mock_db_manager):
        """Test creating sub job without description"""
        mock_db_manager.execute_non_query.return_value = 1

        rowcount = sub_job_repo.create_sub_job(1, 'Putaway')

        assert rowcount == 1
        call_args = mock_db_manager.execute_non_query.call_args[0]
        assert call_args[1] == (1, 'Putaway', '')

    def test_duplicate_exists_true(self, sub_job_repo, mock_db_manager):
        """Test checking if sub job name exists (returns true)"""
        mock_db_manager.execute_query.return_value = [{'count': 1}]

        exists = sub_job_repo.duplicate_exists(1, 'Receiving')

        assert exists is True
        mock_db_manager.execute_query.assert_called_once()

        # Verify query checks both main_job_id and sub_job_name
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "main_job_id = ?" in call_args[0]
        assert "sub_job_name = ?" in call_args[0]
        assert "is_active = 1" in call_args[0]
        assert call_args[1] == (1, 'Receiving')

    def test_duplicate_exists_false(self, sub_job_repo, mock_db_manager):
        """Test checking if sub job name exists (returns false)"""
        mock_db_manager.execute_query.return_value = [{'count': 0}]

        exists = sub_job_repo.duplicate_exists(1, 'NonExistent')

        assert exists is False

    def test_duplicate_exists_exclude_id(self, sub_job_repo, mock_db_manager):
        """Test checking duplicate with ID exclusion"""
        mock_db_manager.execute_query.return_value = [{'count': 0}]

        exists = sub_job_repo.duplicate_exists(1, 'Receiving', exclude_id=1)

        assert exists is False

        # Verify query excludes the specified ID
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "id != ?" in call_args[0]
        assert call_args[1] == (1, 'Receiving', 1)


@pytest.mark.unit
@pytest.mark.database
class TestSubJobRepositorySoftDelete:
    """Test soft delete functionality"""

    def test_soft_delete(self, sub_job_repo, mock_db_manager):
        """Test soft deleting a sub job"""
        mock_db_manager.execute_non_query.return_value = 1

        rowcount = sub_job_repo.soft_delete(1)

        assert rowcount == 1
        mock_db_manager.execute_non_query.assert_called_once()

        # Verify UPDATE query sets is_active = 0
        call_args = mock_db_manager.execute_non_query.call_args[0]
        assert "UPDATE sub_job_types" in call_args[0]
        assert "is_active = 0" in call_args[0]
        assert "updated_date = GETDATE()" in call_args[0]
        assert call_args[1] == (1,)

    def test_activate(self, sub_job_repo, mock_db_manager):
        """Test reactivating a sub job"""
        mock_db_manager.execute_non_query.return_value = 1

        rowcount = sub_job_repo.activate(1)

        assert rowcount == 1
        mock_db_manager.execute_non_query.assert_called_once()

        # Verify UPDATE query sets is_active = 1
        call_args = mock_db_manager.execute_non_query.call_args[0]
        assert "is_active = 1" in call_args[0]
        assert "updated_date = GETDATE()" in call_args[0]


@pytest.mark.unit
@pytest.mark.database
class TestSubJobRepositoryCount:
    """Test counting sub jobs"""

    def test_get_active_count_all(self, sub_job_repo, mock_db_manager):
        """Test getting count of all active sub jobs"""
        mock_db_manager.execute_query.return_value = [{'count': 10}]

        count = sub_job_repo.get_active_count()

        assert count == 10
        mock_db_manager.execute_query.assert_called_once()

        # Verify query counts only active records
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "WHERE is_active = 1" in call_args[0]

    def test_get_active_count_by_main_job(self, sub_job_repo, mock_db_manager):
        """Test getting count of active sub jobs for a main job"""
        mock_db_manager.execute_query.return_value = [{'count': 5}]

        count = sub_job_repo.get_active_count(main_job_id=1)

        assert count == 5

        # Verify query filters by main_job_id
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "main_job_id = ?" in call_args[0]
        assert "is_active = 1" in call_args[0]
        assert call_args[1] == (1,)


@pytest.mark.unit
@pytest.mark.database
class TestSubJobRepositoryAdvanced:
    """Test advanced sub job operations"""

    def test_get_all_active(self, sub_job_repo, mock_db_manager):
        """Test getting all active sub jobs across all main jobs"""
        mock_db_manager.execute_query.return_value = [
            {'id': 1, 'main_job_id': 1, 'sub_job_name': 'Receiving', 'description': 'Receive items'},
            {'id': 2, 'main_job_id': 2, 'sub_job_name': 'Picking', 'description': 'Pick items'},
            {'id': 3, 'main_job_id': 1, 'sub_job_name': 'Putaway', 'description': 'Store items'}
        ]

        results = sub_job_repo.get_all_active()

        assert len(results) == 3
        assert results[0]['sub_job_name'] == 'Receiving'
        assert results[1]['main_job_id'] == 2
        mock_db_manager.execute_query.assert_called_once()

        # Verify query filters by is_active and orders by sub_job_name
        call_args = mock_db_manager.execute_query.call_args[0]
        assert "WHERE is_active = 1" in call_args[0]
        assert "ORDER BY sub_job_name" in call_args[0]

    def test_get_all_active_empty(self, sub_job_repo, mock_db_manager):
        """Test getting all active sub jobs when none exist"""
        mock_db_manager.execute_query.return_value = []

        results = sub_job_repo.get_all_active()

        assert len(results) == 0

    def test_update_sub_job(self, sub_job_repo, mock_db_manager):
        """Test updating a sub job's name and description"""
        mock_db_manager.execute_non_query.return_value = 1

        rowcount = sub_job_repo.update_sub_job(
            sub_job_id=5,
            sub_job_name='New Name',
            description='New Description'
        )

        assert rowcount == 1
        mock_db_manager.execute_non_query.assert_called_once()

        # Verify UPDATE query
        call_args = mock_db_manager.execute_non_query.call_args[0]
        assert "UPDATE sub_job_types" in call_args[0]
        assert "SET sub_job_name = ?" in call_args[0]
        assert "description = ?" in call_args[0]
        assert "updated_date = GETDATE()" in call_args[0]
        assert "WHERE id = ?" in call_args[0]
        assert call_args[1] == ('New Name', 'New Description', 5)

    def test_update_sub_job_no_description(self, sub_job_repo, mock_db_manager):
        """Test updating sub job without description"""
        mock_db_manager.execute_non_query.return_value = 1

        rowcount = sub_job_repo.update_sub_job(
            sub_job_id=3,
            sub_job_name='Updated Name'
        )

        assert rowcount == 1
        call_args = mock_db_manager.execute_non_query.call_args[0]
        assert call_args[1] == ('Updated Name', '', 3)


@pytest.mark.unit
@pytest.mark.database
class TestSubJobRepositoryTableManagement:
    """Test table creation and management"""

    def test_ensure_table_exists_success(self, sub_job_repo, mock_db_manager):
        """Test table creation succeeds"""
        mock_db_manager.execute_non_query.return_value = 0

        result = sub_job_repo.ensure_table_exists()

        assert result is True
        mock_db_manager.execute_non_query.assert_called_once()

        # Verify CREATE TABLE query
        call_args = mock_db_manager.execute_non_query.call_args[0]
        assert "CREATE TABLE sub_job_types" in call_args[0]
        assert "main_job_id INT NOT NULL" in call_args[0]
        assert "is_active BIT DEFAULT 1" in call_args[0]
        assert "FOREIGN KEY (main_job_id) REFERENCES job_types(id)" in call_args[0]

    def test_ensure_table_exists_failure(self, sub_job_repo, mock_db_manager):
        """Test table creation fails gracefully"""
        mock_db_manager.execute_non_query.side_effect = Exception("Database error")

        result = sub_job_repo.ensure_table_exists()

        assert result is False
