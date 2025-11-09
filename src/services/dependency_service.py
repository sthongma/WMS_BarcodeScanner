#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dependency Service Module
Handles business logic for job dependency management
"""

from typing import Dict, List, Optional, Any
from ..database.dependency_repository import DependencyRepository
from ..database.job_type_repository import JobTypeRepository


class DependencyService:
    """
    Service for handling job dependency business logic

    Responsibilities:
    - Manage job dependencies (add, remove, validate)
    - Check circular dependencies
    - Get dependencies with scan status
    - Validate dependency operations

    Note: This service contains NO UI logic.
    It only contains pure business logic and returns structured results.
    """

    def __init__(
        self,
        dependency_repo: DependencyRepository,
        job_type_repo: JobTypeRepository
    ):
        """
        Initialize DependencyService with required repositories

        Args:
            dependency_repo: Repository for dependency operations
            job_type_repo: Repository for job type operations
        """
        self.dependency_repo = dependency_repo
        self.job_type_repo = job_type_repo

    def add_dependency(
        self,
        job_id: int,
        required_job_id: int
    ) -> Dict[str, Any]:
        """
        Add a dependency between jobs with validation

        Args:
            job_id: ID of the job
            required_job_id: ID of the job that is required

        Returns:
            Result dictionary with success status and message
        """
        # Validate that both jobs exist
        job_validation = self._validate_jobs_exist(job_id, required_job_id)
        if not job_validation['success']:
            return job_validation

        # Check if dependency already exists
        if self.dependency_repo.dependency_exists(job_id, required_job_id):
            return {
                'success': False,
                'message': 'Dependency already exists',
                'data': {}
            }

        # Check for circular dependency
        circular_check = self._check_circular_dependency(job_id, required_job_id)
        if not circular_check['success']:
            return circular_check

        # Add the dependency
        try:
            rowcount = self.dependency_repo.add_dependency(job_id, required_job_id)
            if rowcount > 0:
                return {
                    'success': True,
                    'message': 'Dependency added successfully',
                    'data': {
                        'job_id': job_id,
                        'required_job_id': required_job_id
                    }
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to add dependency',
                    'data': {}
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error adding dependency: {str(e)}',
                'data': {}
            }

    def remove_dependency(
        self,
        job_id: int,
        required_job_id: int
    ) -> Dict[str, Any]:
        """
        Remove a specific dependency

        Args:
            job_id: ID of the job
            required_job_id: ID of the required job to remove

        Returns:
            Result dictionary with success status and message
        """
        try:
            rowcount = self.dependency_repo.remove_dependency(job_id, required_job_id)
            if rowcount > 0:
                return {
                    'success': True,
                    'message': 'Dependency removed successfully',
                    'data': {
                        'job_id': job_id,
                        'required_job_id': required_job_id
                    }
                }
            else:
                return {
                    'success': False,
                    'message': 'Dependency not found',
                    'data': {}
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error removing dependency: {str(e)}',
                'data': {}
            }

    def remove_all_dependencies(self, job_id: int) -> Dict[str, Any]:
        """
        Remove all dependencies for a job

        Args:
            job_id: ID of the job to remove all dependencies for

        Returns:
            Result dictionary with success status and message
        """
        try:
            rowcount = self.dependency_repo.remove_all_dependencies(job_id)
            return {
                'success': True,
                'message': f'Removed {rowcount} dependencies',
                'data': {
                    'job_id': job_id,
                    'dependencies_removed': rowcount
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error removing dependencies: {str(e)}',
                'data': {}
            }

    def get_required_jobs(
        self,
        job_id: int,
        include_scan_status: bool = False,
        check_today_only: bool = True
    ) -> Dict[str, Any]:
        """
        Get all required jobs for a specific job

        Args:
            job_id: ID of the job to get requirements for
            include_scan_status: Whether to include scan status
            check_today_only: If True, check only today's scans

        Returns:
            Result dictionary with list of required jobs
        """
        try:
            if include_scan_status:
                required_jobs = self.dependency_repo.get_required_job_with_scan_status(
                    job_id, check_today_only
                )
            else:
                required_jobs = self.dependency_repo.get_required_jobs(job_id)

            return {
                'success': True,
                'message': f'Found {len(required_jobs)} required jobs',
                'data': {
                    'job_id': job_id,
                    'required_jobs': required_jobs,
                    'count': len(required_jobs)
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error getting required jobs: {str(e)}',
                'data': {}
            }

    def save_dependencies(
        self,
        job_id: int,
        required_job_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Save/update all dependencies for a job (replace existing)

        Args:
            job_id: ID of the job
            required_job_ids: List of required job IDs

        Returns:
            Result dictionary with success status and message
        """
        try:
            # First, remove all existing dependencies
            self.dependency_repo.remove_all_dependencies(job_id)

            # Then add new dependencies
            added_count = 0
            errors = []

            for required_job_id in required_job_ids:
                # Validate circular dependency
                if not self.dependency_repo.validate_no_circular_dependency(
                    job_id, required_job_id
                ):
                    errors.append(f'Circular dependency detected with job {required_job_id}')
                    continue

                # Add dependency
                try:
                    self.dependency_repo.add_dependency(job_id, required_job_id)
                    added_count += 1
                except Exception as e:
                    errors.append(f'Error adding dependency {required_job_id}: {str(e)}')

            return {
                'success': len(errors) == 0,
                'message': f'Added {added_count} dependencies' + (
                    f', {len(errors)} errors' if errors else ''
                ),
                'data': {
                    'job_id': job_id,
                    'dependencies_added': added_count,
                    'errors': errors
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error saving dependencies: {str(e)}',
                'data': {}
            }

    def get_all_dependencies(self) -> Dict[str, Any]:
        """
        Get all dependencies in the system

        Returns:
            Result dictionary with list of all dependencies
        """
        try:
            dependencies = self.dependency_repo.get_all_dependencies()
            return {
                'success': True,
                'message': f'Found {len(dependencies)} dependencies',
                'data': {
                    'dependencies': dependencies,
                    'count': len(dependencies)
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error getting dependencies: {str(e)}',
                'data': {}
            }

    # Private helper methods

    def _validate_jobs_exist(
        self,
        job_id: int,
        required_job_id: int
    ) -> Dict[str, Any]:
        """
        Validate that both jobs exist

        Args:
            job_id: ID of the main job
            required_job_id: ID of the required job

        Returns:
            Result dictionary
        """
        # Check if job exists
        job = self.job_type_repo.find_by_id(job_id)
        if not job:
            return {
                'success': False,
                'message': f'Job with ID {job_id} not found',
                'data': {}
            }

        # Check if required job exists
        required_job = self.job_type_repo.find_by_id(required_job_id)
        if not required_job:
            return {
                'success': False,
                'message': f'Required job with ID {required_job_id} not found',
                'data': {}
            }

        # Check if trying to add dependency to itself
        if job_id == required_job_id:
            return {
                'success': False,
                'message': 'Cannot add dependency to itself',
                'data': {}
            }

        return {
            'success': True,
            'message': 'Jobs exist',
            'data': {}
        }

    def _check_circular_dependency(
        self,
        job_id: int,
        required_job_id: int
    ) -> Dict[str, Any]:
        """
        Check if adding this dependency would create a circular reference

        Args:
            job_id: ID of the main job
            required_job_id: ID of the job to be required

        Returns:
            Result dictionary
        """
        is_valid = self.dependency_repo.validate_no_circular_dependency(
            job_id, required_job_id
        )

        if not is_valid:
            return {
                'success': False,
                'message': 'Cannot add dependency: would create circular reference',
                'data': {}
            }

        return {
            'success': True,
            'message': 'No circular dependency',
            'data': {}
        }
