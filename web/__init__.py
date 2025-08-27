"""
Web package for WMS Barcode Scanner
Contains web application components and services
"""

from .database_service import get_db_manager, initialize_database, ensure_tables_exist, get_connection_status

__all__ = ['get_db_manager', 'initialize_database', 'ensure_tables_exist', 'get_connection_status']