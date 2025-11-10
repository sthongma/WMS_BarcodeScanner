#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import Service Module
Handles business logic for data import/export operations
"""

from typing import Dict, List, Optional, Any
from ..database.job_type_repository import JobTypeRepository
from ..database.sub_job_repository import SubJobRepository
from ..database.scan_log_repository import ScanLogRepository
from .. import constants


class ImportService:
    """
    Service for handling import/export business logic

    Responsibilities:
    - Validate import data (structure and content)
    - Validate individual import rows
    - Process bulk import operations
    - Generate template data for exports

    Note: This service contains NO UI logic and NO file I/O.
    It only contains pure business logic and returns structured results.
    File reading/writing should be handled by the UI layer.
    """

    def __init__(
        self,
        job_type_repo: JobTypeRepository,
        sub_job_repo: SubJobRepository,
        scan_log_repo: ScanLogRepository
    ):
        """
        Initialize ImportService with required repositories

        Args:
            job_type_repo: Repository for job type operations
            sub_job_repo: Repository for sub job type operations
            scan_log_repo: Repository for scan log operations
        """
        self.job_type_repo = job_type_repo
        self.sub_job_repo = sub_job_repo
        self.scan_log_repo = scan_log_repo

    def validate_import_data(
        self,
        data: List[Dict[str, Any]],
        required_columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate import data structure and content

        Args:
            data: List of dictionaries representing rows to import
            required_columns: Optional list of required column names
                            Default: ['barcode', 'main_job_id', 'sub_job_id']

        Returns:
            Dictionary with:
            - success (bool): Whether validation was successful
            - message (str): Summary message
            - data (dict): Detailed validation results
        """
        if required_columns is None:
            required_columns = constants.REQUIRED_IMPORT_COLUMNS

        # Check if data is empty
        if not data:
            return {
                'success': False,
                'message': constants.ERROR_NO_IMPORT_DATA,
                'data': {
                    'valid_rows': 0,
                    'invalid_rows': 0,
                    'total_rows': 0,
                    'validation_results': []
                }
            }

        # Validate each row
        validation_results = []
        valid_count = 0
        invalid_count = 0

        for idx, row in enumerate(data, start=1):
            row_result = self.validate_import_row(row, idx, required_columns)
            validation_results.append(row_result)

            if row_result['valid']:
                valid_count += 1
            else:
                invalid_count += 1

        total_rows = len(data)
        all_valid = invalid_count == 0

        return {
            'success': all_valid,
            'message': constants.SUCCESS_VALIDATION_COMPLETE.format(valid_count, invalid_count),
            'data': {
                'valid_rows': valid_count,
                'invalid_rows': invalid_count,
                'total_rows': total_rows,
                'validation_results': validation_results,
                'all_valid': all_valid
            }
        }

    def validate_import_row(
        self,
        row: Dict[str, Any],
        row_number: int,
        required_columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate a single import row

        Args:
            row: Dictionary representing a single row
            row_number: Row number for error reporting
            required_columns: List of required column names

        Returns:
            Dictionary with validation result
        """
        if required_columns is None:
            required_columns = constants.REQUIRED_IMPORT_COLUMNS

        result = {
            'valid': True,
            'row_number': row_number,
            'errors': [],
            'warnings': []
        }

        # Extract and clean values
        barcode = str(row.get('barcode', '')).strip()
        main_job_id_str = str(row.get('main_job_id', '')).strip()
        sub_job_id_str = str(row.get('sub_job_id', '')).strip()
        notes = str(row.get('notes', '')).strip() if 'notes' in row else ''

        # Validate required fields
        if not barcode or barcode == 'nan':
            result['valid'] = False
            result['errors'].append('ไม่มีบาร์โค้ด')

        if not main_job_id_str or main_job_id_str == 'nan':
            result['valid'] = False
            result['errors'].append('ไม่มี ID ประเภทงานหลัก')

        if not sub_job_id_str or sub_job_id_str == 'nan':
            result['valid'] = False
            result['errors'].append('ไม่มี ID ประเภทงานย่อย')

        # If basic validation failed, return early
        if not result['valid']:
            return result

        # Validate IDs are numeric
        main_job_id = None
        sub_job_id = None

        try:
            main_job_id = int(float(main_job_id_str))
        except (ValueError, TypeError):
            result['valid'] = False
            result['errors'].append(f'ID ประเภทงานหลักไม่ถูกต้อง: {main_job_id_str}')

        try:
            sub_job_id = int(float(sub_job_id_str))
        except (ValueError, TypeError):
            result['valid'] = False
            result['errors'].append(f'ID ประเภทงานย่อยไม่ถูกต้อง: {sub_job_id_str}')

        # If ID parsing failed, return early
        if not result['valid']:
            return result

        # Validate job types exist
        try:
            job_info = self.job_type_repo.find_by_id(main_job_id)
            if not job_info:
                result['valid'] = False
                result['errors'].append(f'ไม่พบประเภทงานหลัก ID: {main_job_id}')
            else:
                result['main_job_name'] = job_info['job_name']
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f'ไม่สามารถตรวจสอบประเภทงานหลักได้: {str(e)}')

        # Validate sub job exists and belongs to main job
        try:
            sub_job_info = self.sub_job_repo.get_details(sub_job_id)
            if not sub_job_info:
                result['valid'] = False
                result['errors'].append(f'ไม่พบประเภทงานย่อย ID: {sub_job_id}')
            else:
                result['sub_job_name'] = sub_job_info['sub_job_name']

                # Check if sub job is active
                if not sub_job_info.get('is_active', True):
                    result['valid'] = False
                    result['errors'].append(f'ประเภทงานย่อย ID {sub_job_id} ถูกปิดการใช้งาน')

                # Check if sub job belongs to main job
                if sub_job_info['main_job_id'] != main_job_id:
                    result['valid'] = False
                    result['errors'].append(
                        f'ประเภทงานย่อย ID {sub_job_id} ไม่สัมพันธ์กับประเภทงานหลัก ID {main_job_id}'
                    )
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f'ไม่สามารถตรวจสอบประเภทงานย่อยได้: {str(e)}')

        # Store validated data
        if result['valid']:
            result['validated_data'] = {
                'barcode': barcode,
                'main_job_id': main_job_id,
                'sub_job_id': sub_job_id,
                'notes': notes
            }

        return result

    def import_scans(
        self,
        validated_rows: List[Dict[str, Any]],
        user_id: str,
        job_type_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Import validated scan data into database

        Args:
            validated_rows: List of validated row results from validate_import_row
            user_id: User ID performing the import
            job_type_name: Optional job type name (will be looked up if not provided)

        Returns:
            Dictionary with import results
        """
        if not validated_rows:
            return {
                'success': False,
                'message': constants.ERROR_NO_VALID_DATA,
                'data': {
                    'imported_count': 0,
                    'failed_count': 0,
                    'errors': []
                }
            }

        imported_count = 0
        failed_count = 0
        errors = []

        for row_result in validated_rows:
            # Skip invalid rows
            if not row_result.get('valid', False):
                failed_count += 1
                errors.append({
                    'row_number': row_result['row_number'],
                    'error': 'Row failed validation'
                })
                continue

            validated_data = row_result.get('validated_data', {})
            if not validated_data:
                failed_count += 1
                errors.append({
                    'row_number': row_result['row_number'],
                    'error': 'No validated data found'
                })
                continue

            # Get job type name if not provided
            if not job_type_name:
                job_info = self.job_type_repo.find_by_id(validated_data['main_job_id'])
                current_job_type_name = job_info['job_name'] if job_info else 'Unknown'
            else:
                current_job_type_name = job_type_name

            # Import the scan
            try:
                self.scan_log_repo.create_scan(
                    barcode=validated_data['barcode'],
                    job_type=current_job_type_name,
                    user_id=user_id,
                    job_id=validated_data['main_job_id'],
                    sub_job_id=validated_data['sub_job_id'],
                    notes=validated_data.get('notes', '')
                )
                imported_count += 1
            except Exception as e:
                failed_count += 1
                errors.append({
                    'row_number': row_result['row_number'],
                    'error': f'ไม่สามารถบันทึกข้อมูลได้: {str(e)}'
                })

        total_processed = imported_count + failed_count
        success = failed_count == 0

        return {
            'success': success,
            'message': constants.SUCCESS_IMPORT_COMPLETE.format(imported_count, failed_count),
            'data': {
                'imported_count': imported_count,
                'failed_count': failed_count,
                'total_processed': total_processed,
                'errors': errors
            }
        }

    def generate_template_data(self) -> Dict[str, Any]:
        """
        Generate template data for Excel export

        Returns:
            Dictionary with template information including job types and sub jobs
        """
        try:
            # Get all job types
            job_types = self.job_type_repo.get_all_job_types()

            # Get all active sub job types
            sub_jobs = self.sub_job_repo.get_all_active()

            # Build template information
            template_info = {
                'job_types': job_types,
                'sub_jobs': sub_jobs,
                'columns': constants.TEMPLATE_COLUMNS,
                'sample_data': [
                    {
                        'barcode': 'BC001',
                        'main_job_id': job_types[0]['id'] if job_types else 1,
                        'sub_job_id': sub_jobs[0]['id'] if sub_jobs else 1,
                        'notes': 'ตัวอย่างหมายเหตุ'
                    }
                ] if job_types and sub_jobs else []
            }

            return {
                'success': True,
                'message': f'สร้างข้อมูล template สำเร็จ: {len(job_types)} งานหลัก, {len(sub_jobs)} งานย่อย',
                'data': template_info
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'ไม่สามารถสร้างข้อมูล template ได้: {str(e)}',
                'data': {}
            }
