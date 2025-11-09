#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JobType Repository Module
Handles all database operations for job_types table
"""

from typing import Dict, List, Optional, Any
from .base_repository import BaseRepository
from .database_manager import DatabaseManager


class JobTypeRepository(BaseRepository):
    """
    Repository for job_types table

    Handles CRUD operations for job types including:
    - Listing all job types
    - Finding job types by ID or name
    - Creating new job types
    - Deleting job types
    """

    @property
    def table_name(self) -> str:
        """Table name for job types"""
        return "job_types"

    # ========================================================================
    # Job Type Specific Operations
    # ========================================================================

    def get_all_job_types(self) -> List[Dict[str, Any]]:
        """
        Get all job types ordered by name

        Returns:
            List of job type dictionaries with 'id' and 'job_name'
        """
        query = "SELECT id, job_name FROM job_types ORDER BY job_name"
        return self.db.execute_query(query)

    def find_by_name(self, job_name: str) -> Optional[Dict[str, Any]]:
        """
        Find a job type by name

        Args:
            job_name: Name of the job type to find

        Returns:
            Job type dictionary or None if not found
        """
        query = "SELECT * FROM job_types WHERE job_name = ?"
        results = self.db.execute_query(query, (job_name,))
        return results[0] if results else None

    def create_job_type(self, job_name: str) -> int:
        """
        Create a new job type

        Args:
            job_name: Name of the job type

        Returns:
            Number of rows affected (1 if successful)
        """
        return self.insert({'job_name': job_name})

    def delete_job_type(self, job_type_id: int) -> int:
        """
        Delete a job type by ID

        Args:
            job_type_id: ID of the job type to delete

        Returns:
            Number of rows affected

        Note:
            This will cascade delete related records due to FK constraints
        """
        return self.delete(job_type_id)

    def job_name_exists(self, job_name: str, exclude_id: Optional[int] = None) -> bool:
        """
        Check if a job name already exists

        Args:
            job_name: Job name to check
            exclude_id: Optional ID to exclude from check (for updates)

        Returns:
            True if job name exists
        """
        if exclude_id:
            query = "SELECT COUNT(*) as count FROM job_types WHERE job_name = ? AND id != ?"
            results = self.db.execute_query(query, (job_name, exclude_id))
        else:
            query = "SELECT COUNT(*) as count FROM job_types WHERE job_name = ?"
            results = self.db.execute_query(query, (job_name,))

        return results[0]['count'] > 0 if results else False

    def get_job_type_count(self) -> int:
        """
        Get total count of job types

        Returns:
            Number of job types in the database
        """
        return self.count()

    # ========================================================================
    # Table Management
    # ========================================================================

    def ensure_table_exists(self) -> bool:
        """
        Create job_types table if it doesn't exist

        Returns:
            True if table exists or was created successfully
        """
        create_table_query = """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'job_types')
        BEGIN
            CREATE TABLE job_types (
                id INT PRIMARY KEY IDENTITY(1,1),
                job_name NVARCHAR(100) NOT NULL UNIQUE
            )
        END
        """
        try:
            self.db.execute_non_query(create_table_query)
            return True
        except Exception:
            return False
