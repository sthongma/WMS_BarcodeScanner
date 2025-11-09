#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Repository Module
Provides base class for all repository implementations
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from .database_manager import DatabaseManager


class BaseRepository(ABC):
    """
    Base class for all repositories

    Provides common CRUD operations and database access patterns.
    Child classes should implement table-specific logic.
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize repository with database manager

        Args:
            db_manager: DatabaseManager instance for database operations
        """
        self.db = db_manager

    @property
    @abstractmethod
    def table_name(self) -> str:
        """
        Table name for this repository
        Must be implemented by child classes
        """
        pass

    # ========================================================================
    # Common CRUD Operations
    # ========================================================================

    def find_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """
        Find a single record by ID

        Args:
            record_id: The ID to search for

        Returns:
            Dictionary containing the record, or None if not found
        """
        query = f"SELECT * FROM {self.table_name} WHERE id = ?"
        results = self.db.execute_query(query, (record_id,))
        return results[0] if results else None

    def find_all(self, order_by: str = "id") -> List[Dict[str, Any]]:
        """
        Get all records from the table

        Args:
            order_by: Column name to order by (default: "id")

        Returns:
            List of dictionaries containing all records
        """
        query = f"SELECT * FROM {self.table_name} ORDER BY {order_by}"
        return self.db.execute_query(query)

    def find_where(
        self,
        conditions: Dict[str, Any],
        order_by: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find records matching conditions

        Args:
            conditions: Dictionary of column: value pairs to match
            order_by: Optional column name to order results

        Returns:
            List of matching records

        Example:
            repo.find_where({'is_active': 1, 'user_id': 5}, order_by='created_date')
        """
        where_clause = " AND ".join([f"{col} = ?" for col in conditions.keys()])
        query = f"SELECT * FROM {self.table_name} WHERE {where_clause}"

        if order_by:
            query += f" ORDER BY {order_by}"

        params = tuple(conditions.values())
        return self.db.execute_query(query, params)

    def count(self, conditions: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records, optionally with conditions

        Args:
            conditions: Optional dictionary of column: value pairs to filter

        Returns:
            Count of matching records
        """
        if conditions:
            where_clause = " AND ".join([f"{col} = ?" for col in conditions.keys()])
            query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE {where_clause}"
            params = tuple(conditions.values())
        else:
            query = f"SELECT COUNT(*) as count FROM {self.table_name}"
            params = ()

        results = self.db.execute_query(query, params)
        return results[0]['count'] if results else 0

    def insert(self, data: Dict[str, Any]) -> int:
        """
        Insert a new record

        Args:
            data: Dictionary of column: value pairs to insert

        Returns:
            Number of rows affected (typically 1)
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        params = tuple(data.values())
        return self.db.execute_non_query(query, params)

    def update(self, record_id: int, data: Dict[str, Any]) -> int:
        """
        Update an existing record by ID

        Args:
            record_id: ID of the record to update
            data: Dictionary of column: value pairs to update

        Returns:
            Number of rows affected
        """
        set_clause = ", ".join([f"{col} = ?" for col in data.keys()])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?"
        params = tuple(list(data.values()) + [record_id])
        return self.db.execute_non_query(query, params)

    def delete(self, record_id: int) -> int:
        """
        Delete a record by ID

        Args:
            record_id: ID of the record to delete

        Returns:
            Number of rows affected
        """
        query = f"DELETE FROM {self.table_name} WHERE id = ?"
        return self.db.execute_non_query(query, (record_id,))

    def exists(self, conditions: Dict[str, Any]) -> bool:
        """
        Check if a record exists matching conditions

        Args:
            conditions: Dictionary of column: value pairs to match

        Returns:
            True if at least one matching record exists
        """
        return self.count(conditions) > 0

    # ========================================================================
    # Raw Query Support
    # ========================================================================

    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict]:
        """
        Execute a custom SELECT query

        Args:
            query: SQL query string
            params: Query parameters tuple

        Returns:
            List of result dictionaries
        """
        return self.db.execute_query(query, params)

    def execute_non_query(self, query: str, params: Tuple = ()) -> int:
        """
        Execute a custom INSERT/UPDATE/DELETE query

        Args:
            query: SQL query string
            params: Query parameters tuple

        Returns:
            Number of rows affected
        """
        return self.db.execute_non_query(query, params)
