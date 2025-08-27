"""
Database package for WMS Barcode Scanner
Handles all database operations and connections
"""

from .database_manager import DatabaseManager
from .connection_config import ConnectionConfig

def get_db_instance(connection_info=None):
    """Helper function to get DatabaseManager singleton instance"""
    return DatabaseManager.get_instance(connection_info)

__all__ = ['DatabaseManager', 'ConnectionConfig', 'get_db_instance'] 