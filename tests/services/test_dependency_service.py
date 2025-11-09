"""
Tests for DependencyService class

This module tests the dependency service business logic including:
- Adding dependencies with validation
- Removing dependencies
- Checking circular dependencies
- Getting dependencies with scan status
- Batch operations
"""
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_dependency_repo():
    """Mock DependencyRepository for testing"""
    return MagicMock()


@pytest.fixture
def mock_job_type_repo():
    """Mock JobTypeRepository for testing"""
    return MagicMock()


@pytest.fixture
def dependency_service(mock_dependency_repo, mock_job_type_repo):
    """Create DependencyService instance with mocked repositories"""
    from src.services.dependency_service import DependencyService
    return DependencyService(mock_dependency_repo, mock_job_type_repo)


@pytest.mark.unit
@pytest.mark.services
class TestDependencyServiceInitialization:
    """Test DependencyService initialization"""

    def test_init(self, dependency_service, mock_dependency_repo, mock_job_type_repo):
        """Test that DependencyService initializes correctly"""
        assert dependency_service.dependency_repo == mock_dependency_repo
        assert dependency_service.job_type_repo == mock_job_type_repo


@pytest.mark.unit
@pytest.mark.services
class TestDependencyServiceAddDependency:
    """Test adding dependencies"""

    def test_add_dependency_success(
        self, dependency_service, mock_dependency_repo, mock_job_type_repo
    ):
        """Test successfully adding a dependency"""
        # Setup mocks
        mock_job_type_repo.find_by_id.side_effect = [
            {'id': 1, 'job_name': 'Job1'},  # Main job
            {'id': 2, 'job_name': 'Job2'}   # Required job
        ]
        mock_dependency_repo.dependency_exists.return_value = False
        mock_dependency_repo.validate_no_circular_dependency.return_value = True
        mock_dependency_repo.add_dependency.return_value = 1

        result = dependency_service.add_dependency(1, 2)

        assert result['success'] is True
        assert 'added successfully' in result['message']
        mock_dependency_repo.add_dependency.assert_called_once_with(1, 2)

    def test_add_dependency_job_not_found(
        self, dependency_service, mock_job_type_repo
    ):
        """Test adding dependency when main job doesn't exist"""
        mock_job_type_repo.find_by_id.return_value = None

        result = dependency_service.add_dependency(999, 2)

        assert result['success'] is False
        assert 'not found' in result['message']

    def test_add_dependency_required_job_not_found(
        self, dependency_service, mock_job_type_repo
    ):
        """Test adding dependency when required job doesn't exist"""
        mock_job_type_repo.find_by_id.side_effect = [
            {'id': 1, 'job_name': 'Job1'},  # Main job exists
            None  # Required job doesn't exist
        ]

        result = dependency_service.add_dependency(1, 999)

        assert result['success'] is False
        assert 'not found' in result['message']

    def test_add_dependency_to_itself(
        self, dependency_service, mock_job_type_repo
    ):
        """Test adding dependency to itself"""
        mock_job_type_repo.find_by_id.side_effect = [
            {'id': 1, 'job_name': 'Job1'},
            {'id': 1, 'job_name': 'Job1'}
        ]

        result = dependency_service.add_dependency(1, 1)

        assert result['success'] is False
        assert 'itself' in result['message']

    def test_add_dependency_already_exists(
        self, dependency_service, mock_dependency_repo, mock_job_type_repo
    ):
        """Test adding dependency that already exists"""
        mock_job_type_repo.find_by_id.side_effect = [
            {'id': 1, 'job_name': 'Job1'},
            {'id': 2, 'job_name': 'Job2'}
        ]
        mock_dependency_repo.dependency_exists.return_value = True

        result = dependency_service.add_dependency(1, 2)

        assert result['success'] is False
        assert 'already exists' in result['message']

    def test_add_dependency_circular_reference(
        self, dependency_service, mock_dependency_repo, mock_job_type_repo
    ):
        """Test adding dependency that would create circular reference"""
        mock_job_type_repo.find_by_id.side_effect = [
            {'id': 1, 'job_name': 'Job1'},
            {'id': 2, 'job_name': 'Job2'}
        ]
        mock_dependency_repo.dependency_exists.return_value = False
        mock_dependency_repo.validate_no_circular_dependency.return_value = False

        result = dependency_service.add_dependency(1, 2)

        assert result['success'] is False
        assert 'circular' in result['message']

    def test_add_dependency_error(
        self, dependency_service, mock_dependency_repo, mock_job_type_repo
    ):
        """Test adding dependency handles errors"""
        mock_job_type_repo.find_by_id.side_effect = [
            {'id': 1, 'job_name': 'Job1'},
            {'id': 2, 'job_name': 'Job2'}
        ]
        mock_dependency_repo.dependency_exists.return_value = False
        mock_dependency_repo.validate_no_circular_dependency.return_value = True
        mock_dependency_repo.add_dependency.side_effect = Exception("Database error")

        result = dependency_service.add_dependency(1, 2)

        assert result['success'] is False
        assert 'Error' in result['message']


@pytest.mark.unit
@pytest.mark.services
class TestDependencyServiceRemoveDependency:
    """Test removing dependencies"""

    def test_remove_dependency_success(
        self, dependency_service, mock_dependency_repo
    ):
        """Test successfully removing a dependency"""
        mock_dependency_repo.remove_dependency.return_value = 1

        result = dependency_service.remove_dependency(1, 2)

        assert result['success'] is True
        assert 'removed successfully' in result['message']
        mock_dependency_repo.remove_dependency.assert_called_once_with(1, 2)

    def test_remove_dependency_not_found(
        self, dependency_service, mock_dependency_repo
    ):
        """Test removing dependency that doesn't exist"""
        mock_dependency_repo.remove_dependency.return_value = 0

        result = dependency_service.remove_dependency(1, 2)

        assert result['success'] is False
        assert 'not found' in result['message']

    def test_remove_dependency_error(
        self, dependency_service, mock_dependency_repo
    ):
        """Test removing dependency handles errors"""
        mock_dependency_repo.remove_dependency.side_effect = Exception("Database error")

        result = dependency_service.remove_dependency(1, 2)

        assert result['success'] is False
        assert 'Error' in result['message']


@pytest.mark.unit
@pytest.mark.services
class TestDependencyServiceRemoveAllDependencies:
    """Test removing all dependencies for a job"""

    def test_remove_all_dependencies_success(
        self, dependency_service, mock_dependency_repo
    ):
        """Test successfully removing all dependencies"""
        mock_dependency_repo.remove_all_dependencies.return_value = 3

        result = dependency_service.remove_all_dependencies(1)

        assert result['success'] is True
        assert '3 dependencies' in result['message']
        assert result['data']['dependencies_removed'] == 3

    def test_remove_all_dependencies_none(
        self, dependency_service, mock_dependency_repo
    ):
        """Test removing all dependencies when there are none"""
        mock_dependency_repo.remove_all_dependencies.return_value = 0

        result = dependency_service.remove_all_dependencies(1)

        assert result['success'] is True
        assert '0 dependencies' in result['message']

    def test_remove_all_dependencies_error(
        self, dependency_service, mock_dependency_repo
    ):
        """Test removing all dependencies handles errors"""
        mock_dependency_repo.remove_all_dependencies.side_effect = Exception("Database error")

        result = dependency_service.remove_all_dependencies(1)

        assert result['success'] is False
        assert 'Error' in result['message']


@pytest.mark.unit
@pytest.mark.services
class TestDependencyServiceGetRequiredJobs:
    """Test getting required jobs"""

    def test_get_required_jobs_without_scan_status(
        self, dependency_service, mock_dependency_repo
    ):
        """Test getting required jobs without scan status"""
        mock_dependency_repo.get_required_jobs.return_value = [
            {'required_job_id': 2, 'job_name': 'Job2'},
            {'required_job_id': 3, 'job_name': 'Job3'}
        ]

        result = dependency_service.get_required_jobs(1, include_scan_status=False)

        assert result['success'] is True
        assert result['data']['count'] == 2
        assert len(result['data']['required_jobs']) == 2
        mock_dependency_repo.get_required_jobs.assert_called_once_with(1)

    def test_get_required_jobs_with_scan_status(
        self, dependency_service, mock_dependency_repo
    ):
        """Test getting required jobs with scan status"""
        mock_dependency_repo.get_required_job_with_scan_status.return_value = [
            {'required_job_id': 2, 'job_name': 'Job2', 'scan_count': 5},
            {'required_job_id': 3, 'job_name': 'Job3', 'scan_count': 0}
        ]

        result = dependency_service.get_required_jobs(
            1, include_scan_status=True, check_today_only=True
        )

        assert result['success'] is True
        assert result['data']['count'] == 2
        mock_dependency_repo.get_required_job_with_scan_status.assert_called_once_with(1, True)

    def test_get_required_jobs_error(
        self, dependency_service, mock_dependency_repo
    ):
        """Test getting required jobs handles errors"""
        mock_dependency_repo.get_required_jobs.side_effect = Exception("Database error")

        result = dependency_service.get_required_jobs(1)

        assert result['success'] is False
        assert 'Error' in result['message']


@pytest.mark.unit
@pytest.mark.services
class TestDependencyServiceSaveDependencies:
    """Test batch saving dependencies"""

    def test_save_dependencies_success(
        self, dependency_service, mock_dependency_repo
    ):
        """Test successfully saving dependencies"""
        mock_dependency_repo.remove_all_dependencies.return_value = 2
        mock_dependency_repo.validate_no_circular_dependency.return_value = True
        mock_dependency_repo.add_dependency.return_value = 1

        result = dependency_service.save_dependencies(1, [2, 3, 4])

        assert result['success'] is True
        assert result['data']['dependencies_added'] == 3
        assert len(result['data']['errors']) == 0
        assert mock_dependency_repo.add_dependency.call_count == 3

    def test_save_dependencies_with_circular(
        self, dependency_service, mock_dependency_repo
    ):
        """Test saving dependencies with circular dependency detected"""
        mock_dependency_repo.remove_all_dependencies.return_value = 0
        mock_dependency_repo.validate_no_circular_dependency.side_effect = [True, False, True]
        mock_dependency_repo.add_dependency.return_value = 1

        result = dependency_service.save_dependencies(1, [2, 3, 4])

        assert result['success'] is False  # Has errors
        assert result['data']['dependencies_added'] == 2  # Only 2 added (skipped circular)
        assert len(result['data']['errors']) == 1
        assert 'Circular' in result['data']['errors'][0]

    def test_save_dependencies_empty_list(
        self, dependency_service, mock_dependency_repo
    ):
        """Test saving empty dependencies list"""
        mock_dependency_repo.remove_all_dependencies.return_value = 2

        result = dependency_service.save_dependencies(1, [])

        assert result['success'] is True
        assert result['data']['dependencies_added'] == 0
        mock_dependency_repo.remove_all_dependencies.assert_called_once_with(1)

    def test_save_dependencies_error(
        self, dependency_service, mock_dependency_repo
    ):
        """Test saving dependencies handles errors"""
        mock_dependency_repo.remove_all_dependencies.side_effect = Exception("Database error")

        result = dependency_service.save_dependencies(1, [2, 3])

        assert result['success'] is False
        assert 'Error' in result['message']


@pytest.mark.unit
@pytest.mark.services
class TestDependencyServiceGetAllDependencies:
    """Test getting all dependencies"""

    def test_get_all_dependencies_success(
        self, dependency_service, mock_dependency_repo
    ):
        """Test getting all dependencies"""
        mock_dependency_repo.get_all_dependencies.return_value = [
            {'id': 1, 'job_id': 3, 'job_name': 'Job3', 'required_job_id': 1, 'required_job_name': 'Job1'},
            {'id': 2, 'job_id': 3, 'job_name': 'Job3', 'required_job_id': 2, 'required_job_name': 'Job2'}
        ]

        result = dependency_service.get_all_dependencies()

        assert result['success'] is True
        assert result['data']['count'] == 2
        assert len(result['data']['dependencies']) == 2

    def test_get_all_dependencies_empty(
        self, dependency_service, mock_dependency_repo
    ):
        """Test getting all dependencies when none exist"""
        mock_dependency_repo.get_all_dependencies.return_value = []

        result = dependency_service.get_all_dependencies()

        assert result['success'] is True
        assert result['data']['count'] == 0

    def test_get_all_dependencies_error(
        self, dependency_service, mock_dependency_repo
    ):
        """Test getting all dependencies handles errors"""
        mock_dependency_repo.get_all_dependencies.side_effect = Exception("Database error")

        result = dependency_service.get_all_dependencies()

        assert result['success'] is False
        assert 'Error' in result['message']
