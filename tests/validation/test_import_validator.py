"""
Tests for ImportValidator class

This module tests the import validator functionality including:
- Row validation
- Required columns check
- Data type validation
- ID field validation
- Job existence validation
"""
import pytest
from unittest.mock import MagicMock
from src.validation.import_validator import ImportValidator
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
def import_validator(mock_job_type_repo, mock_sub_job_repo):
    """Create ImportValidator instance with mocked repositories"""
    return ImportValidator(
        job_type_repo=mock_job_type_repo,
        sub_job_repo=mock_sub_job_repo
    )


@pytest.fixture
def import_validator_no_repos():
    """Create ImportValidator instance without repositories"""
    return ImportValidator()


@pytest.mark.unit
@pytest.mark.validation
class TestImportValidatorInitialization:
    """Test ImportValidator initialization"""

    def test_init_with_repos(self, import_validator, mock_job_type_repo, mock_sub_job_repo):
        """Test initialization with repositories"""
        assert import_validator.job_type_repo == mock_job_type_repo
        assert import_validator.sub_job_repo == mock_sub_job_repo

    def test_init_without_repos(self, import_validator_no_repos):
        """Test initialization without repositories"""
        assert import_validator_no_repos.job_type_repo is None
        assert import_validator_no_repos.sub_job_repo is None


@pytest.mark.unit
@pytest.mark.validation
class TestValidateRequiredColumns:
    """Test required columns validation"""

    def test_validate_required_columns_all_present(self, import_validator):
        """Test validation passes when all required columns present"""
        row = {
            "barcode": "BC001",
            "main_job_id": 1,
            "sub_job_id": 10,
            "notes": "Test"
        }

        result = import_validator.validate_required_columns(row)

        assert result.is_valid is True

    def test_validate_required_columns_one_missing(self, import_validator):
        """Test validation fails when one required column missing"""
        row = {
            "barcode": "BC001",
            "main_job_id": 1
            # Missing sub_job_id
        }

        result = import_validator.validate_required_columns(row)

        assert result.is_valid is False
        assert "sub_job_id" in result.message

    def test_validate_required_columns_multiple_missing(self, import_validator):
        """Test validation fails when multiple required columns missing"""
        row = {
            "barcode": "BC001"
            # Missing main_job_id and sub_job_id
        }

        result = import_validator.validate_required_columns(row)

        assert result.is_valid is False
        assert len(result.errors) == 2

    def test_validate_required_columns_custom_list(self, import_validator):
        """Test validation with custom required columns list"""
        row = {
            "custom_field": "value"
        }

        result = import_validator.validate_required_columns(
            row,
            required_columns=["custom_field"]
        )

        assert result.is_valid is True


@pytest.mark.unit
@pytest.mark.validation
class TestValidateBarcodeField:
    """Test barcode field validation"""

    def test_validate_barcode_field_valid(self, import_validator):
        """Test validation passes with valid barcode"""
        result = import_validator.validate_barcode_field("BARCODE123")

        assert result.is_valid is True

    def test_validate_barcode_field_empty_string(self, import_validator):
        """Test validation fails with empty string"""
        result = import_validator.validate_barcode_field("")

        assert result.is_valid is False
        assert "empty" in result.message.lower()

    def test_validate_barcode_field_whitespace(self, import_validator):
        """Test validation fails with whitespace only"""
        result = import_validator.validate_barcode_field("   ")

        assert result.is_valid is False

    def test_validate_barcode_field_none(self, import_validator):
        """Test validation fails with None"""
        result = import_validator.validate_barcode_field(None)

        assert result.is_valid is False

    def test_validate_barcode_field_nan_string(self, import_validator):
        """Test validation fails with 'nan' string (pandas NaN)"""
        result = import_validator.validate_barcode_field("nan")

        assert result.is_valid is False

    def test_validate_barcode_field_numeric(self, import_validator):
        """Test validation passes with numeric barcode"""
        result = import_validator.validate_barcode_field(12345)

        assert result.is_valid is True


@pytest.mark.unit
@pytest.mark.validation
class TestValidateIdField:
    """Test ID field validation"""

    def test_validate_id_field_valid_integer(self, import_validator):
        """Test validation passes with valid integer"""
        result = import_validator.validate_id_field(1, "test_id")

        assert result.is_valid is True

    def test_validate_id_field_valid_string(self, import_validator):
        """Test validation passes with numeric string"""
        result = import_validator.validate_id_field("5", "test_id")

        assert result.is_valid is True

    def test_validate_id_field_float_string(self, import_validator):
        """Test validation passes with float string (Excel format)"""
        result = import_validator.validate_id_field("10.0", "test_id")

        assert result.is_valid is True

    def test_validate_id_field_empty_string(self, import_validator):
        """Test validation fails with empty string"""
        result = import_validator.validate_id_field("", "test_id")

        assert result.is_valid is False
        assert "test_id" in result.message

    def test_validate_id_field_none(self, import_validator):
        """Test validation fails with None"""
        result = import_validator.validate_id_field(None, "test_id")

        assert result.is_valid is False

    def test_validate_id_field_nan_string(self, import_validator):
        """Test validation fails with 'nan' string"""
        result = import_validator.validate_id_field("nan", "test_id")

        assert result.is_valid is False

    def test_validate_id_field_zero(self, import_validator):
        """Test validation fails with zero"""
        result = import_validator.validate_id_field(0, "test_id")

        assert result.is_valid is False
        assert "positive" in result.message

    def test_validate_id_field_negative(self, import_validator):
        """Test validation fails with negative number"""
        result = import_validator.validate_id_field(-1, "test_id")

        assert result.is_valid is False
        assert "positive" in result.message

    def test_validate_id_field_invalid_string(self, import_validator):
        """Test validation fails with non-numeric string"""
        result = import_validator.validate_id_field("abc", "test_id")

        assert result.is_valid is False
        assert "numeric" in result.message


@pytest.mark.unit
@pytest.mark.validation
class TestValidateJobExists:
    """Test job existence validation"""

    def test_validate_job_exists_without_repo(self, import_validator_no_repos):
        """Test validation passes without repository"""
        result = import_validator_no_repos.validate_job_exists(1)

        assert result.is_valid is True

    def test_validate_job_exists_found(self, import_validator, mock_job_type_repo):
        """Test validation passes when job exists"""
        mock_job_type_repo.find_by_id.return_value = {"id": 1, "job_name": "Inbound"}

        result = import_validator.validate_job_exists(1)

        assert result.is_valid is True
        mock_job_type_repo.find_by_id.assert_called_once_with(1)

    def test_validate_job_exists_not_found(self, import_validator, mock_job_type_repo):
        """Test validation fails when job not found"""
        mock_job_type_repo.find_by_id.return_value = None

        result = import_validator.validate_job_exists(999)

        assert result.is_valid is False
        assert "999" in result.message

    def test_validate_job_exists_error(self, import_validator, mock_job_type_repo):
        """Test validation handles repository errors"""
        mock_job_type_repo.find_by_id.side_effect = Exception("Database error")

        result = import_validator.validate_job_exists(1)

        assert result.is_valid is False
        assert "Error" in result.message


@pytest.mark.unit
@pytest.mark.validation
class TestValidateSubJobExists:
    """Test sub job existence validation"""

    def test_validate_sub_job_exists_without_repo(self, import_validator_no_repos):
        """Test validation passes without repository"""
        result = import_validator_no_repos.validate_sub_job_exists(10)

        assert result.is_valid is True

    def test_validate_sub_job_exists_found_active(
        self, import_validator, mock_sub_job_repo
    ):
        """Test validation passes when sub job exists and is active"""
        mock_sub_job_repo.get_details.return_value = {
            "id": 10,
            "sub_job_name": "Receiving",
            "is_active": True
        }

        result = import_validator.validate_sub_job_exists(10)

        assert result.is_valid is True
        mock_sub_job_repo.get_details.assert_called_once_with(10)

    def test_validate_sub_job_exists_not_found(
        self, import_validator, mock_sub_job_repo
    ):
        """Test validation fails when sub job not found"""
        mock_sub_job_repo.get_details.return_value = None

        result = import_validator.validate_sub_job_exists(999)

        assert result.is_valid is False
        assert "999" in result.message

    def test_validate_sub_job_exists_inactive(
        self, import_validator, mock_sub_job_repo
    ):
        """Test validation fails when sub job is inactive"""
        mock_sub_job_repo.get_details.return_value = {
            "id": 10,
            "sub_job_name": "Receiving",
            "is_active": False
        }

        result = import_validator.validate_sub_job_exists(10)

        assert result.is_valid is False
        assert "inactive" in result.message.lower()

    def test_validate_sub_job_exists_error(
        self, import_validator, mock_sub_job_repo
    ):
        """Test validation handles repository errors"""
        mock_sub_job_repo.get_details.side_effect = Exception("Database error")

        result = import_validator.validate_sub_job_exists(10)

        assert result.is_valid is False
        assert "Error" in result.message


@pytest.mark.unit
@pytest.mark.validation
class TestValidateJobRelationship:
    """Test job relationship validation"""

    def test_validate_job_relationship_without_repo(self, import_validator_no_repos):
        """Test validation passes without repository"""
        result = import_validator_no_repos.validate_job_relationship(1, 10)

        assert result.is_valid is True

    def test_validate_job_relationship_correct(
        self, import_validator, mock_sub_job_repo
    ):
        """Test validation passes when relationship is correct"""
        mock_sub_job_repo.get_details.return_value = {
            "id": 10,
            "sub_job_name": "Receiving",
            "main_job_id": 1
        }

        result = import_validator.validate_job_relationship(1, 10)

        assert result.is_valid is True

    def test_validate_job_relationship_incorrect(
        self, import_validator, mock_sub_job_repo
    ):
        """Test validation fails when relationship is incorrect"""
        mock_sub_job_repo.get_details.return_value = {
            "id": 10,
            "sub_job_name": "Receiving",
            "main_job_id": 2  # Different main job
        }

        result = import_validator.validate_job_relationship(1, 10)

        assert result.is_valid is False
        assert "belong" in result.message.lower()

    def test_validate_job_relationship_error(
        self, import_validator, mock_sub_job_repo
    ):
        """Test validation handles repository errors"""
        mock_sub_job_repo.get_details.side_effect = Exception("Database error")

        result = import_validator.validate_job_relationship(1, 10)

        assert result.is_valid is False
        assert "Error" in result.message


@pytest.mark.unit
@pytest.mark.validation
class TestValidateDataTypes:
    """Test data type validation"""

    def test_validate_data_types_valid(self, import_validator):
        """Test validation passes with valid data types"""
        row = {
            "barcode": "BC001",
            "main_job_id": 1,
            "sub_job_id": 10,
            "notes": "Test notes"
        }

        result = import_validator.validate_data_types(row)

        assert result.is_valid is True

    def test_validate_data_types_numeric_strings(self, import_validator):
        """Test validation passes with numeric strings"""
        row = {
            "barcode": "BC001",
            "main_job_id": "1",
            "sub_job_id": "10",
            "notes": "Test"
        }

        result = import_validator.validate_data_types(row)

        assert result.is_valid is True

    def test_validate_data_types_invalid_main_job_id(self, import_validator):
        """Test validation fails with invalid main_job_id type"""
        row = {
            "barcode": "BC001",
            "main_job_id": "abc",
            "sub_job_id": 10
        }

        result = import_validator.validate_data_types(row)

        assert result.is_valid is False
        assert any("main_job_id" in err for err in result.errors)

    def test_validate_data_types_invalid_sub_job_id(self, import_validator):
        """Test validation fails with invalid sub_job_id type"""
        row = {
            "barcode": "BC001",
            "main_job_id": 1,
            "sub_job_id": "xyz"
        }

        result = import_validator.validate_data_types(row)

        assert result.is_valid is False
        assert any("sub_job_id" in err for err in result.errors)


@pytest.mark.unit
@pytest.mark.validation
class TestValidateRow:
    """Test full row validation"""

    def test_validate_row_success_without_repos(self, import_validator_no_repos):
        """Test row validation passes without repository checks"""
        row = {
            "barcode": "BARCODE123",
            "main_job_id": 1,
            "sub_job_id": 10,
            "notes": "Test"
        }

        result = import_validator_no_repos.validate_row(row, 1)

        assert result.is_valid is True

    def test_validate_row_success_with_repos(
        self, import_validator, mock_job_type_repo, mock_sub_job_repo
    ):
        """Test row validation passes with all checks"""
        mock_job_type_repo.find_by_id.return_value = {"id": 1, "job_name": "Inbound"}
        mock_sub_job_repo.get_details.return_value = {
            "id": 10,
            "sub_job_name": "Receiving",
            "main_job_id": 1,
            "is_active": True
        }

        row = {
            "barcode": "BARCODE123",
            "main_job_id": 1,
            "sub_job_id": 10
        }

        result = import_validator.validate_row(row, 1)

        assert result.is_valid is True

    def test_validate_row_empty_barcode(self, import_validator):
        """Test row validation fails with empty barcode"""
        row = {
            "barcode": "",
            "main_job_id": 1,
            "sub_job_id": 10
        }

        result = import_validator.validate_row(row, 1)

        assert result.is_valid is False
        assert len(result.errors) >= 1

    def test_validate_row_invalid_ids(self, import_validator):
        """Test row validation fails with invalid IDs"""
        row = {
            "barcode": "BC001",
            "main_job_id": "abc",
            "sub_job_id": "xyz"
        }

        result = import_validator.validate_row(row, 1)

        assert result.is_valid is False
        assert len(result.errors) >= 2

    def test_validate_row_relationship_mismatch(
        self, import_validator, mock_job_type_repo, mock_sub_job_repo
    ):
        """Test row validation fails with relationship mismatch"""
        mock_job_type_repo.find_by_id.return_value = {"id": 1, "job_name": "Inbound"}
        mock_sub_job_repo.get_details.return_value = {
            "id": 10,
            "sub_job_name": "Receiving",
            "main_job_id": 2,  # Different main job
            "is_active": True
        }

        row = {
            "barcode": "BC001",
            "main_job_id": 1,
            "sub_job_id": 10
        }

        result = import_validator.validate_row(row, 1)

        assert result.is_valid is False

    def test_validate_row_includes_row_number(self, import_validator):
        """Test row validation includes row number in error"""
        row = {
            "barcode": "",
            "main_job_id": 1,
            "sub_job_id": 10
        }

        result = import_validator.validate_row(row, 42)

        assert result.is_valid is False
        assert "42" in result.message


@pytest.mark.unit
@pytest.mark.validation
class TestFullValidation:
    """Test full import data validation"""

    def test_validate_empty_data(self, import_validator):
        """Test validation fails with empty data"""
        result = import_validator.validate([])

        assert result.is_valid is False
        assert constants.ERROR_NO_IMPORT_DATA in result.message

    def test_validate_success(self, import_validator_no_repos):
        """Test validation passes with valid data"""
        data = [
            {
                "barcode": "BC001",
                "main_job_id": 1,
                "sub_job_id": 10
            },
            {
                "barcode": "BC002",
                "main_job_id": 1,
                "sub_job_id": 10
            }
        ]

        result = import_validator_no_repos.validate(data)

        assert result.is_valid is True
        assert "2" in result.message

    def test_validate_missing_columns(self, import_validator):
        """Test validation fails with missing required columns"""
        data = [
            {
                "barcode": "BC001"
                # Missing main_job_id and sub_job_id
            }
        ]

        result = import_validator.validate(data)

        assert result.is_valid is False

    def test_validate_returns_validation_result(self, import_validator):
        """Test validate returns ValidationResult instance"""
        data = [{"barcode": "BC001", "main_job_id": 1, "sub_job_id": 10}]

        result = import_validator.validate(data)

        assert isinstance(result, ValidationResult)
