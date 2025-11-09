#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scan Service Module
Handles business logic for barcode scanning operations
"""

from typing import Dict, Optional, Any
from ..database.scan_log_repository import ScanLogRepository
from ..database.sub_job_repository import SubJobRepository
from ..database.dependency_repository import DependencyRepository


class ScanService:
    """
    Service for handling barcode scanning business logic

    Responsibilities:
    - Validate scan input
    - Check for duplicate scans
    - Verify job dependencies
    - Process and save scans

    Note: This service contains NO UI logic (no messageboxes, no widgets).
    It only contains pure business logic and returns structured results.
    """

    def __init__(
        self,
        scan_log_repo: ScanLogRepository,
        sub_job_repo: SubJobRepository,
        dependency_repo: DependencyRepository
    ):
        """
        Initialize ScanService with required repositories

        Args:
            scan_log_repo: Repository for scan log operations
            sub_job_repo: Repository for sub job type operations
            dependency_repo: Repository for dependency operations
        """
        self.scan_log_repo = scan_log_repo
        self.sub_job_repo = sub_job_repo
        self.dependency_repo = dependency_repo

    def process_scan(
        self,
        barcode: str,
        job_type_name: str,
        job_id: int,
        sub_job_type_name: str,
        user_id: str,
        notes: str = ""
    ) -> Dict[str, Any]:
        """
        Process a barcode scan with full validation and dependency checking

        Args:
            barcode: Barcode string to scan
            job_type_name: Name of the main job type
            job_id: ID of the main job type
            sub_job_type_name: Name of the sub job type
            user_id: User performing the scan
            notes: Optional notes for the scan

        Returns:
            Dictionary with:
            - success (bool): Whether the scan was successful
            - message (str): Human-readable message
            - data (dict): Additional data (duplicate_info, scan_id, etc.)
        """
        # Step 1: Validate input
        validation_result = self._validate_input(
            barcode, job_type_name, sub_job_type_name
        )
        if not validation_result['success']:
            return validation_result

        # Step 2: Get sub job ID
        sub_job_data = self.sub_job_repo.find_by_name(job_id, sub_job_type_name)
        if not sub_job_data:
            return {
                'success': False,
                'message': 'ไม่พบประเภทงานย่อยที่เลือก',
                'data': {}
            }

        sub_job_id = sub_job_data['id']

        # Step 3: Check for duplicates
        duplicate_result = self._check_duplicate(barcode, job_id, sub_job_id)
        if not duplicate_result['success']:
            return duplicate_result

        # Step 4: Check dependencies
        dependency_result = self._check_dependencies(barcode, job_id)
        if not dependency_result['success']:
            return dependency_result

        # Step 5: Save the scan
        try:
            self.scan_log_repo.create_scan(
                barcode=barcode,
                job_type=job_type_name,
                user_id=user_id,
                job_id=job_id,
                sub_job_id=sub_job_id,
                notes=notes
            )

            return {
                'success': True,
                'message': 'สแกนสำเร็จ',
                'data': {
                    'barcode': barcode,
                    'job_type': job_type_name,
                    'sub_job_type': sub_job_type_name,
                    'notes': notes
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'ไม่สามารถบันทึกข้อมูลได้: {str(e)}',
                'data': {}
            }

    def _validate_input(
        self,
        barcode: str,
        job_type_name: str,
        sub_job_type_name: str
    ) -> Dict[str, Any]:
        """
        Validate scan input parameters

        Args:
            barcode: Barcode to validate
            job_type_name: Main job type name
            sub_job_type_name: Sub job type name

        Returns:
            Result dictionary
        """
        if not barcode or not barcode.strip():
            return {
                'success': False,
                'message': 'กรุณาใส่บาร์โค้ด',
                'data': {}
            }

        if not job_type_name or not job_type_name.strip():
            return {
                'success': False,
                'message': 'กรุณาเลือกประเภทงานหลักก่อน',
                'data': {}
            }

        if not sub_job_type_name or not sub_job_type_name.strip():
            return {
                'success': False,
                'message': 'กรุณาเลือกประเภทงานย่อยก่อน',
                'data': {}
            }

        return {
            'success': True,
            'message': 'Validation passed',
            'data': {}
        }

    def _check_duplicate(
        self,
        barcode: str,
        job_id: int,
        sub_job_id: int
    ) -> Dict[str, Any]:
        """
        Check for duplicate scans

        Args:
            barcode: Barcode to check
            job_id: Main job ID
            sub_job_id: Sub job ID

        Returns:
            Result dictionary with duplicate_info if found
        """
        try:
            existing = self.scan_log_repo.check_duplicate(
                barcode=barcode,
                job_id=job_id,
                hours=24*365  # Check entire history
            )

            # Check if the existing scan has the same sub_job_id
            if existing and existing.get('sub_job_id') == sub_job_id:
                return {
                    'success': False,
                    'message': 'พบข้อมูลซ้ำ',
                    'data': {
                        'duplicate_info': existing
                    }
                }

            return {
                'success': True,
                'message': 'No duplicate found',
                'data': {}
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'ไม่สามารถตรวจสอบข้อมูลซ้ำได้: {str(e)}',
                'data': {}
            }

    def _check_dependencies(
        self,
        barcode: str,
        job_id: int
    ) -> Dict[str, Any]:
        """
        Check if all required job dependencies are satisfied

        Args:
            barcode: Barcode to check
            job_id: Current job ID

        Returns:
            Result dictionary with missing_dependencies if any
        """
        try:
            required_jobs = self.dependency_repo.get_required_jobs(job_id)

            if not required_jobs:
                # No dependencies, can scan
                return {
                    'success': True,
                    'message': 'No dependencies',
                    'data': {}
                }

            missing_dependencies = []

            # Check if all required jobs have been scanned for this barcode
            for required_job in required_jobs:
                required_job_id = required_job['required_job_id']
                required_job_name = required_job['job_name']

                duplicate = self.scan_log_repo.check_duplicate(
                    barcode=barcode,
                    job_id=required_job_id,
                    hours=24*365  # Check entire history
                )

                if duplicate is None:
                    missing_dependencies.append({
                        'job_id': required_job_id,
                        'job_name': required_job_name
                    })

            if missing_dependencies:
                # Build error message
                missing_names = [dep['job_name'] for dep in missing_dependencies]
                message = f"ไม่มีงาน {', '.join(missing_names)}"

                return {
                    'success': False,
                    'message': message,
                    'data': {
                        'missing_dependencies': missing_dependencies
                    }
                }

            # All dependencies satisfied
            return {
                'success': True,
                'message': 'All dependencies satisfied',
                'data': {}
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'ไม่สามารถตรวจสอบ dependencies ได้: {str(e)}',
                'data': {}
            }
