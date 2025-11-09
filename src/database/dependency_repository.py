#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dependency Repository Module
Handles all database operations for job_dependencies table
"""

from typing import Dict, List, Optional, Any
from .base_repository import BaseRepository
from .database_manager import DatabaseManager


class DependencyRepository(BaseRepository):
    """
    Repository for job_dependencies table

    Handles CRUD operations for job dependencies including:
    - Getting required jobs for a job
    - Adding dependencies
    - Removing dependencies
    - Checking if required jobs have been scanned
    """

    @property
    def table_name(self) -> str:
        """Table name for job dependencies"""
        return "job_dependencies"

    # ========================================================================
    # Dependency Specific Operations
    # ========================================================================

    def get_required_jobs(self, job_id: int) -> List[Dict[str, Any]]:
        """
        Get all jobs required for a specific job

        Args:
            job_id: ID of the job to get requirements for

        Returns:
            List of dictionaries with 'required_job_id' and 'job_name'
        """
        query = """
            SELECT jd.required_job_id, jt.job_name
            FROM job_dependencies jd
            JOIN job_types jt ON jd.required_job_id = jt.id
            WHERE jd.job_id = ?
            ORDER BY jt.job_name
        """
        return self.db.execute_query(query, (job_id,))

    def get_required_job_with_scan_status(
        self,
        job_id: int,
        check_today_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get required jobs with their scan status

        Args:
            job_id: ID of the job to check
            check_today_only: If True, check only today's scans (default: True)

        Returns:
            List of dictionaries with job info and scan count
        """
        if check_today_only:
            query = """
                SELECT
                    jd.required_job_id,
                    jt.job_name,
                    (SELECT COUNT(*)
                     FROM scan_logs
                     WHERE job_id = jd.required_job_id
                     AND CAST(scan_date AS DATE) = CAST(GETDATE() AS DATE)) as scan_count
                FROM job_dependencies jd
                JOIN job_types jt ON jd.required_job_id = jt.id
                WHERE jd.job_id = ?
                ORDER BY jt.job_name
            """
        else:
            query = """
                SELECT
                    jd.required_job_id,
                    jt.job_name,
                    (SELECT COUNT(*)
                     FROM scan_logs
                     WHERE job_id = jd.required_job_id) as scan_count
                FROM job_dependencies jd
                JOIN job_types jt ON jd.required_job_id = jt.id
                WHERE jd.job_id = ?
                ORDER BY jt.job_name
            """
        return self.db.execute_query(query, (job_id,))

    def check_required_job_scanned(
        self,
        required_job_id: int,
        today_only: bool = True
    ) -> int:
        """
        Check if a required job has been scanned

        Args:
            required_job_id: ID of the required job
            today_only: If True, check only today's scans (default: True)

        Returns:
            Count of scans for the required job
        """
        if today_only:
            query = """
                SELECT COUNT(*) as count
                FROM scan_logs
                WHERE job_id = ?
                AND CAST(scan_date AS DATE) = CAST(GETDATE() AS DATE)
            """
        else:
            query = "SELECT COUNT(*) as count FROM scan_logs WHERE job_id = ?"

        results = self.db.execute_query(query, (required_job_id,))
        return results[0]['count'] if results else 0

    def add_dependency(self, job_id: int, required_job_id: int) -> int:
        """
        Add a dependency between jobs

        Args:
            job_id: ID of the job
            required_job_id: ID of the job that is required

        Returns:
            Number of rows affected (1 if successful)

        Note:
            Will fail if dependency already exists due to unique constraint
        """
        query = """
            INSERT INTO job_dependencies (job_id, required_job_id, created_date)
            VALUES (?, ?, GETDATE())
        """
        return self.db.execute_non_query(query, (job_id, required_job_id))

    def remove_dependency(self, job_id: int, required_job_id: int) -> int:
        """
        Remove a specific dependency

        Args:
            job_id: ID of the job
            required_job_id: ID of the required job to remove

        Returns:
            Number of rows affected
        """
        query = """
            DELETE FROM job_dependencies
            WHERE job_id = ? AND required_job_id = ?
        """
        return self.db.execute_non_query(query, (job_id, required_job_id))

    def remove_all_dependencies(self, job_id: int) -> int:
        """
        Remove all dependencies for a job

        Args:
            job_id: ID of the job to remove all dependencies for

        Returns:
            Number of rows affected
        """
        query = "DELETE FROM job_dependencies WHERE job_id = ?"
        return self.db.execute_non_query(query, (job_id,))

    def dependency_exists(self, job_id: int, required_job_id: int) -> bool:
        """
        Check if a dependency already exists

        Args:
            job_id: ID of the job
            required_job_id: ID of the required job

        Returns:
            True if dependency exists
        """
        query = """
            SELECT COUNT(*) as count
            FROM job_dependencies
            WHERE job_id = ? AND required_job_id = ?
        """
        results = self.db.execute_query(query, (job_id, required_job_id))
        return results[0]['count'] > 0 if results else False

    def get_dependencies_count(self, job_id: int) -> int:
        """
        Get count of dependencies for a job

        Args:
            job_id: ID of the job

        Returns:
            Number of required jobs
        """
        return self.count({'job_id': job_id})

    def get_all_dependencies(self) -> List[Dict[str, Any]]:
        """
        Get all job dependencies in the system

        Returns:
            List of all dependency records with job names
        """
        query = """
            SELECT
                jd.id,
                jd.job_id,
                jt1.job_name as job_name,
                jd.required_job_id,
                jt2.job_name as required_job_name,
                jd.created_date
            FROM job_dependencies jd
            JOIN job_types jt1 ON jd.job_id = jt1.id
            JOIN job_types jt2 ON jd.required_job_id = jt2.id
            ORDER BY jt1.job_name, jt2.job_name
        """
        return self.db.execute_query(query)

    def validate_no_circular_dependency(
        self,
        job_id: int,
        required_job_id: int
    ) -> bool:
        """
        Check if adding a dependency would create a circular reference

        Args:
            job_id: ID of the job
            required_job_id: ID of the job to be required

        Returns:
            True if no circular dependency would be created

        Example:
            If Job A requires Job B, and we try to make Job B require Job A,
            this would create a circular dependency and return False
        """
        # Check if required_job_id already requires job_id
        query = """
            SELECT COUNT(*) as count
            FROM job_dependencies
            WHERE job_id = ? AND required_job_id = ?
        """
        results = self.db.execute_query(query, (required_job_id, job_id))
        has_reverse = results[0]['count'] > 0 if results else False

        return not has_reverse

    # ========================================================================
    # Table Management
    # ========================================================================

    def ensure_table_exists(self) -> bool:
        """
        Create job_dependencies table if it doesn't exist

        Returns:
            True if table exists or was created successfully
        """
        create_table_query = """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'job_dependencies')
        BEGIN
            CREATE TABLE job_dependencies (
                id INT PRIMARY KEY IDENTITY(1,1),
                job_id INT NOT NULL,
                required_job_id INT NOT NULL,
                created_date DATETIME DEFAULT GETDATE(),
                FOREIGN KEY (job_id) REFERENCES job_types(id),
                FOREIGN KEY (required_job_id) REFERENCES job_types(id),
                CONSTRAINT unique_job_dependency UNIQUE (job_id, required_job_id)
            )
        END
        """
        try:
            self.db.execute_non_query(create_table_query)
            return True
        except Exception:
            return False
