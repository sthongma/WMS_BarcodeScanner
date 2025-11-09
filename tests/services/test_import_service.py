"""
Tests for ImportService class

This module tests the import service business logic including:
- Data validation (structure and content)
- Row-level validation
- Bulk import operations
- Template data generation
"""
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_job_type_repo():
    """Mock JobTypeRepository for testing"""
    return MagicMock()


@pytest.fixture
def mock_sub_job_repo():
    """Mock SubJobRepository for testing"""
    return MagicMock()


@pytest.fixture
def mock_scan_log_repo():
    """Mock ScanLogRepository for testing"""
    return MagicMock()


@pytest.fixture
def import_service(mock_job_type_repo, mock_sub_job_repo, mock_scan_log_repo):
    """Create ImportService instance with mocked repositories"""
    from src.services.import_service import ImportService
    return ImportService(mock_job_type_repo, mock_sub_job_repo, mock_scan_log_repo)


@pytest.fixture
def sample_import_data():
    """Sample import data for testing"""
    return [
        {
            'barcode': 'BC001',
            'main_job_id': '1',
            'sub_job_id': '10',
            'notes': 'Test note 1'
        },
        {
            'barcode': 'BC002',
            'main_job_id': '1',
            'sub_job_id': '10',
            'notes': 'Test note 2'
        },
        {
            'barcode': 'BC003',
            'main_job_id': '2',
            'sub_job_id': '20',
            'notes': ''
        }
    ]


@pytest.mark.unit
@pytest.mark.services
class TestImportServiceInitialization:
    """Test ImportService initialization"""

    def test_init(
        self, import_service, mock_job_type_repo,
        mock_sub_job_repo, mock_scan_log_repo
    ):
        """Test that ImportService initializes correctly"""
        assert import_service.job_type_repo == mock_job_type_repo
        assert import_service.sub_job_repo == mock_sub_job_repo
        assert import_service.scan_log_repo == mock_scan_log_repo


@pytest.mark.unit
@pytest.mark.services
class TestImportServiceValidateData:
    """Test import data validation"""

    def test_validate_import_data_success(
        self, import_service, sample_import_data,
        mock_job_type_repo, mock_sub_job_repo
    ):
        """Test successful validation of import data"""
        # Setup mocks to handle multiple job IDs
        def find_job_by_id(job_id):
            jobs = {
                1: {'id': 1, 'job_name': 'Inbound'},
                2: {'id': 2, 'job_name': 'Outbound'}
            }
            return jobs.get(job_id)

        def get_sub_job_details(sub_job_id):
            sub_jobs = {
                10: {'id': 10, 'sub_job_name': 'Receiving', 'main_job_id': 1, 'is_active': True},
                20: {'id': 20, 'sub_job_name': 'Picking', 'main_job_id': 2, 'is_active': True}
            }
            return sub_jobs.get(sub_job_id)

        mock_job_type_repo.find_by_id.side_effect = find_job_by_id
        mock_sub_job_repo.get_details.side_effect = get_sub_job_details

        result = import_service.validate_import_data(sample_import_data)

        assert result['success'] is True
        assert result['data']['valid_rows'] == 3
        assert result['data']['invalid_rows'] == 0
        assert result['data']['total_rows'] == 3
        assert result['data']['all_valid'] is True

    def test_validate_import_data_empty(self, import_service):
        """Test validation with empty data"""
        result = import_service.validate_import_data([])

        assert result['success'] is False
        assert 'ไม่มีข้อมูล' in result['message']
        assert result['data']['total_rows'] == 0

    def test_validate_import_data_with_errors(
        self, import_service, mock_job_type_repo, mock_sub_job_repo
    ):
        """Test validation with some invalid rows"""
        data = [
            {'barcode': 'BC001', 'main_job_id': '1', 'sub_job_id': '10'},  # Valid
            {'barcode': '', 'main_job_id': '1', 'sub_job_id': '10'},  # Missing barcode
            {'barcode': 'BC003', 'main_job_id': 'invalid', 'sub_job_id': '10'},  # Invalid ID
        ]

        # Mock for valid row only
        mock_job_type_repo.find_by_id.return_value = {'id': 1, 'job_name': 'Inbound'}
        mock_sub_job_repo.get_details.return_value = {
            'id': 10,
            'sub_job_name': 'Receiving',
            'main_job_id': 1,
            'is_active': True
        }

        result = import_service.validate_import_data(data)

        assert result['success'] is False
        assert result['data']['valid_rows'] == 1
        assert result['data']['invalid_rows'] == 2


@pytest.mark.unit
@pytest.mark.services
class TestImportServiceValidateRow:
    """Test single row validation"""

    def test_validate_row_success(
        self, import_service, mock_job_type_repo, mock_sub_job_repo
    ):
        """Test successful row validation"""
        row = {
            'barcode': 'BC001',
            'main_job_id': '1',
            'sub_job_id': '10',
            'notes': 'Test'
        }

        mock_job_type_repo.find_by_id.return_value = {'id': 1, 'job_name': 'Inbound'}
        mock_sub_job_repo.get_details.return_value = {
            'id': 10,
            'sub_job_name': 'Receiving',
            'main_job_id': 1,
            'is_active': True
        }

        result = import_service.validate_import_row(row, 1)

        assert result['valid'] is True
        assert result['row_number'] == 1
        assert len(result['errors']) == 0
        assert 'validated_data' in result
        assert result['validated_data']['barcode'] == 'BC001'

    def test_validate_row_missing_barcode(self, import_service):
        """Test validation with missing barcode"""
        row = {
            'barcode': '',
            'main_job_id': '1',
            'sub_job_id': '10'
        }

        result = import_service.validate_import_row(row, 1)

        assert result['valid'] is False
        assert any('บาร์โค้ด' in error for error in result['errors'])

    def test_validate_row_missing_main_job_id(self, import_service):
        """Test validation with missing main job ID"""
        row = {
            'barcode': 'BC001',
            'main_job_id': '',
            'sub_job_id': '10'
        }

        result = import_service.validate_import_row(row, 1)

        assert result['valid'] is False
        assert any('ประเภทงานหลัก' in error for error in result['errors'])

    def test_validate_row_invalid_main_job_id(self, import_service):
        """Test validation with invalid main job ID format"""
        row = {
            'barcode': 'BC001',
            'main_job_id': 'invalid',
            'sub_job_id': '10'
        }

        result = import_service.validate_import_row(row, 1)

        assert result['valid'] is False
        assert any('ไม่ถูกต้อง' in error for error in result['errors'])

    def test_validate_row_job_not_found(
        self, import_service, mock_job_type_repo
    ):
        """Test validation when job type not found"""
        row = {
            'barcode': 'BC001',
            'main_job_id': '999',
            'sub_job_id': '10'
        }

        mock_job_type_repo.find_by_id.return_value = None

        result = import_service.validate_import_row(row, 1)

        assert result['valid'] is False
        assert any('ไม่พบประเภทงานหลัก' in error for error in result['errors'])

    def test_validate_row_sub_job_not_found(
        self, import_service, mock_job_type_repo, mock_sub_job_repo
    ):
        """Test validation when sub job not found"""
        row = {
            'barcode': 'BC001',
            'main_job_id': '1',
            'sub_job_id': '999'
        }

        mock_job_type_repo.find_by_id.return_value = {'id': 1, 'job_name': 'Inbound'}
        mock_sub_job_repo.get_details.return_value = None

        result = import_service.validate_import_row(row, 1)

        assert result['valid'] is False
        assert any('ไม่พบประเภทงานย่อย' in error for error in result['errors'])

    def test_validate_row_sub_job_inactive(
        self, import_service, mock_job_type_repo, mock_sub_job_repo
    ):
        """Test validation when sub job is inactive"""
        row = {
            'barcode': 'BC001',
            'main_job_id': '1',
            'sub_job_id': '10'
        }

        mock_job_type_repo.find_by_id.return_value = {'id': 1, 'job_name': 'Inbound'}
        mock_sub_job_repo.get_details.return_value = {
            'id': 10,
            'sub_job_name': 'Receiving',
            'main_job_id': 1,
            'is_active': False  # Inactive
        }

        result = import_service.validate_import_row(row, 1)

        assert result['valid'] is False
        assert any('ปิดการใช้งาน' in error for error in result['errors'])

    def test_validate_row_sub_job_wrong_main_job(
        self, import_service, mock_job_type_repo, mock_sub_job_repo
    ):
        """Test validation when sub job doesn't belong to main job"""
        row = {
            'barcode': 'BC001',
            'main_job_id': '1',
            'sub_job_id': '10'
        }

        mock_job_type_repo.find_by_id.return_value = {'id': 1, 'job_name': 'Inbound'}
        mock_sub_job_repo.get_details.return_value = {
            'id': 10,
            'sub_job_name': 'Receiving',
            'main_job_id': 2,  # Different main job
            'is_active': True
        }

        result = import_service.validate_import_row(row, 1)

        assert result['valid'] is False
        assert any('ไม่สัมพันธ์' in error for error in result['errors'])


@pytest.mark.unit
@pytest.mark.services
class TestImportServiceImportScans:
    """Test bulk import operations"""

    def test_import_scans_success(
        self, import_service, mock_job_type_repo, mock_scan_log_repo
    ):
        """Test successful bulk import"""
        validated_rows = [
            {
                'valid': True,
                'row_number': 1,
                'validated_data': {
                    'barcode': 'BC001',
                    'main_job_id': 1,
                    'sub_job_id': 10,
                    'notes': 'Test'
                }
            },
            {
                'valid': True,
                'row_number': 2,
                'validated_data': {
                    'barcode': 'BC002',
                    'main_job_id': 1,
                    'sub_job_id': 10,
                    'notes': ''
                }
            }
        ]

        mock_job_type_repo.find_by_id.return_value = {'id': 1, 'job_name': 'Inbound'}
        mock_scan_log_repo.create_scan.return_value = 1

        result = import_service.import_scans(validated_rows, 'user1')

        assert result['success'] is True
        assert result['data']['imported_count'] == 2
        assert result['data']['failed_count'] == 0
        assert mock_scan_log_repo.create_scan.call_count == 2

    def test_import_scans_empty(self, import_service):
        """Test import with no validated rows"""
        result = import_service.import_scans([], 'user1')

        assert result['success'] is False
        assert 'ไม่มีข้อมูล' in result['message']
        assert result['data']['imported_count'] == 0

    def test_import_scans_skip_invalid(
        self, import_service, mock_job_type_repo, mock_scan_log_repo
    ):
        """Test import skips invalid rows"""
        validated_rows = [
            {
                'valid': True,
                'row_number': 1,
                'validated_data': {
                    'barcode': 'BC001',
                    'main_job_id': 1,
                    'sub_job_id': 10,
                    'notes': ''
                }
            },
            {
                'valid': False,  # Invalid row
                'row_number': 2,
                'errors': ['Test error']
            }
        ]

        mock_job_type_repo.find_by_id.return_value = {'id': 1, 'job_name': 'Inbound'}
        mock_scan_log_repo.create_scan.return_value = 1

        result = import_service.import_scans(validated_rows, 'user1')

        assert result['success'] is False  # Not all succeeded
        assert result['data']['imported_count'] == 1
        assert result['data']['failed_count'] == 1
        assert mock_scan_log_repo.create_scan.call_count == 1

    def test_import_scans_database_error(
        self, import_service, mock_job_type_repo, mock_scan_log_repo
    ):
        """Test import handles database errors"""
        validated_rows = [
            {
                'valid': True,
                'row_number': 1,
                'validated_data': {
                    'barcode': 'BC001',
                    'main_job_id': 1,
                    'sub_job_id': 10,
                    'notes': ''
                }
            }
        ]

        mock_job_type_repo.find_by_id.return_value = {'id': 1, 'job_name': 'Inbound'}
        mock_scan_log_repo.create_scan.side_effect = Exception("Database error")

        result = import_service.import_scans(validated_rows, 'user1')

        assert result['success'] is False
        assert result['data']['imported_count'] == 0
        assert result['data']['failed_count'] == 1
        assert len(result['data']['errors']) == 1


@pytest.mark.unit
@pytest.mark.services
class TestImportServiceGenerateTemplate:
    """Test template data generation"""

    def test_generate_template_data_success(
        self, import_service, mock_job_type_repo, mock_sub_job_repo
    ):
        """Test successful template data generation"""
        mock_job_type_repo.get_all_job_types.return_value = [
            {'id': 1, 'job_name': 'Inbound'},
            {'id': 2, 'job_name': 'Outbound'}
        ]
        mock_sub_job_repo.get_all_active.return_value = [
            {'id': 10, 'sub_job_name': 'Receiving', 'main_job_id': 1},
            {'id': 20, 'sub_job_name': 'Picking', 'main_job_id': 2}
        ]

        result = import_service.generate_template_data()

        assert result['success'] is True
        assert len(result['data']['job_types']) == 2
        assert len(result['data']['sub_jobs']) == 2
        assert len(result['data']['columns']) == 4
        assert len(result['data']['sample_data']) == 1

    def test_generate_template_data_empty(
        self, import_service, mock_job_type_repo, mock_sub_job_repo
    ):
        """Test template generation with no data"""
        mock_job_type_repo.get_all_job_types.return_value = []
        mock_sub_job_repo.get_all_active.return_value = []

        result = import_service.generate_template_data()

        assert result['success'] is True
        assert len(result['data']['job_types']) == 0
        assert len(result['data']['sub_jobs']) == 0
        assert len(result['data']['sample_data']) == 0

    def test_generate_template_data_error(
        self, import_service, mock_job_type_repo
    ):
        """Test template generation handles errors"""
        mock_job_type_repo.get_all_job_types.side_effect = Exception("Database error")

        result = import_service.generate_template_data()

        assert result['success'] is False
        assert 'ไม่สามารถสร้างข้อมูล template' in result['message']
