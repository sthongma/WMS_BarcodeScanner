#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Report Service Module
Handles business logic for report generation
"""

from typing import Dict, Optional, Any, List
from datetime import datetime
from ..database.scan_log_repository import ScanLogRepository
from ..database.job_type_repository import JobTypeRepository
from ..database.sub_job_repository import SubJobRepository
from .. import constants


class ReportService:
    """
    Service for handling report generation business logic

    Responsibilities:
    - Validate report parameters (date, job type, sub job)
    - Generate reports with various filters
    - Format report data
    - Calculate report statistics

    Note: This service contains NO UI logic.
    It only contains pure business logic and returns structured results.
    """

    def __init__(
        self,
        scan_log_repo: ScanLogRepository,
        job_type_repo: JobTypeRepository,
        sub_job_repo: SubJobRepository
    ):
        """
        Initialize ReportService with required repositories

        Args:
            scan_log_repo: Repository for scan log operations
            job_type_repo: Repository for job type operations
            sub_job_repo: Repository for sub job type operations
        """
        self.scan_log_repo = scan_log_repo
        self.job_type_repo = job_type_repo
        self.sub_job_repo = sub_job_repo

    def generate_report(
        self,
        report_date: str,
        job_id: int,
        sub_job_id: Optional[int] = None,
        notes_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a report for a specific date and job

        Args:
            report_date: Report date in YYYY-MM-DD format
            job_id: Job type ID to filter by
            sub_job_id: Optional sub job type ID to filter by
            notes_filter: Optional notes text to filter by

        Returns:
            Dictionary with:
            - success (bool): Whether the report was generated successfully
            - message (str): Human-readable message
            - data (dict): Report data with scans list and statistics
        """
        # Step 1: Validate inputs
        validation_result = self._validate_inputs(report_date, job_id, sub_job_id)
        if not validation_result['success']:
            return validation_result

        # Step 2: Parse and format date
        try:
            date_obj = datetime.strptime(report_date, constants.DATE_FORMAT)
            start_date = date_obj.strftime(constants.DATE_FORMAT)
            end_date = date_obj.strftime(constants.DATE_FORMAT)
        except ValueError:
            return {
                'success': False,
                'message': constants.ERROR_INVALID_DATE_FORMAT,
                'data': {}
            }

        # Step 3: Get report data
        try:
            if sub_job_id is not None:
                # Get report with specific sub job
                scans = self.scan_log_repo.get_report_with_sub_job(
                    start_date=start_date,
                    end_date=end_date,
                    job_id=job_id,
                    sub_job_id=sub_job_id
                )
            else:
                # Get report for all sub jobs of the main job
                scans = self.scan_log_repo.get_report_with_sub_job(
                    start_date=start_date,
                    end_date=end_date,
                    job_id=job_id
                )

            # Step 4: Apply notes filter if specified
            if notes_filter:
                scans = [
                    scan for scan in scans
                    if scan.get('notes') and notes_filter.lower() in scan['notes'].lower()
                ]

            # Step 5: Calculate statistics
            total_scans = len(scans)
            unique_barcodes = len(set(scan['barcode'] for scan in scans))

            # Get job and sub job names
            job_info = self.job_type_repo.find_by_id(job_id)
            job_name = job_info['job_name'] if job_info else 'Unknown'

            sub_job_name = None
            if sub_job_id is not None:
                sub_job_info = self.sub_job_repo.get_details(sub_job_id)
                sub_job_name = sub_job_info['sub_job_name'] if sub_job_info else 'Unknown'

            return {
                'success': True,
                'message': constants.INFO_DATA_FOUND.format(total_scans),
                'data': {
                    'report_date': report_date,
                    'job_id': job_id,
                    'job_name': job_name,
                    'sub_job_id': sub_job_id,
                    'sub_job_name': sub_job_name,
                    'notes_filter': notes_filter,
                    'scans': scans,
                    'statistics': {
                        'total_scans': total_scans,
                        'unique_barcodes': unique_barcodes
                    }
                }
            }

        except Exception as e:
            return {
                'success': False,
                'message': constants.ERROR_CREATE_REPORT.format(str(e)),
                'data': {}
            }

    def generate_date_range_report(
        self,
        start_date: str,
        end_date: str,
        job_id: int,
        sub_job_id: Optional[int] = None,
        notes_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a report for a date range

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            job_id: Job type ID to filter by
            sub_job_id: Optional sub job type ID to filter by
            notes_filter: Optional notes text to filter by

        Returns:
            Dictionary with success status, message, and report data
        """
        # Step 1: Validate dates
        try:
            start_obj = datetime.strptime(start_date, constants.DATE_FORMAT)
            end_obj = datetime.strptime(end_date, constants.DATE_FORMAT)

            if start_obj > end_obj:
                return {
                    'success': False,
                    'message': constants.ERROR_DATE_RANGE_INVALID,
                    'data': {}
                }
        except ValueError:
            return {
                'success': False,
                'message': constants.ERROR_INVALID_DATE_FORMAT,
                'data': {}
            }

        # Step 2: Validate job
        validation_result = self._validate_inputs(start_date, job_id, sub_job_id)
        if not validation_result['success']:
            return validation_result

        # Step 3: Get report data
        try:
            if sub_job_id is not None:
                scans = self.scan_log_repo.get_report_with_sub_job(
                    start_date=start_date,
                    end_date=end_date,
                    job_id=job_id,
                    sub_job_id=sub_job_id
                )
            else:
                scans = self.scan_log_repo.get_report_with_sub_job(
                    start_date=start_date,
                    end_date=end_date,
                    job_id=job_id
                )

            # Apply notes filter if specified
            if notes_filter:
                scans = [
                    scan for scan in scans
                    if scan.get('notes') and notes_filter.lower() in scan['notes'].lower()
                ]

            # Calculate statistics
            total_scans = len(scans)
            unique_barcodes = len(set(scan['barcode'] for scan in scans))

            # Get job and sub job names
            job_info = self.job_type_repo.find_by_id(job_id)
            job_name = job_info['job_name'] if job_info else 'Unknown'

            sub_job_name = None
            if sub_job_id is not None:
                sub_job_info = self.sub_job_repo.get_details(sub_job_id)
                sub_job_name = sub_job_info['sub_job_name'] if sub_job_info else 'Unknown'

            return {
                'success': True,
                'message': constants.INFO_DATA_FOUND.format(total_scans),
                'data': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'job_id': job_id,
                    'job_name': job_name,
                    'sub_job_id': sub_job_id,
                    'sub_job_name': sub_job_name,
                    'notes_filter': notes_filter,
                    'scans': scans,
                    'statistics': {
                        'total_scans': total_scans,
                        'unique_barcodes': unique_barcodes
                    }
                }
            }

        except Exception as e:
            return {
                'success': False,
                'message': constants.ERROR_CREATE_REPORT.format(str(e)),
                'data': {}
            }

    # Private helper methods

    def _validate_inputs(
        self,
        date_str: str,
        job_id: int,
        sub_job_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Validate report input parameters

        Args:
            date_str: Date string to validate
            job_id: Job ID to validate
            sub_job_id: Optional sub job ID to validate

        Returns:
            Result dictionary
        """
        # Validate date
        if not date_str or not date_str.strip():
            return {
                'success': False,
                'message': constants.ERROR_NO_DATE,
                'data': {}
            }

        # Validate job exists
        job_info = self.job_type_repo.find_by_id(job_id)
        if not job_info:
            return {
                'success': False,
                'message': constants.ERROR_JOB_NOT_FOUND.format(job_id),
                'data': {}
            }

        # Validate sub job if specified
        if sub_job_id is not None:
            sub_job_info = self.sub_job_repo.get_details(sub_job_id)
            if not sub_job_info:
                return {
                    'success': False,
                    'message': constants.ERROR_SUB_JOB_NOT_FOUND.format(sub_job_id),
                    'data': {}
                }

            # Validate sub job belongs to the main job
            if sub_job_info['main_job_id'] != job_id:
                return {
                    'success': False,
                    'message': constants.ERROR_SUB_JOB_MISMATCH,
                    'data': {}
                }

        return {
            'success': True,
            'message': 'Validation passed',
            'data': {}
        }
