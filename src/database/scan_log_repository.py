#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ScanLog Repository Module
Handles all database operations for scan_logs table
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from .base_repository import BaseRepository
from .database_manager import DatabaseManager


class ScanLogRepository(BaseRepository):
    """
    Repository for scan_logs table

    Handles CRUD operations for scan logs including:
    - Creating scan records
    - Retrieving scan history with filtering
    - Generating reports
    - Checking for duplicates
    - Getting summary statistics
    """

    @property
    def table_name(self) -> str:
        """Table name for scan logs"""
        return "scan_logs"

    # ========================================================================
    # Scan Log Specific Operations
    # ========================================================================

    def create_scan(
        self,
        barcode: str,
        job_type: str,
        user_id: str,
        job_id: int,
        sub_job_id: Optional[int] = None,
        notes: str = ""
    ) -> int:
        """
        Create a new scan log entry

        Args:
            barcode: The barcode that was scanned
            job_type: Type of job (from job_types table)
            user_id: ID of the user performing the scan
            job_id: ID of the job type
            sub_job_id: Optional ID of the sub job type
            notes: Optional notes about the scan

        Returns:
            Number of rows affected (1 if successful)
        """
        query = """
            INSERT INTO scan_logs
            (barcode, scan_date, job_type, user_id, job_id, sub_job_id, notes)
            VALUES (?, GETDATE(), ?, ?, ?, ?, ?)
        """
        return self.db.execute_non_query(
            query,
            (barcode, job_type, user_id, job_id, sub_job_id, notes)
        )

    def get_recent_scans(
        self,
        limit: int = 50,
        include_sub_job_name: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get recent scan logs with optional sub job name

        Args:
            limit: Maximum number of records to return (default: 50)
            include_sub_job_name: Include sub job name via JOIN (default: True)

        Returns:
            List of scan log dictionaries
        """
        if include_sub_job_name:
            query = f"""
                SELECT TOP {limit} sl.*, sjt.sub_job_name
                FROM scan_logs sl
                LEFT JOIN sub_job_types sjt ON sl.sub_job_id = sjt.id
                ORDER BY sl.scan_date DESC
            """
        else:
            query = f"""
                SELECT TOP {limit} *
                FROM scan_logs
                ORDER BY scan_date DESC
            """
        return self.db.execute_query(query)

    def check_duplicate(
        self,
        barcode: str,
        job_id: int,
        hours: int = 24
    ) -> Optional[Dict[str, Any]]:
        """
        Check if barcode was scanned recently for the same job

        Args:
            barcode: Barcode to check
            job_id: Job ID to check
            hours: Time window in hours to check (default: 24)

        Returns:
            Existing scan record if found, None otherwise
        """
        query = """
            SELECT TOP 1 *
            FROM scan_logs
            WHERE barcode = ? AND job_id = ?
            AND scan_date >= DATEADD(HOUR, ?, GETDATE())
            ORDER BY scan_date DESC
        """
        results = self.db.execute_query(query, (barcode, job_id, -hours))
        return results[0] if results else None

    def search_history(
        self,
        barcode: Optional[str] = None,
        job_id: Optional[int] = None,
        sub_job_id: Optional[int] = None,
        user_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search scan logs with multiple filters

        Args:
            barcode: Filter by barcode (supports partial match with LIKE)
            job_id: Filter by job type ID
            sub_job_id: Filter by sub job type ID
            user_id: Filter by user ID
            start_date: Filter by start date (YYYY-MM-DD)
            end_date: Filter by end date (YYYY-MM-DD)
            limit: Maximum records to return

        Returns:
            List of matching scan logs with sub job name
        """
        conditions = []
        params = []

        if barcode:
            conditions.append("sl.barcode LIKE ?")
            params.append(f"%{barcode}%")

        if job_id is not None:
            conditions.append("sl.job_id = ?")
            params.append(job_id)

        if sub_job_id is not None:
            conditions.append("sl.sub_job_id = ?")
            params.append(sub_job_id)

        if user_id:
            conditions.append("sl.user_id = ?")
            params.append(user_id)

        if start_date:
            conditions.append("CAST(sl.scan_date AS DATE) >= ?")
            params.append(start_date)

        if end_date:
            conditions.append("CAST(sl.scan_date AS DATE) <= ?")
            params.append(end_date)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
            SELECT TOP {limit} sl.*, sjt.sub_job_name
            FROM scan_logs sl
            LEFT JOIN sub_job_types sjt ON sl.sub_job_id = sjt.id
            WHERE {where_clause}
            ORDER BY sl.scan_date DESC
        """

        return self.db.execute_query(query, tuple(params))

    def get_report_with_sub_job(
        self,
        start_date: str,
        end_date: str,
        job_id: Optional[int] = None,
        sub_job_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get report data with sub job information

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            job_id: Optional filter by job ID
            sub_job_id: Optional filter by sub job ID

        Returns:
            List of scan logs with sub job names
        """
        conditions = ["CAST(sl.scan_date AS DATE) BETWEEN ? AND ?"]
        params = [start_date, end_date]

        if job_id is not None:
            conditions.append("sl.job_id = ?")
            params.append(job_id)

        if sub_job_id is not None:
            conditions.append("sl.sub_job_id = ?")
            params.append(sub_job_id)

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT sl.*, sjt.sub_job_name
            FROM scan_logs sl
            LEFT JOIN sub_job_types sjt ON sl.sub_job_id = sjt.id
            WHERE {where_clause}
            ORDER BY sl.scan_date DESC
        """

        return self.db.execute_query(query, tuple(params))

    def get_report_main_job_only(
        self,
        start_date: str,
        end_date: str,
        job_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get report data for main job only (no sub job filter)

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            job_id: Job type ID

        Returns:
            List of scan logs
        """
        query = """
            SELECT sl.*
            FROM scan_logs sl
            WHERE sl.job_id = ?
            AND CAST(sl.scan_date AS DATE) BETWEEN ? AND ?
            ORDER BY sl.scan_date DESC
        """
        return self.db.execute_query(query, (job_id, start_date, end_date))

    def get_today_summary_count(
        self,
        job_id: int,
        sub_job_id: Optional[int] = None,
        notes_filter: Optional[str] = None
    ) -> int:
        """
        Get count of scans for today

        Args:
            job_id: Job type ID
            sub_job_id: Optional sub job type ID
            notes_filter: Optional notes filter (LIKE search)

        Returns:
            Count of scans today
        """
        if sub_job_id is not None:
            query = """
                SELECT COUNT(*) as total_count
                FROM scan_logs
                WHERE job_id = ? AND sub_job_id = ?
                AND CAST(scan_date AS DATE) = CAST(GETDATE() AS DATE)
            """
            params = [job_id, sub_job_id]
        else:
            query = """
                SELECT COUNT(*) as total_count
                FROM scan_logs
                WHERE job_id = ?
                AND CAST(scan_date AS DATE) = CAST(GETDATE() AS DATE)
            """
            params = [job_id]

        # Add notes filter if specified
        if notes_filter:
            query = query.rstrip() + " AND notes LIKE ?"
            params.append(f"%{notes_filter}%")

        results = self.db.execute_query(query, tuple(params))
        return results[0]['total_count'] if results else 0

    def get_count_by_job(
        self,
        job_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> int:
        """
        Get count of scans for a specific job

        Args:
            job_id: Job type ID
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)

        Returns:
            Count of scans
        """
        if start_date and end_date:
            query = """
                SELECT COUNT(*) as count
                FROM scan_logs
                WHERE job_id = ?
                AND CAST(scan_date AS DATE) BETWEEN ? AND ?
            """
            params = (job_id, start_date, end_date)
        else:
            query = "SELECT COUNT(*) as count FROM scan_logs WHERE job_id = ?"
            params = (job_id,)

        results = self.db.execute_query(query, params)
        return results[0]['count'] if results else 0

    # ========================================================================
    # Table Management
    # ========================================================================

    def ensure_table_exists(self) -> bool:
        """
        Create scan_logs table if it doesn't exist

        Returns:
            True if table exists or was created successfully
        """
        create_table_query = """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'scan_logs')
        BEGIN
            CREATE TABLE scan_logs (
                id INT PRIMARY KEY IDENTITY(1,1),
                barcode NVARCHAR(100) NOT NULL,
                scan_date DATETIME DEFAULT GETDATE(),
                job_type NVARCHAR(100),
                user_id NVARCHAR(50),
                job_id INT,
                sub_job_id INT,
                notes NVARCHAR(500),
                FOREIGN KEY (job_id) REFERENCES job_types(id),
                FOREIGN KEY (sub_job_id) REFERENCES sub_job_types(id)
            )
        END
        """
        try:
            self.db.execute_non_query(create_table_query)
            return True
        except Exception:
            return False

    def ensure_indexes_exist(self) -> bool:
        """
        Create performance indexes on scan_logs table

        Returns:
            True if indexes exist or were created successfully
        """
        indexes = [
            "CREATE NONCLUSTERED INDEX idx_scan_logs_barcode ON scan_logs(barcode)",
            "CREATE NONCLUSTERED INDEX idx_scan_logs_scan_date ON scan_logs(scan_date)",
            "CREATE NONCLUSTERED INDEX idx_scan_logs_job_type ON scan_logs(job_type)",
            "CREATE NONCLUSTERED INDEX idx_scan_logs_user_id ON scan_logs(user_id)",
            "CREATE NONCLUSTERED INDEX idx_scan_logs_job_id ON scan_logs(job_id)",
            "CREATE NONCLUSTERED INDEX idx_scan_logs_sub_job_id ON scan_logs(sub_job_id)"
        ]

        try:
            for index_query in indexes:
                # Check if index exists first
                index_name = index_query.split()[2]  # Extract index name
                check_query = f"""
                IF NOT EXISTS (
                    SELECT * FROM sys.indexes
                    WHERE name = '{index_name}' AND object_id = OBJECT_ID('scan_logs')
                )
                BEGIN
                    {index_query}
                END
                """
                self.db.execute_non_query(check_query)
            return True
        except Exception:
            return False
