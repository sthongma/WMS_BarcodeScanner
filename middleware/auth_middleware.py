#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authentication Middleware
Handles authentication checks for protected routes
"""

from functools import wraps
from flask import session, jsonify, request, redirect
import logging
import time
from threading import Lock

logger = logging.getLogger(__name__)

# Auth cache with thread safety
_auth_cache = {}
_cache_lock = Lock()
CACHE_DURATION = 5  # Cache auth check for 5 seconds


def _get_cache_key():
    """Generate cache key for current session"""
    if 'db_config' not in session:
        return None
    config = session['db_config']
    return f"{config.get('server', '')}_{config.get('database', '')}_{config.get('username', '')}"

def _is_auth_cached():
    """Check if authentication is cached and valid"""
    cache_key = _get_cache_key()
    if not cache_key:
        return False
    
    with _cache_lock:
        cached_data = _auth_cache.get(cache_key)
        if not cached_data:
            return False
        
        # Check if cache is still valid
        if time.time() - cached_data['timestamp'] < CACHE_DURATION:
            logger.debug(f"🚀 Auth cache hit for: {cache_key}")
            return cached_data['authenticated']
        else:
            # Cache expired, remove it
            del _auth_cache[cache_key]
            return False

def _cache_auth_result(authenticated: bool):
    """Cache authentication result"""
    cache_key = _get_cache_key()
    if cache_key:
        with _cache_lock:
            _auth_cache[cache_key] = {
                'authenticated': authenticated,
                'timestamp': time.time()
            }

def require_auth(f):
    """
    Decorator to require authentication for API endpoints with caching
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
        
        # Check cache first to avoid duplicate DB checks
        if _is_auth_cached():
            return f(*args, **kwargs)
        
        # Verify session is still valid by checking database connection
        try:
            from web.database_service import get_db_manager
            db_manager = get_db_manager(f"Middleware: auth_middleware ({request.endpoint})")
            
            if not db_manager or not db_manager.test_connection():
                logger.warning(f"Database connection failed for session user")
                session.clear()
                _cache_auth_result(False)
                
                if request.path.startswith('/api/'):
                    return jsonify({
                        'success': False,
                        'message': 'การเชื่อมต่อฐานข้อมูลหมดอายุ กรุณาเข้าสู่ระบบใหม่',
                        'authenticated': False
                    }), 401
                
                return redirect('/login')
            
            # Cache successful authentication
            _cache_auth_result(True)
                
        except Exception as e:
            logger.error(f"Auth middleware error: {str(e)}")
            session.clear()
            _cache_auth_result(False)
            
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