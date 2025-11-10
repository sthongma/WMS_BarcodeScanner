"""
Scan Validator - Validates barcode scanning data
"""

from typing import Any, Dict, Optional
from src.validation.base_validator import BaseValidator, ValidationResult
from src import constants


class ScanValidator(BaseValidator):
    """Validator for barcode scanning operations"""

    def __init__(self, job_type_repo=None, sub_job_repo=None):
        """
        Initialize scan validator

        Args:
            job_type_repo: JobTypeRepository instance (for validation against DB)
            sub_job_repo: SubJobRepository instance (for validation against DB)
        """
        self.job_type_repo = job_type_repo
        self.sub_job_repo = sub_job_repo

    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate scan data

        Args:
            data: Dictionary containing:
                - barcode: str
                - job_type_id: int
                - sub_job_type_id: int
                - user_id: str (optional)
                - notes: str (optional)

        Returns:
            ValidationResult: Validation result
        """
        errors = []

        # Validate barcode
        barcode_result = self.validate_barcode(data.get("barcode"))
        if not barcode_result:
            errors.append(barcode_result.message)

        # Validate job type ID
        job_id_result = self.validate_job_type_id(data.get("job_type_id"))
        if not job_id_result:
            errors.append(job_id_result.message)

        # Validate sub job type ID
        sub_job_id_result = self.validate_sub_job_type_id(data.get("sub_job_type_id"))
        if not sub_job_id_result:
            errors.append(sub_job_id_result.message)

        # Validate relationship if both IDs are valid
        if job_id_result and sub_job_id_result:
            relationship_result = self.validate_job_relationship(
                data.get("job_type_id"), data.get("sub_job_type_id")
            )
            if not relationship_result:
                errors.append(relationship_result.message)

        if errors:
            return self.create_error_result("; ".join(errors), errors)

        return self.create_success_result("Validation successful")

    def validate_barcode(self, barcode: Optional[str]) -> ValidationResult:
        """
        Validate barcode value

        Args:
            barcode: Barcode string to validate

        Returns:
            ValidationResult: Validation result
        """
        if not self.is_not_empty(barcode):
            return self.create_error_result(constants.ERROR_EMPTY_BARCODE)

        # Additional barcode format validation can be added here
        # For example: length checks, pattern matching, etc.

        return self.create_success_result()

    def validate_job_type_id(self, job_type_id: Any) -> ValidationResult:
        """
        Validate job type ID

        Args:
            job_type_id: Job type ID to validate

        Returns:
            ValidationResult: Validation result
        """
        if job_type_id is None or job_type_id == "":
            return self.create_error_result(constants.ERROR_NO_JOB_TYPE)

        if not self.is_positive_integer(job_type_id):
            return self.create_error_result("Job type ID must be a positive integer")

        # Optional: Check if job type exists in database
        if self.job_type_repo:
            job_type = self.job_type_repo.find_by_id(int(job_type_id))
            if not job_type:
                return self.create_error_result(constants.ERROR_JOB_NOT_FOUND.format(job_type_id))

        return self.create_success_result()

    def validate_sub_job_type_id(self, sub_job_type_id: Any) -> ValidationResult:
        """
        Validate sub job type ID

        Args:
            sub_job_type_id: Sub job type ID to validate

        Returns:
            ValidationResult: Validation result
        """
        if sub_job_type_id is None or sub_job_type_id == "":
            return self.create_error_result(constants.ERROR_NO_SUB_JOB_TYPE)

        if not self.is_positive_integer(sub_job_type_id):
            return self.create_error_result("Sub job type ID must be a positive integer")

        # Optional: Check if sub job type exists in database
        if self.sub_job_repo:
            sub_job = self.sub_job_repo.find_by_id(int(sub_job_type_id))
            if not sub_job:
                return self.create_error_result(constants.ERROR_SUB_JOB_NOT_FOUND.format(sub_job_type_id))

        return self.create_success_result()

    def validate_job_relationship(self, job_type_id: int, sub_job_type_id: int) -> ValidationResult:
        """
        Validate that sub job belongs to the specified main job

        Args:
            job_type_id: Main job type ID
            sub_job_type_id: Sub job type ID

        Returns:
            ValidationResult: Validation result
        """
        if not self.sub_job_repo:
            # Skip validation if repository not provided
            return self.create_success_result()

        sub_job = self.sub_job_repo.find_by_id(int(sub_job_type_id))
        if sub_job and sub_job.get(constants.COL_MAIN_JOB_ID) != int(job_type_id):
            return self.create_error_result(constants.ERROR_SUB_JOB_MISMATCH)

        return self.create_success_result()

    def validate_user_id(self, user_id: Optional[str]) -> ValidationResult:
        """
        Validate user ID (optional field)

        Args:
            user_id: User ID string

        Returns:
            ValidationResult: Validation result
        """
        # User ID is optional, empty is valid
        if user_id is None or user_id == "":
            return self.create_success_result()

        # Additional user ID validation can be added here

        return self.create_success_result()

    def validate_notes(self, notes: Optional[str]) -> ValidationResult:
        """
        Validate notes field (optional)

        Args:
            notes: Notes string

        Returns:
            ValidationResult: Validation result
        """
        # Notes are optional, no specific validation needed
        return self.create_success_result()
