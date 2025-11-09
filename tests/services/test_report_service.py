"""
Tests for ReportService class

This module tests the report service business logic including:
- Report generation for single date
- Report generation for date range
- Input validation
- Notes filtering
- Statistics calculation
"""
import pytest
from unittest.mock import MagicMock
from datetime import datetime


@pytest.fixture
def mock_scan_log_repo():
    """Mock ScanLogRepository for testing"""
    return MagicMock()


@pytest.fixture
def mock_job_type_repo():
    """Mock JobTypeRepository for testing"""
    return MagicMock()


@pytest.fixture
def mock_sub_job_repo():
    """Mock SubJobRepository for testing"""
    return MagicMock()


@pytest.fixture
def report_service(mock_scan_log_repo, mock_job_type_repo, mock_sub_job_repo):
    """Create ReportService instance with mocked repositories"""
    from src.services.report_service import ReportService
    return ReportService(mock_scan_log_repo, mock_job_type_repo, mock_sub_job_repo)


@pytest.fixture
def sample_scans():
    """Sample scan data for testing"""
    return [
        {
            'barcode': 'BC001',
            'scan_date': '2024-01-15 10:00:00',
            'job_id': 1,
            'sub_job_id': 10,
            'notes': 'Test note 1',
            'user_id': 'user1'
        },
        {
            'barcode': 'BC002',
            'scan_date': '2024-01-15 11:00:00',
            'job_id': 1,
            'sub_job_id': 10,
            'notes': 'Test note 2',
            'user_id': 'user1'
        },
        {
            'barcode': 'BC001',  # Duplicate barcode
            'scan_date': '2024-01-15 12:00:00',
            'job_id': 1,
            'sub_job_id': 10,
            'notes': 'Another scan',
            'user_id': 'user2'
        }
    ]


@pytest.mark.unit
@pytest.mark.services
class TestReportServiceInitialization:
    """Test ReportService initialization"""

    def test_init(self, report_service, mock_scan_log_repo, mock_job_type_repo, mock_sub_job_repo):
        """Test that ReportService initializes correctly"""
        assert report_service.scan_log_repo == mock_scan_log_repo
        assert report_service.job_type_repo == mock_job_type_repo
        assert report_service.sub_job_repo == mock_sub_job_repo


@pytest.mark.unit
@pytest.mark.services
class TestReportServiceValidation:
    """Test input validation"""

    def test_validate_inputs_success(
        self, report_service, mock_job_type_repo, mock_sub_job_repo
    ):
        """Test validation passes with valid inputs"""
        mock_job_type_repo.find_by_id.return_value = {'id': 1, 'job_name': 'Inbound'}
        mock_sub_job_repo.get_details.return_value = {
            'id': 10,
            'sub_job_name': 'Receiving',
            'main_job_id': 1
        }

        result = report_service._validate_inputs('2024-01-15', 1, 10)

        assert result['success'] is True
        assert result['message'] == 'Validation passed'

    def test_validate_inputs_no_date(self, report_service):
        """Test validation fails with no date"""
        result = report_service._validate_inputs('', 1, None)

        assert result['success'] is False
        assert 'วันที่' in result['message']

    def test_validate_inputs_job_not_found(
        self, report_service, mock_job_type_repo
    ):
        """Test validation fails when job not found"""
        mock_job_type_repo.find_by_id.return_value = None

        result = report_service._validate_inputs('2024-01-15', 999, None)

        assert result['success'] is False
        assert 'ไม่พบงานหลัก' in result['message']

    def test_validate_inputs_sub_job_not_found(
        self, report_service, mock_job_type_repo, mock_sub_job_repo
    ):
        """Test validation fails when sub job not found"""
        mock_job_type_repo.find_by_id.return_value = {'id': 1, 'job_name': 'Inbound'}
        mock_sub_job_repo.get_details.return_value = None

        result = report_service._validate_inputs('2024-01-15', 1, 999)

        assert result['success'] is False
        assert 'ไม่พบงานย่อย' in result['message']

    def test_validate_inputs_sub_job_wrong_main_job(
        self, report_service, mock_job_type_repo, mock_sub_job_repo
    ):
        """Test validation fails when sub job doesn't belong to main job"""
        mock_job_type_repo.find_by_id.return_value = {'id': 1, 'job_name': 'Inbound'}
        mock_sub_job_repo.get_details.return_value = {
            'id': 10,
            'sub_job_name': 'Receiving',
            'main_job_id': 2  # Different main job
        }

        result = report_service._validate_inputs('2024-01-15', 1, 10)

        assert result['success'] is False
        assert 'ไม่ตรงกับงานหลัก' in result['message']


@pytest.mark.unit
@pytest.mark.services
class TestReportServiceGenerateReport:
    """Test single date report generation"""

    def test_generate_report_success_with_sub_job(
        self, report_service, mock_scan_log_repo, mock_job_type_repo,
        mock_sub_job_repo, sample_scans
    ):
        """Test successful report generation with sub job filter"""
        # Setup mocks
        mock_job_type_repo.find_by_id.return_value = {'id': 1, 'job_name': 'Inbound'}
        mock_sub_job_repo.get_details.return_value = {
            'id': 10,
            'sub_job_name': 'Receiving',
            'main_job_id': 1
        }
        mock_scan_log_repo.get_report_with_sub_job.return_value = sample_scans

        result = report_service.generate_report('2024-01-15', 1, 10)

        assert result['success'] is True
        assert result['data']['statistics']['total_scans'] == 3
        assert result['data']['statistics']['unique_barcodes'] == 2  # BC001, BC002
        assert result['data']['job_name'] == 'Inbound'
        assert result['data']['sub_job_name'] == 'Receiving'
        mock_scan_log_repo.get_report_with_sub_job.assert_called_once_with(
            start_date='2024-01-15',
            end_date='2024-01-15',
            job_id=1,
            sub_job_id=10
        )

    def test_generate_report_success_without_sub_job(
        self, report_service, mock_scan_log_repo, mock_job_type_repo,
        mock_sub_job_repo, sample_scans
    ):
        """Test successful report generation without sub job filter"""
        # Setup mocks
        mock_job_type_repo.find_by_id.return_value = {'id': 1, 'job_name': 'Inbound'}
        mock_scan_log_repo.get_report_with_sub_job.return_value = sample_scans

        result = report_service.generate_report('2024-01-15', 1)

        assert result['success'] is True
        assert result['data']['statistics']['total_scans'] == 3
        assert result['data']['sub_job_name'] is None
        mock_scan_log_repo.get_report_with_sub_job.assert_called_once_with(
            start_date='2024-01-15',
            end_date='2024-01-15',
            job_id=1
        )

    def test_generate_report_with_notes_filter(
        self, report_service, mock_scan_log_repo, mock_job_type_repo,
        mock_sub_job_repo, sample_scans
    ):
        """Test report generation with notes filter"""
        # Setup mocks
        mock_job_type_repo.find_by_id.return_value = {'id': 1, 'job_name': 'Inbound'}
        mock_scan_log_repo.get_report_with_sub_job.return_value = sample_scans

        result = report_service.generate_report('2024-01-15', 1, notes_filter='note 1')

        assert result['success'] is True
        assert result['data']['statistics']['total_scans'] == 1  # Only 'Test note 1' matches
        assert result['data']['scans'][0]['barcode'] == 'BC001'

    def test_generate_report_empty_results(
        self, report_service, mock_scan_log_repo, mock_job_type_repo, mock_sub_job_repo
    ):
        """Test report generation with no results"""
        # Setup mocks
        mock_job_type_repo.find_by_id.return_value = {'id': 1, 'job_name': 'Inbound'}
        mock_scan_log_repo.get_report_with_sub_job.return_value = []

        result = report_service.generate_report('2024-01-15', 1)

        assert result['success'] is True
        assert result['data']['statistics']['total_scans'] == 0
        assert result['data']['statistics']['unique_barcodes'] == 0

    def test_generate_report_invalid_date_format(
        self, report_service, mock_job_type_repo
    ):
        """Test report generation with invalid date format"""
        mock_job_type_repo.find_by_id.return_value = {'id': 1, 'job_name': 'Inbound'}

        result = report_service.generate_report('invalid-date', 1)

        assert result['success'] is False
        assert 'รูปแบบวันที่' in result['message']

    def test_generate_report_job_not_found(
        self, report_service, mock_job_type_repo
    ):
        """Test report generation when job not found"""
        mock_job_type_repo.find_by_id.return_value = None

        result = report_service.generate_report('2024-01-15', 999)

        assert result['success'] is False
        assert 'ไม่พบงานหลัก' in result['message']

    def test_generate_report_database_error(
        self, report_service, mock_scan_log_repo, mock_job_type_repo
    ):
        """Test report generation handles database errors"""
        mock_job_type_repo.find_by_id.return_value = {'id': 1, 'job_name': 'Inbound'}
        mock_scan_log_repo.get_report_with_sub_job.side_effect = Exception("Database error")

        result = report_service.generate_report('2024-01-15', 1)

        assert result['success'] is False
        assert 'ไม่สามารถสร้างรายงาน' in result['message']


@pytest.mark.unit
@pytest.mark.services
class TestReportServiceDateRangeReport:
    """Test date range report generation"""

    def test_generate_date_range_report_success(
        self, report_service, mock_scan_log_repo, mock_job_type_repo,
        mock_sub_job_repo, sample_scans
    ):
        """Test successful date range report generation"""
        # Setup mocks
        mock_job_type_repo.find_by_id.return_value = {'id': 1, 'job_name': 'Inbound'}
        mock_sub_job_repo.get_details.return_value = {
            'id': 10,
            'sub_job_name': 'Receiving',
            'main_job_id': 1
        }
        mock_scan_log_repo.get_report_with_sub_job.return_value = sample_scans

        result = report_service.generate_date_range_report(
            '2024-01-01', '2024-01-31', 1, 10
        )

        assert result['success'] is True
        assert result['data']['start_date'] == '2024-01-01'
        assert result['data']['end_date'] == '2024-01-31'
        assert result['data']['statistics']['total_scans'] == 3
        mock_scan_log_repo.get_report_with_sub_job.assert_called_once_with(
            start_date='2024-01-01',
            end_date='2024-01-31',
            job_id=1,
            sub_job_id=10
        )

    def test_generate_date_range_report_invalid_range(
        self, report_service
    ):
        """Test date range report with start > end"""
        result = report_service.generate_date_range_report(
            '2024-01-31', '2024-01-01', 1
        )

        assert result['success'] is False
        assert 'เกิน' in result['message']

    def test_generate_date_range_report_invalid_format(
        self, report_service
    ):
        """Test date range report with invalid date format"""
        result = report_service.generate_date_range_report(
            'invalid', '2024-01-31', 1
        )

        assert result['success'] is False
        assert 'รูปแบบวันที่' in result['message']

    def test_generate_date_range_report_with_notes_filter(
        self, report_service, mock_scan_log_repo, mock_job_type_repo, sample_scans
    ):
        """Test date range report with notes filter"""
        mock_job_type_repo.find_by_id.return_value = {'id': 1, 'job_name': 'Inbound'}
        mock_scan_log_repo.get_report_with_sub_job.return_value = sample_scans

        result = report_service.generate_date_range_report(
            '2024-01-01', '2024-01-31', 1, notes_filter='Another'
        )

        assert result['success'] is True
        assert result['data']['statistics']['total_scans'] == 1
        assert result['data']['scans'][0]['notes'] == 'Another scan'

    def test_generate_date_range_report_database_error(
        self, report_service, mock_scan_log_repo, mock_job_type_repo
    ):
        """Test date range report handles database errors"""
        mock_job_type_repo.find_by_id.return_value = {'id': 1, 'job_name': 'Inbound'}
        mock_scan_log_repo.get_report_with_sub_job.side_effect = Exception("Database error")

        result = report_service.generate_date_range_report(
            '2024-01-01', '2024-01-31', 1
        )

        assert result['success'] is False
        assert 'ไม่สามารถสร้างรายงาน' in result['message']


@pytest.mark.unit
@pytest.mark.services
class TestReportServiceStatistics:
    """Test report statistics calculation"""

    def test_statistics_unique_barcodes(
        self, report_service, mock_scan_log_repo, mock_job_type_repo
    ):
        """Test unique barcode count is calculated correctly"""
        mock_job_type_repo.find_by_id.return_value = {'id': 1, 'job_name': 'Inbound'}
        scans = [
            {'barcode': 'BC001', 'notes': ''},
            {'barcode': 'BC001', 'notes': ''},  # Duplicate
            {'barcode': 'BC002', 'notes': ''},
            {'barcode': 'BC003', 'notes': ''}
        ]
        mock_scan_log_repo.get_report_with_sub_job.return_value = scans

        result = report_service.generate_report('2024-01-15', 1)

        assert result['success'] is True
        assert result['data']['statistics']['total_scans'] == 4
        assert result['data']['statistics']['unique_barcodes'] == 3

    def test_statistics_no_scans(
        self, report_service, mock_scan_log_repo, mock_job_type_repo
    ):
        """Test statistics with no scans"""
        mock_job_type_repo.find_by_id.return_value = {'id': 1, 'job_name': 'Inbound'}
        mock_scan_log_repo.get_report_with_sub_job.return_value = []

        result = report_service.generate_report('2024-01-15', 1)

        assert result['success'] is True
        assert result['data']['statistics']['total_scans'] == 0
        assert result['data']['statistics']['unique_barcodes'] == 0
