"""
Tests for ScanService class

This module tests the scan service business logic including:
- Scan processing workflow
- Input validation
- Duplicate checking
- Dependency verification
- Error handling
"""
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_scan_log_repo():
    """Mock ScanLogRepository for testing"""
    return MagicMock()


@pytest.fixture
def mock_sub_job_repo():
    """Mock SubJobRepository for testing"""
    return MagicMock()


@pytest.fixture
def mock_dependency_repo():
    """Mock DependencyRepository for testing"""
    return MagicMock()


@pytest.fixture
def scan_service(mock_scan_log_repo, mock_sub_job_repo, mock_dependency_repo):
    """Create ScanService instance with mocked repositories"""
    from src.services.scan_service import ScanService
    return ScanService(mock_scan_log_repo, mock_sub_job_repo, mock_dependency_repo)


@pytest.mark.unit
@pytest.mark.services
class TestScanServiceInitialization:
    """Test ScanService initialization"""

    def test_init(self, scan_service, mock_scan_log_repo, mock_sub_job_repo, mock_dependency_repo):
        """Test that ScanService initializes correctly"""
        assert scan_service.scan_log_repo == mock_scan_log_repo
        assert scan_service.sub_job_repo == mock_sub_job_repo
        assert scan_service.dependency_repo == mock_dependency_repo


@pytest.mark.unit
@pytest.mark.services
class TestScanServiceValidation:
    """Test input validation"""

    def test_validate_input_success(self, scan_service):
        """Test validation passes with valid input"""
        result = scan_service._validate_input("BARCODE123", "Inbound", "Receiving")
        assert result['success'] is True
        assert result['message'] == 'Validation passed'

    def test_validate_input_no_barcode(self, scan_service):
        """Test validation fails with no barcode"""
        result = scan_service._validate_input("", "Inbound", "Receiving")
        assert result['success'] is False
        assert 'บาร์โค้ด' in result['message']

    def test_validate_input_whitespace_barcode(self, scan_service):
        """Test validation fails with whitespace-only barcode"""
        result = scan_service._validate_input("   ", "Inbound", "Receiving")
        assert result['success'] is False
        assert 'บาร์โค้ด' in result['message']

    def test_validate_input_no_job_type(self, scan_service):
        """Test validation fails with no job type"""
        result = scan_service._validate_input("BARCODE123", "", "Receiving")
        assert result['success'] is False
        assert 'งานหลัก' in result['message']

    def test_validate_input_no_sub_job_type(self, scan_service):
        """Test validation fails with no sub job type"""
        result = scan_service._validate_input("BARCODE123", "Inbound", "")
        assert result['success'] is False
        assert 'งานย่อย' in result['message']


@pytest.mark.unit
@pytest.mark.services
class TestScanServiceDuplicateCheck:
    """Test duplicate checking"""

    def test_check_duplicate_not_found(self, scan_service, mock_scan_log_repo):
        """Test no duplicate found"""
        mock_scan_log_repo.check_duplicate.return_value = None

        result = scan_service._check_duplicate("BARCODE123", 1, 10)

        assert result['success'] is True
        mock_scan_log_repo.check_duplicate.assert_called_once_with(
            barcode="BARCODE123",
            job_id=1,
            hours=24*365
        )

    def test_check_duplicate_found_same_sub_job(self, scan_service, mock_scan_log_repo):
        """Test duplicate found with same sub job"""
        existing_scan = {
            'id': 123,
            'barcode': 'BARCODE123',
            'job_id': 1,
            'sub_job_id': 10,
            'scan_date': '2024-01-01 10:00:00'
        }
        mock_scan_log_repo.check_duplicate.return_value = existing_scan

        result = scan_service._check_duplicate("BARCODE123", 1, 10)

        assert result['success'] is False
        assert 'ซ้ำ' in result['message']
        assert result['data']['duplicate_info'] == existing_scan

    def test_check_duplicate_found_different_sub_job(self, scan_service, mock_scan_log_repo):
        """Test duplicate found but different sub job - should allow"""
        existing_scan = {
            'id': 123,
            'barcode': 'BARCODE123',
            'job_id': 1,
            'sub_job_id': 11,  # Different sub job
            'scan_date': '2024-01-01 10:00:00'
        }
        mock_scan_log_repo.check_duplicate.return_value = existing_scan

        result = scan_service._check_duplicate("BARCODE123", 1, 10)

        assert result['success'] is True

    def test_check_duplicate_error(self, scan_service, mock_scan_log_repo):
        """Test duplicate check handles errors"""
        mock_scan_log_repo.check_duplicate.side_effect = Exception("Database error")

        result = scan_service._check_duplicate("BARCODE123", 1, 10)

        assert result['success'] is False
        assert 'ตรวจสอบข้อมูลซ้ำ' in result['message']


@pytest.mark.unit
@pytest.mark.services
class TestScanServiceDependencyCheck:
    """Test dependency checking"""

    def test_check_dependencies_no_dependencies(self, scan_service, mock_dependency_repo):
        """Test when job has no dependencies"""
        mock_dependency_repo.get_required_jobs.return_value = []

        result = scan_service._check_dependencies("BARCODE123", 1)

        assert result['success'] is True

    def test_check_dependencies_all_satisfied(self, scan_service, mock_dependency_repo, mock_scan_log_repo):
        """Test when all dependencies are satisfied"""
        mock_dependency_repo.get_required_jobs.return_value = [
            {'required_job_id': 2, 'job_name': 'Inbound'},
            {'required_job_id': 3, 'job_name': 'QC'}
        ]

        # Both required jobs have been scanned
        mock_scan_log_repo.check_duplicate.side_effect = [
            {'id': 1, 'barcode': 'BARCODE123', 'job_id': 2},  # Inbound found
            {'id': 2, 'barcode': 'BARCODE123', 'job_id': 3}   # QC found
        ]

        result = scan_service._check_dependencies("BARCODE123", 1)

        assert result['success'] is True
        assert mock_scan_log_repo.check_duplicate.call_count == 2

    def test_check_dependencies_one_missing(self, scan_service, mock_dependency_repo, mock_scan_log_repo):
        """Test when one dependency is missing"""
        mock_dependency_repo.get_required_jobs.return_value = [
            {'required_job_id': 2, 'job_name': 'Inbound'},
            {'required_job_id': 3, 'job_name': 'QC'}
        ]

        # First job found, second job missing
        mock_scan_log_repo.check_duplicate.side_effect = [
            {'id': 1, 'barcode': 'BARCODE123', 'job_id': 2},  # Inbound found
            None  # QC not found
        ]

        result = scan_service._check_dependencies("BARCODE123", 1)

        assert result['success'] is False
        assert 'QC' in result['message']
        assert len(result['data']['missing_dependencies']) == 1
        assert result['data']['missing_dependencies'][0]['job_name'] == 'QC'

    def test_check_dependencies_multiple_missing(self, scan_service, mock_dependency_repo, mock_scan_log_repo):
        """Test when multiple dependencies are missing"""
        mock_dependency_repo.get_required_jobs.return_value = [
            {'required_job_id': 2, 'job_name': 'Inbound'},
            {'required_job_id': 3, 'job_name': 'QC'},
            {'required_job_id': 4, 'job_name': 'Putaway'}
        ]

        # All jobs missing
        mock_scan_log_repo.check_duplicate.side_effect = [None, None, None]

        result = scan_service._check_dependencies("BARCODE123", 1)

        assert result['success'] is False
        assert len(result['data']['missing_dependencies']) == 3

    def test_check_dependencies_error(self, scan_service, mock_dependency_repo):
        """Test dependency check handles errors"""
        mock_dependency_repo.get_required_jobs.side_effect = Exception("Database error")

        result = scan_service._check_dependencies("BARCODE123", 1)

        assert result['success'] is False
        assert 'dependencies' in result['message']


@pytest.mark.unit
@pytest.mark.services
class TestScanServiceProcessScan:
    """Test full scan processing workflow"""

    def test_process_scan_success(
        self, scan_service, mock_scan_log_repo, mock_sub_job_repo, mock_dependency_repo
    ):
        """Test successful scan processing"""
        # Setup mocks
        mock_sub_job_repo.find_by_name.return_value = {'id': 10, 'sub_job_name': 'Receiving'}
        mock_scan_log_repo.check_duplicate.side_effect = [None, None]  # No duplicate, no dependencies
        mock_dependency_repo.get_required_jobs.return_value = []
        mock_scan_log_repo.create_scan.return_value = 1

        result = scan_service.process_scan(
            barcode="BARCODE123",
            job_type_name="Inbound",
            job_id=1,
            sub_job_type_name="Receiving",
            user_id="user1",
            notes="Test notes"
        )

        assert result['success'] is True
        assert 'สำเร็จ' in result['message']
        assert result['data']['barcode'] == "BARCODE123"
        mock_scan_log_repo.create_scan.assert_called_once()

    def test_process_scan_validation_failed(self, scan_service):
        """Test scan fails validation"""
        result = scan_service.process_scan(
            barcode="",
            job_type_name="Inbound",
            job_id=1,
            sub_job_type_name="Receiving",
            user_id="user1"
        )

        assert result['success'] is False
        assert 'บาร์โค้ด' in result['message']

    def test_process_scan_sub_job_not_found(self, scan_service, mock_sub_job_repo):
        """Test scan fails when sub job not found"""
        mock_sub_job_repo.find_by_name.return_value = None

        result = scan_service.process_scan(
            barcode="BARCODE123",
            job_type_name="Inbound",
            job_id=1,
            sub_job_type_name="NonExistent",
            user_id="user1"
        )

        assert result['success'] is False
        assert 'ไม่พบประเภทงานย่อย' in result['message']

    def test_process_scan_duplicate_found(
        self, scan_service, mock_scan_log_repo, mock_sub_job_repo
    ):
        """Test scan fails when duplicate found"""
        mock_sub_job_repo.find_by_name.return_value = {'id': 10, 'sub_job_name': 'Receiving'}
        mock_scan_log_repo.check_duplicate.return_value = {
            'id': 123,
            'barcode': 'BARCODE123',
            'job_id': 1,
            'sub_job_id': 10
        }

        result = scan_service.process_scan(
            barcode="BARCODE123",
            job_type_name="Inbound",
            job_id=1,
            sub_job_type_name="Receiving",
            user_id="user1"
        )

        assert result['success'] is False
        assert 'ซ้ำ' in result['message']
        assert 'duplicate_info' in result['data']

    def test_process_scan_dependencies_not_satisfied(
        self, scan_service, mock_scan_log_repo, mock_sub_job_repo, mock_dependency_repo
    ):
        """Test scan fails when dependencies not satisfied"""
        mock_sub_job_repo.find_by_name.return_value = {'id': 10, 'sub_job_name': 'Receiving'}
        mock_scan_log_repo.check_duplicate.side_effect = [
            None,  # No duplicate
            None   # Required job not found
        ]
        mock_dependency_repo.get_required_jobs.return_value = [
            {'required_job_id': 2, 'job_name': 'Inbound'}
        ]

        result = scan_service.process_scan(
            barcode="BARCODE123",
            job_type_name="Outbound",
            job_id=3,
            sub_job_type_name="Picking",
            user_id="user1"
        )

        assert result['success'] is False
        assert 'Inbound' in result['message']
        assert 'missing_dependencies' in result['data']

    def test_process_scan_save_error(
        self, scan_service, mock_scan_log_repo, mock_sub_job_repo, mock_dependency_repo
    ):
        """Test scan handles save errors"""
        mock_sub_job_repo.find_by_name.return_value = {'id': 10, 'sub_job_name': 'Receiving'}
        mock_scan_log_repo.check_duplicate.return_value = None
        mock_dependency_repo.get_required_jobs.return_value = []
        mock_scan_log_repo.create_scan.side_effect = Exception("Database error")

        result = scan_service.process_scan(
            barcode="BARCODE123",
            job_type_name="Inbound",
            job_id=1,
            sub_job_type_name="Receiving",
            user_id="user1"
        )

        assert result['success'] is False
        assert 'บันทึก' in result['message']
