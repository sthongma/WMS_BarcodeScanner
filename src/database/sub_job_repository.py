#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SubJob Repository Module
Handles all database operations for sub_job_types table
"""

from typing import Dict, List, Optional, Any
from .base_repository import BaseRepository
from .database_manager import DatabaseManager


class SubJobRepository(BaseRepository):
    """
    Repository for sub_job_types table

    Handles CRUD operations for sub job types including:
    - Listing sub jobs by main job
    - Finding sub jobs by ID or name
    - Creating new sub jobs
    - Soft deleting sub jobs (is_active = 0)
    - Checking for duplicates
    """

    @property
    def table_name(self) -> str:
        """Table name for sub job types"""
        return "sub_job_types"

    # ========================================================================
    # Sub Job Specific Operations
    # ========================================================================

    def get_by_main_job(
        self,
        main_job_id: int,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get all sub jobs for a specific main job

        Args:
            main_job_id: ID of the main job type
            active_only: If True, only return active sub jobs (default: True)

        Returns:
            List of sub job dictionaries with 'id' and 'sub_job_name'
        """
        if active_only:
            query = """
                SELECT id, sub_job_name
                FROM sub_job_types
                WHERE main_job_id = ? AND is_active = 1
                ORDER BY sub_job_name
            """
        else:
            query = """
                SELECT id, sub_job_name, is_active
                FROM sub_job_types
                WHERE main_job_id = ?
                ORDER BY sub_job_name
            """
        return self.db.execute_query(query, (main_job_id,))

    def find_by_name(
        self,
        main_job_id: int,
        sub_job_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find a sub job by name within a main job

        Args:
            main_job_id: ID of the main job type
            sub_job_name: Name of the sub job to find

        Returns:
            Sub job dictionary or None if not found
        """
        query = """
            SELECT * FROM sub_job_types
            WHERE main_job_id = ? AND sub_job_name = ? AND is_active = 1
        """
        results = self.db.execute_query(query, (main_job_id, sub_job_name))
        return results[0] if results else None

    def get_details(self, sub_job_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a sub job

        Args:
            sub_job_id: ID of the sub job

        Returns:
            Full sub job details including all columns
        """
        query = """
            SELECT id, main_job_id, sub_job_name, description,
                   created_date, updated_date, is_active
            FROM sub_job_types
            WHERE id = ?
        """
        results = self.db.execute_query(query, (sub_job_id,))
        return results[0] if results else None

    def create_sub_job(
        self,
        main_job_id: int,
        sub_job_name: str,
        description: str = ""
    ) -> int:
        """
        Create a new sub job type

        Args:
            main_job_id: ID of the main job type
            sub_job_name: Name of the sub job
            description: Optional description

        Returns:
            Number of rows affected (1 if successful)
        """
        query = """
            INSERT INTO sub_job_types
            (main_job_id, sub_job_name, description, created_date, updated_date, is_active)
            VALUES (?, ?, ?, GETDATE(), GETDATE(), 1)
        """
        return self.db.execute_non_query(query, (main_job_id, sub_job_name, description))

    def soft_delete(self, sub_job_id: int) -> int:
        """
        Soft delete a sub job (set is_active = 0)

        Args:
            sub_job_id: ID of the sub job to delete

        Returns:
            Number of rows affected

        Note:
            This does not actually delete the record, just marks it inactive
        """
        query = """
            UPDATE sub_job_types
            SET is_active = 0, updated_date = GETDATE()
            WHERE id = ?
        """
        return self.db.execute_non_query(query, (sub_job_id,))

    def activate(self, sub_job_id: int) -> int:
        """
        Reactivate a soft-deleted sub job

        Args:
            sub_job_id: ID of the sub job to activate

        Returns:
            Number of rows affected
        """
        query = """
            UPDATE sub_job_types
            SET is_active = 1, updated_date = GETDATE()
            WHERE id = ?
        """
        return self.db.execute_non_query(query, (sub_job_id,))

    def duplicate_exists(
        self,
        main_job_id: int,
        sub_job_name: str,
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        Check if a sub job name already exists for a main job

        Args:
            main_job_id: ID of the main job type
            sub_job_name: Sub job name to check
            exclude_id: Optional ID to exclude from check (for updates)

        Returns:
            True if duplicate exists
        """
        if exclude_id:
            query = """
                SELECT COUNT(*) as count FROM sub_job_types
                WHERE main_job_id = ? AND sub_job_name = ?
                AND is_active = 1 AND id != ?
            """
            results = self.db.execute_query(query, (main_job_id, sub_job_name, exclude_id))
        else:
            query = """
                SELECT COUNT(*) as count FROM sub_job_types
                WHERE main_job_id = ? AND sub_job_name = ? AND is_active = 1
            """
            results = self.db.execute_query(query, (main_job_id, sub_job_name))

        return results[0]['count'] > 0 if results else False

    def get_all_active(self) -> List[Dict[str, Any]]:
        """
        Get all active sub jobs across all main jobs

        Returns:
            List of active sub job dictionaries
        """
        query = """
            SELECT id, main_job_id, sub_job_name, description
            FROM sub_job_types
            WHERE is_active = 1
            ORDER BY sub_job_name
        """
        return self.db.execute_query(query)

    def update_sub_job(
        self,
        sub_job_id: int,
        sub_job_name: str,
        description: str = ""
    ) -> int:
        """
        Update a sub job's name and description

        Args:
            sub_job_id: ID of the sub job to update
            sub_job_name: New name for the sub job
            description: New description

        Returns:
            Number of rows affected
        """
        query = """
            UPDATE sub_job_types
            SET sub_job_name = ?, description = ?, updated_date = GETDATE()
            WHERE id = ?
        """
        return self.db.execute_non_query(query, (sub_job_name, description, sub_job_id))

    def get_active_count(self, main_job_id: Optional[int] = None) -> int:
        """
        Get count of active sub jobs

        Args:
            main_job_id: Optional main job ID to filter by

        Returns:
            Number of active sub jobs
        """
        if main_job_id:
            query = """
                SELECT COUNT(*) as count FROM sub_job_types
                WHERE main_job_id = ? AND is_active = 1
            """
            results = self.db.execute_query(query, (main_job_id,))
        else:
            query = "SELECT COUNT(*) as count FROM sub_job_types WHERE is_active = 1"
            results = self.db.execute_query(query)

        return results[0]['count'] if results else 0

    # ========================================================================
    # Table Management
    # ========================================================================

    def ensure_table_exists(self) -> bool:
        """
        Create sub_job_types table if it doesn't exist

        Returns:
            True if table exists or was created successfully
        """
        create_table_query = """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sub_job_types')
        BEGIN
            CREATE TABLE sub_job_types (
                id INT PRIMARY KEY IDENTITY(1,1),
                main_job_id INT NOT NULL,
                sub_job_name NVARCHAR(100) NOT NULL,
                description NVARCHAR(500),
                created_date DATETIME DEFAULT GETDATE(),
                updated_date DATETIME DEFAULT GETDATE(),
                is_active BIT DEFAULT 1,
                FOREIGN KEY (main_job_id) REFERENCES job_types(id) ON DELETE CASCADE,
                CONSTRAINT unique_sub_job UNIQUE (main_job_id, sub_job_name, is_active)
            )
        END
        """
        try:
            self.db.execute_non_query(create_table_query)
            return True
        except Exception:
            return False
