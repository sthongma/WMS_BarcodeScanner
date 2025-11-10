"""
Tests for ScanValidator class

This module tests the scan validator functionality including:
- Barcode validation
- Job type ID validation
- Sub job type ID validation
- Job relationship validation
- Full scan data validation
"""
import pytest
from unittest.mock import MagicMock
from src.validation.scan_validator import ScanValidator
from src.validation.base_validator import ValidationResult
from src import constants


@pytest.fixture
def mock_job_type_repo():
    """Mock JobTypeRepository for testing"""
    return MagicMock()


@pytest.fixture
def mock_sub_job_repo():
    """Mock SubJobRepository for testing"""
    return MagicMock()


@pytest.fixture
def scan_validator(mock_job_type_repo, mock_sub_job_repo):
    """Create ScanValidator instance with mocked repositories"""
    return ScanValidator(
        job_type_repo=mock_job_type_repo,
        sub_job_repo=mock_sub_job_repo
    )


@pytest.fixture
def scan_validator_no_repos():
    """Create ScanValidator instance without repositories"""
    return ScanValidator()


@pytest.mark.unit
@pytest.mark.validation
class TestScanValidatorInitialization:
    """Test ScanValidator initialization"""

    def test_init_with_repos(self, scan_validator, mock_job_type_repo, mock_sub_job_repo):
        """Test initialization with repositories"""
        assert scan_validator.job_type_repo == mock_job_type_repo
        assert scan_validator.sub_job_repo == mock_sub_job_repo

    def test_init_without_repos(self, scan_validator_no_repos):
        """Test initialization without repositories"""
        assert scan_validator_no_repos.job_type_repo is None
        assert scan_validator_no_repos.sub_job_repo is None


@pytest.mark.unit
@pytest.mark.validation
class TestValidateBarcode:
    """Test barcode validation"""

    def test_validate_barcode_valid(self, scan_validator):
        """Test validation passes with valid barcode"""
        result = scan_validator.validate_barcode("BARCODE123")

        assert result.is_valid is True
        assert result.message == ""

    def test_validate_barcode_empty_string(self, scan_validator):
        """Test validation fails with empty barcode"""
        result = scan_validator.validate_barcode("")

        assert result.is_valid is False
        assert constants.ERROR_EMPTY_BARCODE in result.message

    def test_validate_barcode_whitespace(self, scan_validator):
        """Test validation fails with whitespace-only barcode"""
        result = scan_validator.validate_barcode("   ")

        assert result.is_valid is False
        assert constants.ERROR_EMPTY_BARCODE in result.message

    def test_validate_barcode_none(self, scan_validator):
        """Test validation fails with None barcode"""
        result = scan_validator.validate_barcode(None)

        assert result.is_valid is False
        assert constants.ERROR_EMPTY_BARCODE in result.message

    def test_validate_barcode_returns_validation_result(self, scan_validator):
        """Test validate_barcode returns ValidationResult"""
        result = scan_validator.validate_barcode("TEST")

        assert isinstance(result, ValidationResult)


@pytest.mark.unit
@pytest.mark.validation
class TestValidateJobTypeId:
    """Test job type ID validation"""

    def test_validate_job_type_id_valid(self, scan_validator):
        """Test validation passes with valid job type ID"""
        result = scan_validator.validate_job_type_id(1)

        assert result.is_valid is True

    def test_validate_job_type_id_string_number(self, scan_validator):
        """Test validation passes with string number"""
        result = scan_validator.validate_job_type_id("5")

        assert result.is_valid is True

    def test_validate_job_type_id_none(self, scan_validator):
        """Test validation fails with None"""
        result = scan_validator.validate_job_type_id(None)

        assert result.is_valid is False
        assert constants.ERROR_NO_JOB_TYPE in result.message

    def test_validate_job_type_id_empty_string(self, scan_validator):
        """Test validation fails with empty string"""
        result = scan_validator.validate_job_type_id("")

        assert result.is_valid is False
        assert constants.ERROR_NO_JOB_TYPE in result.message

    def test_validate_job_type_id_zero(self, scan_validator):
        """Test validation fails with zero"""
        result = scan_validator.validate_job_type_id(0)

        assert result.is_valid is False
        assert "positive integer" in result.message

    def test_validate_job_type_id_negative(self, scan_validator):
        """Test validation fails with negative number"""
        result = scan_validator.validate_job_type_id(-1)

        assert result.is_valid is False
        assert "positive integer" in result.message

    def test_validate_job_type_id_invalid_string(self, scan_validator):
        """Test validation fails with non-numeric string"""
        result = scan_validator.validate_job_type_id("abc")

        assert result.is_valid is False
        assert "positive integer" in result.message

    def test_validate_job_type_id_with_repo_exists(
        self, scan_validator, mock_job_type_repo
    ):
        """Test validation with repository when job type exists"""
        mock_job_type_repo.find_by_id.return_value = {"id": 1, "job_name": "Inbound"}

        result = scan_validator.validate_job_type_id(1)

        assert result.is_valid is True
        mock_job_type_repo.find_by_id.assert_called_once_with(1)

    def test_validate_job_type_id_with_repo_not_found(
        self, scan_validator, mock_job_type_repo
    ):
        """Test validation with repository when job type not found"""
        mock_job_type_repo.find_by_id.return_value = None

        result = scan_validator.validate_job_type_id(999)

        assert result.is_valid is False
        assert "999" in result.message


@pytest.mark.unit
@pytest.mark.validation
class TestValidateSubJobTypeId:
    """Test sub job type ID validation"""

    def test_validate_sub_job_type_id_valid(self, scan_validator):
        """Test validation passes with valid sub job type ID"""
        result = scan_validator.validate_sub_job_type_id(10)

        assert result.is_valid is True

    def test_validate_sub_job_type_id_string_number(self, scan_validator):
        """Test validation passes with string number"""
        result = scan_validator.validate_sub_job_type_id("15")

        assert result.is_valid is True

    def test_validate_sub_job_type_id_none(self, scan_validator):
        """Test validation fails with None"""
        result = scan_validator.validate_sub_job_type_id(None)

        assert result.is_valid is False
        assert constants.ERROR_NO_SUB_JOB_TYPE in result.message

    def test_validate_sub_job_type_id_empty_string(self, scan_validator):
        """Test validation fails with empty string"""
        result = scan_validator.validate_sub_job_type_id("")

        assert result.is_valid is False
        assert constants.ERROR_NO_SUB_JOB_TYPE in result.message

    def test_validate_sub_job_type_id_zero(self, scan_validator):
        """Test validation fails with zero"""
        result = scan_validator.validate_sub_job_type_id(0)

        assert result.is_valid is False
        assert "positive integer" in result.message

    def test_validate_sub_job_type_id_negative(self, scan_validator):
        """Test validation fails with negative number"""
        result = scan_validator.validate_sub_job_type_id(-1)

        assert result.is_valid is False
        assert "positive integer" in result.message

    def test_validate_sub_job_type_id_invalid_string(self, scan_validator):
        """Test validation fails with non-numeric string"""
        result = scan_validator.validate_sub_job_type_id("xyz")

        assert result.is_valid is False
        assert "positive integer" in result.message

    def test_validate_sub_job_type_id_with_repo_exists(
        self, scan_validator, mock_sub_job_repo
    ):
        """Test validation with repository when sub job type exists"""
        mock_sub_job_repo.find_by_id.return_value = {
            "id": 10,
            "sub_job_name": "Receiving"
        }

        result = scan_validator.validate_sub_job_type_id(10)

        assert result.is_valid is True
        mock_sub_job_repo.find_by_id.assert_called_once_with(10)

    def test_validate_sub_job_type_id_with_repo_not_found(
        self, scan_validator, mock_sub_job_repo
    ):
        """Test validation with repository when sub job type not found"""
        mock_sub_job_repo.find_by_id.return_value = None

        result = scan_validator.validate_sub_job_type_id(999)

        assert result.is_valid is False
        assert "999" in result.message


@pytest.mark.unit
@pytest.mark.validation
class TestValidateJobRelationship:
    """Test job relationship validation"""

    def test_validate_job_relationship_without_repo(self, scan_validator_no_repos):
        """Test relationship validation without repository"""
        result = scan_validator_no_repos.validate_job_relationship(1, 10)

        assert result.is_valid is True

    def test_validate_job_relationship_correct(
        self, scan_validator, mock_sub_job_repo
    ):
        """Test validation passes when relationship is correct"""
        mock_sub_job_repo.find_by_id.return_value = {
            "id": 10,
            "sub_job_name": "Receiving",
            "main_job_id": 1
        }

        result = scan_validator.validate_job_relationship(1, 10)

        assert result.is_valid is True
        mock_sub_job_repo.find_by_id.assert_called_once_with(10)

    def test_validate_job_relationship_incorrect(
        self, scan_validator, mock_sub_job_repo
    ):
        """Test validation fails when relationship is incorrect"""
        mock_sub_job_repo.find_by_id.return_value = {
            "id": 10,
            "sub_job_name": "Receiving",
            "main_job_id": 2  # Different main job
        }

        result = scan_validator.validate_job_relationship(1, 10)

        assert result.is_valid is False
        assert constants.ERROR_SUB_JOB_MISMATCH in result.message

    def test_validate_job_relationship_sub_job_not_found(
        self, scan_validator, mock_sub_job_repo
    ):
        """Test validation passes when sub job not found (already validated elsewhere)"""
        mock_sub_job_repo.find_by_id.return_value = None

        result = scan_validator.validate_job_relationship(1, 10)

        assert result.is_valid is True


@pytest.mark.unit
@pytest.mark.validation
class TestValidateUserIdAndNotes:
    """Test user ID and notes validation"""

    def test_validate_user_id_valid(self, scan_validator):
        """Test user ID validation with valid value"""
        result = scan_validator.validate_user_id("user123")

        assert result.is_valid is True

    def test_validate_user_id_empty(self, scan_validator):
        """Test user ID validation with empty value (optional)"""
        result = scan_validator.validate_user_id("")

        assert result.is_valid is True

    def test_validate_user_id_none(self, scan_validator):
        """Test user ID validation with None (optional)"""
        result = scan_validator.validate_user_id(None)

        assert result.is_valid is True

    def test_validate_notes_valid(self, scan_validator):
        """Test notes validation with valid value"""
        result = scan_validator.validate_notes("Some notes here")

        assert result.is_valid is True

    def test_validate_notes_empty(self, scan_validator):
        """Test notes validation with empty value (optional)"""
        result = scan_validator.validate_notes("")

        assert result.is_valid is True

    def test_validate_notes_none(self, scan_validator):
        """Test notes validation with None (optional)"""
        result = scan_validator.validate_notes(None)

        assert result.is_valid is True


@pytest.mark.unit
@pytest.mark.validation
class TestFullValidation:
    """Test full scan data validation"""

    def test_validate_success_without_repos(self, scan_validator_no_repos):
        """Test full validation passes without repository checks"""
        data = {
            "barcode": "BARCODE123",
            "job_type_id": 1,
            "sub_job_type_id": 10,
            "user_id": "user1",
            "notes": "Test notes"
        }

        result = scan_validator_no_repos.validate(data)

        assert result.is_valid is True
        assert "successful" in result.message.lower()

    def test_validate_success_with_repos(
        self, scan_validator, mock_job_type_repo, mock_sub_job_repo
    ):
        """Test full validation passes with all checks"""
        mock_job_type_repo.find_by_id.return_value = {"id": 1, "job_name": "Inbound"}
        mock_sub_job_repo.find_by_id.return_value = {
            "id": 10,
            "sub_job_name": "Receiving",
            "main_job_id": 1
        }

        data = {
            "barcode": "BARCODE123",
            "job_type_id": 1,
            "sub_job_type_id": 10
        }

        result = scan_validator.validate(data)

        assert result.is_valid is True

    def test_validate_empty_barcode(self, scan_validator):
        """Test full validation fails with empty barcode"""
        data = {
            "barcode": "",
            "job_type_id": 1,
            "sub_job_type_id": 10
        }

        result = scan_validator.validate(data)

        assert result.is_valid is False
        assert constants.ERROR_EMPTY_BARCODE in result.message

    def test_validate_missing_job_type(self, scan_validator):
        """Test full validation fails with missing job type"""
        data = {
            "barcode": "BARCODE123",
            "job_type_id": None,
            "sub_job_type_id": 10
        }

        result = scan_validator.validate(data)

        assert result.is_valid is False
        assert constants.ERROR_NO_JOB_TYPE in result.message

    def test_validate_missing_sub_job_type(self, scan_validator):
        """Test full validation fails with missing sub job type"""
        data = {
            "barcode": "BARCODE123",
            "job_type_id": 1,
            "sub_job_type_id": None
        }

        result = scan_validator.validate(data)

        assert result.is_valid is False
        assert constants.ERROR_NO_SUB_JOB_TYPE in result.message

    def test_validate_multiple_errors(self, scan_validator):
        """Test full validation with multiple errors"""
        data = {
            "barcode": "",
            "job_type_id": None,
            "sub_job_type_id": ""
        }

        result = scan_validator.validate(data)

        assert result.is_valid is False
        assert len(result.errors) >= 3

    def test_validate_relationship_mismatch(
        self, scan_validator, mock_job_type_repo, mock_sub_job_repo
    ):
        """Test full validation fails with relationship mismatch"""
        mock_job_type_repo.find_by_id.return_value = {"id": 1, "job_name": "Inbound"}
        mock_sub_job_repo.find_by_id.return_value = {
            "id": 10,
            "sub_job_name": "Receiving",
            "main_job_id": 2  # Different main job
        }

        data = {
            "barcode": "BARCODE123",
            "job_type_id": 1,
            "sub_job_type_id": 10
        }

        result = scan_validator.validate(data)

        assert result.is_valid is False
        assert constants.ERROR_SUB_JOB_MISMATCH in result.message

    def test_validate_returns_validation_result(self, scan_validator):
        """Test validate returns ValidationResult instance"""
        data = {
            "barcode": "TEST",
            "job_type_id": 1,
            "sub_job_type_id": 10
        }

        result = scan_validator.validate(data)

        assert isinstance(result, ValidationResult)

    def test_validate_optional_fields(self, scan_validator_no_repos):
        """Test validation with optional fields"""
        data = {
            "barcode": "BARCODE123",
            "job_type_id": 1,
            "sub_job_type_id": 10,
            "user_id": "user1",
            "notes": "Test notes"
        }

        result = scan_validator_no_repos.validate(data)

        assert result.is_valid is True
