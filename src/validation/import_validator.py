"""
Import Validator - Validates import data structure and content
"""

from typing import Any, Dict, List, Optional
from src.validation.base_validator import BaseValidator, ValidationResult
from src import constants


class ImportValidator(BaseValidator):
    """Validator for data import operations"""

    def __init__(self, job_type_repo=None, sub_job_repo=None):
        """
        Initialize import validator

        Args:
            job_type_repo: JobTypeRepository instance (for validation against DB)
            sub_job_repo: SubJobRepository instance (for validation against DB)
        """
        self.job_type_repo = job_type_repo
        self.sub_job_repo = sub_job_repo

    def validate(self, data: List[Dict[str, Any]]) -> ValidationResult:
        """
        Validate import data structure

        Args:
            data: List of dictionaries representing rows to import

        Returns:
            ValidationResult: Validation result
        """
        if not data:
            return self.create_error_result(constants.ERROR_NO_IMPORT_DATA)

        # Validate that all rows have required columns
        columns_result = self.validate_required_columns(data[0])
        if not columns_result:
            return columns_result

        # Validate each row
        errors = []
        for idx, row in enumerate(data, start=1):
            row_result = self.validate_row(row, idx)
            if not row_result:
                errors.extend([f"Row {idx}: {err}" for err in row_result.errors])

        if errors:
            return self.create_error_result(
                f"Validation failed for {len(errors)} errors",
                errors
            )

        return self.create_success_result(f"Validated {len(data)} rows successfully")

    def validate_required_columns(
        self,
        row: Dict[str, Any],
        required_columns: Optional[List[str]] = None
    ) -> ValidationResult:
        """
        Validate that row has all required columns

        Args:
            row: Dictionary representing a single row
            required_columns: List of required column names
                            Default: constants.REQUIRED_IMPORT_COLUMNS

        Returns:
            ValidationResult: Validation result
        """
        if required_columns is None:
            required_columns = constants.REQUIRED_IMPORT_COLUMNS

        all_present, missing = self.has_required_keys(row, required_columns)

        if not all_present:
            return self.create_error_result(
                f"Missing required columns: {', '.join(missing)}",
                [f"Missing: {col}" for col in missing]
            )

        return self.create_success_result()

    def validate_row(
        self,
        row: Dict[str, Any],
        row_number: int
    ) -> ValidationResult:
        """
        Validate a single import row

        Args:
            row: Dictionary representing a single row
            row_number: Row number for error reporting

        Returns:
            ValidationResult: Validation result
        """
        errors = []

        # Validate barcode
        barcode_result = self.validate_barcode_field(row.get('barcode'))
        if not barcode_result:
            errors.append(barcode_result.message)

        # Validate main job ID
        main_job_result = self.validate_id_field(
            row.get('main_job_id'),
            'main_job_id'
        )
        if not main_job_result:
            errors.append(main_job_result.message)

        # Validate sub job ID
        sub_job_result = self.validate_id_field(
            row.get('sub_job_id'),
            'sub_job_id'
        )
        if not sub_job_result:
            errors.append(sub_job_result.message)

        # If basic validation passed, validate against database
        if not errors and self.job_type_repo and self.sub_job_repo:
            try:
                main_job_id = int(float(str(row.get('main_job_id'))))
                sub_job_id = int(float(str(row.get('sub_job_id'))))

                # Check main job exists
                job_exists_result = self.validate_job_exists(main_job_id)
                if not job_exists_result:
                    errors.append(job_exists_result.message)

                # Check sub job exists
                sub_job_exists_result = self.validate_sub_job_exists(sub_job_id)
                if not sub_job_exists_result:
                    errors.append(sub_job_exists_result.message)

                # Check relationship if both exist
                if job_exists_result and sub_job_exists_result:
                    relationship_result = self.validate_job_relationship(
                        main_job_id,
                        sub_job_id
                    )
                    if not relationship_result:
                        errors.append(relationship_result.message)

            except (ValueError, TypeError) as e:
                errors.append(f"Error validating IDs: {str(e)}")

        if errors:
            return self.create_error_result(
                f"Row {row_number} validation failed",
                errors
            )

        return self.create_success_result()

    def validate_barcode_field(self, barcode: Any) -> ValidationResult:
        """
        Validate barcode field in import data

        Args:
            barcode: Barcode value from import row

        Returns:
            ValidationResult: Validation result
        """
        # Convert to string and clean
        barcode_str = str(barcode).strip() if barcode is not None else ''

        # Check for empty or 'nan' values (common in pandas)
        if not barcode_str or barcode_str.lower() == 'nan':
            return self.create_error_result("Barcode is empty or missing")

        if not self.is_not_empty(barcode_str):
            return self.create_error_result("Barcode cannot be empty")

        return self.create_success_result()

    def validate_id_field(self, id_value: Any, field_name: str) -> ValidationResult:
        """
        Validate ID field is numeric and positive

        Args:
            id_value: ID value to validate
            field_name: Name of the field for error messages

        Returns:
            ValidationResult: Validation result
        """
        # Convert to string and clean
        id_str = str(id_value).strip() if id_value is not None else ''

        # Check for empty or 'nan' values
        if not id_str or id_str.lower() == 'nan':
            return self.create_error_result(f"{field_name} is empty or missing")

        # Check if numeric
        try:
            id_int = int(float(id_str))
            if id_int <= 0:
                return self.create_error_result(
                    f"{field_name} must be a positive integer, got: {id_int}"
                )
        except (ValueError, TypeError):
            return self.create_error_result(
                f"{field_name} must be numeric, got: {id_str}"
            )

        return self.create_success_result()

    def validate_job_exists(self, job_id: int) -> ValidationResult:
        """
        Validate that job type exists in database

        Args:
            job_id: Job type ID to check

        Returns:
            ValidationResult: Validation result
        """
        if not self.job_type_repo:
            # Skip validation if repository not provided
            return self.create_success_result()

        try:
            job_info = self.job_type_repo.find_by_id(job_id)
            if not job_info:
                return self.create_error_result(
                    constants.ERROR_JOB_NOT_FOUND.format(job_id)
                )
        except Exception as e:
            return self.create_error_result(f"Error checking job type: {str(e)}")

        return self.create_success_result()

    def validate_sub_job_exists(self, sub_job_id: int) -> ValidationResult:
        """
        Validate that sub job type exists in database

        Args:
            sub_job_id: Sub job type ID to check

        Returns:
            ValidationResult: Validation result
        """
        if not self.sub_job_repo:
            # Skip validation if repository not provided
            return self.create_success_result()

        try:
            sub_job_info = self.sub_job_repo.get_details(sub_job_id)
            if not sub_job_info:
                return self.create_error_result(
                    constants.ERROR_SUB_JOB_NOT_FOUND.format(sub_job_id)
                )

            # Check if sub job is active
            if not sub_job_info.get('is_active', True):
                return self.create_error_result(
                    f"Sub job type ID {sub_job_id} is inactive"
                )
        except Exception as e:
            return self.create_error_result(f"Error checking sub job type: {str(e)}")

        return self.create_success_result()

    def validate_job_relationship(
        self,
        main_job_id: int,
        sub_job_id: int
    ) -> ValidationResult:
        """
        Validate that sub job belongs to the specified main job

        Args:
            main_job_id: Main job type ID
            sub_job_id: Sub job type ID

        Returns:
            ValidationResult: Validation result
        """
        if not self.sub_job_repo:
            # Skip validation if repository not provided
            return self.create_success_result()

        try:
            sub_job_info = self.sub_job_repo.get_details(sub_job_id)
            if sub_job_info and sub_job_info.get(constants.COL_MAIN_JOB_ID) != main_job_id:
                return self.create_error_result(
                    f"Sub job ID {sub_job_id} does not belong to main job ID {main_job_id}"
                )
        except Exception as e:
            return self.create_error_result(f"Error checking job relationship: {str(e)}")

        return self.create_success_result()

    def validate_data_types(self, row: Dict[str, Any]) -> ValidationResult:
        """
        Validate data types in import row

        Args:
            row: Dictionary representing a single row

        Returns:
            ValidationResult: Validation result
        """
        errors = []

        # Check barcode can be converted to string
        try:
            str(row.get('barcode', ''))
        except Exception:
            errors.append("Barcode cannot be converted to string")

        # Check IDs can be converted to integers
        for field in ['main_job_id', 'sub_job_id']:
            try:
                value = row.get(field)
                if value is not None:
                    int(float(str(value)))
            except (ValueError, TypeError):
                errors.append(f"{field} must be numeric")

        # Check notes can be converted to string (optional field)
        if 'notes' in row:
            try:
                str(row.get('notes', ''))
            except Exception:
                errors.append("Notes cannot be converted to string")

        if errors:
            return self.create_error_result("Data type validation failed", errors)

        return self.create_success_result()
