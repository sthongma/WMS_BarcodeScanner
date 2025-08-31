#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authentication Middleware
Handles authentication checks for protected routes
"""

from functools import wraps
from flask import session, jsonify, request, redirect
import logging

logger = logging.getLogger(__name__)


def require_auth(f):
    """
    Decorator to require authentication for API endpoints
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated (has db_config in session)
        if 'db_config' not in session:
            logger.warning(f"Unauthenticated access attempt to {request.endpoint}")
            
            # For API calls, return JSON response
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'message': 'กรุณาเข้าสู่ระบบก่อน',
                    'authenticated': False
                }), 401
            
            # For page requests, redirect to login
            return redirect('/login')
        
        # Verify session is still valid by checking database connection
        try:
            from web.database_service import get_db_manager
            db_manager = get_db_manager("Middleware: auth_middleware")
            
            if not db_manager or not db_manager.test_connection():
                logger.warning(f"Database connection failed for session user")
                session.clear()
                
                if request.path.startswith('/api/'):
                    return jsonify({
                        'success': False,
                        'message': 'การเชื่อมต่อฐานข้อมูลหมดอายุ กรุณาเข้าสู่ระบบใหม่',
                        'authenticated': False
                    }), 401
                
                return redirect('/login')
                
        except Exception as e:
            logger.error(f"Auth middleware error: {str(e)}")
            session.clear()
            
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'message': 'เกิดข้อผิดพลาดในการตรวจสอบสิทธิ์',
                    'authenticated': False
                }), 401
            
            return redirect('/login')
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_session_auth(f):
    """
    Lightweight decorator that only checks session without database verification
    Use for frequently called endpoints where performance is important
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'db_config' not in session:
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'message': 'กรุณาเข้าสู่ระบบก่อน',
                    'authenticated': False
                }), 401
            return redirect('/login')
        
        return f(*args, **kwargs)
    
    return decorated_function


def get_current_user():
    """
    Get current authenticated user information
    Returns None if not authenticated
    """
    if 'db_config' in session:
        db_config = session['db_config']
        return {
            'username': db_config.get('username', ''),
            'server': db_config.get('server', ''),
            'database': db_config.get('database', '')
        }
    return None


def is_authenticated():
    """
    Check if current session is authenticated
    """
    return 'db_config' in session