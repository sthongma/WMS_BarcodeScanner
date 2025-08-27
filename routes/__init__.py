"""
Routes package for WMS Barcode Scanner Web Application
Contains API route handlers
"""

from .auth_routes import auth_bp
from .job_routes import job_bp
from .scan_routes import scan_bp
from .report_routes import report_bp

__all__ = ['auth_bp', 'job_bp', 'scan_bp', 'report_bp']