#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rate Limiter Middleware
Handles API rate limiting functionality
"""

import time
import logging
from collections import defaultdict
from functools import wraps
from flask import request, jsonify
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Rate limiting storage
request_counts = defaultdict(lambda: defaultdict(int))
request_times = defaultdict(list)


class RateLimiter:
    """Rate limiting class"""
    
    def __init__(self):
        self.request_times = defaultdict(list)
    
    def limit(self, max_requests: int = 60, per_seconds: int = 60):
        """Rate limiting decorator"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
                current_time = time.time()
                
                # ลบ request เก่าที่เกินช่วงเวลา
                cutoff_time = current_time - per_seconds
                self.request_times[client_ip] = [
                    req_time for req_time in self.request_times[client_ip] 
                    if req_time > cutoff_time
                ]
                
                # ตรวจสอบจำนวน request
                if len(self.request_times[client_ip]) >= max_requests:
                    logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                    return jsonify({
                        'success': False, 
                        'message': 'Rate limit exceeded. Please try again later.'
                    }), 429
                
                # บันทึก request ปัจจุบัน
                self.request_times[client_ip].append(current_time)
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator


# Centralized rate limit configuration
ENDPOINT_RATE_LIMITS = {
    # Scan endpoints
    'scan_barcode': {'max_requests': 120, 'per_seconds': 60},  # 2 scans/second
    'get_scan_history': {'max_requests': 100, 'per_seconds': 60},
    'get_today_summary': {'max_requests': 140, 'per_seconds': 60},  # มากกว่า scan เพราะใช้บ่อย
    'update_scan_record': {'max_requests': 120, 'per_seconds': 60},
    
    # Job endpoints
    'get_job_types': {'max_requests': 100, 'per_seconds': 60},
    'get_sub_job_types': {'max_requests': 100, 'per_seconds': 60},
    'create_job_type': {'max_requests': 50, 'per_seconds': 60},
    'create_sub_job_type': {'max_requests': 50, 'per_seconds': 60},
    
    # Report endpoints
    'generate_report': {'max_requests': 50, 'per_seconds': 60},
    'export_report': {'max_requests': 25, 'per_seconds': 60},  # ลดลงเพราะ export ใช้ resource มาก
    'get_monthly_summary': {'max_requests': 50, 'per_seconds': 60},
    'get_user_activity_report': {'max_requests': 50, 'per_seconds': 60},
    
    # Default fallback
    'default': {'max_requests': 60, 'per_seconds': 60}
}

# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(max_requests: int = 60, per_seconds: int = 60):
    """Rate limiting decorator function"""
    return rate_limiter.limit(max_requests, per_seconds)


def auto_rate_limit(func):
    """Auto rate limit decorator based on function name"""
    function_name = func.__name__
    config = ENDPOINT_RATE_LIMITS.get(function_name, ENDPOINT_RATE_LIMITS['default'])
    
    return rate_limiter.limit(
        max_requests=config['max_requests'], 
        per_seconds=config['per_seconds']
    )(func)


def get_rate_limit_info(client_ip: str = None) -> Dict[str, Any]:
    """ดึงข้อมูล rate limit ของ client"""
    if not client_ip:
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    
    current_time = time.time()
    recent_requests = [
        req_time for req_time in rate_limiter.request_times[client_ip]
        if req_time > current_time - 60  # requests in last minute
    ]
    
    return {
        'client_ip': client_ip,
        'requests_in_last_minute': len(recent_requests),
        'total_requests': len(rate_limiter.request_times[client_ip])
    }


def clear_expired_requests():
    """ลบ request records ที่หมดอายุ"""
    current_time = time.time()
    cutoff_time = current_time - 3600  # Keep records for 1 hour
    
    for client_ip in list(rate_limiter.request_times.keys()):
        rate_limiter.request_times[client_ip] = [
            req_time for req_time in rate_limiter.request_times[client_ip]
            if req_time > cutoff_time
        ]
        
        # Remove empty entries
        if not rate_limiter.request_times[client_ip]:
            del rate_limiter.request_times[client_ip]