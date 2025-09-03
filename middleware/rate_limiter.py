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
from flask import request, jsonify, render_template, redirect, url_for
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Rate limiting storage
request_counts = defaultdict(lambda: defaultdict(int))
request_times = defaultdict(list)


class RateLimiter:
    """Rate limiting class"""
    
    def __init__(self):
        self.request_times = defaultdict(lambda: defaultdict(list))
    
    def limit(self, max_requests: int = 60, per_seconds: int = 60, show_page: bool = False):
        """Rate limiting decorator"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
                endpoint_key = f.__name__
                current_time = time.time()
                
                # ลบ request เก่าที่เกินช่วงเวลา
                cutoff_time = current_time - per_seconds
                self.request_times[client_ip][endpoint_key] = [
                    req_time for req_time in self.request_times[client_ip][endpoint_key] 
                    if req_time > cutoff_time
                ]
                
                # ตรวจสอบจำนวน request
                if len(self.request_times[client_ip][endpoint_key]) >= max_requests:
                    # คำนวณเวลาที่ต้องรอ
                    oldest_request = min(self.request_times[client_ip][endpoint_key])
                    wait_time = int(per_seconds - (current_time - oldest_request))
                    
                    logger.warning(f"Rate limit exceeded for IP: {client_ip} on endpoint: {endpoint_key}")
                    
                    # ถ้าเป็น page request ให้แสดงหน้า rate limit
                    if show_page:
                        return render_template('rate_limit.html', 
                                             retry_after=wait_time,
                                             limit=max_requests,
                                             period=per_seconds), 429
                    
                    # ถ้าเป็น API request ให้ return JSON
                    return jsonify({
                        'success': False, 
                        'error': 'RATE_LIMIT_EXCEEDED',
                        'message': f'คุณใช้งานเร็วเกินไป กรุณารอ {wait_time} วินาที',
                        'details': {
                            'endpoint': endpoint_key,
                            'limit': max_requests,
                            'period': per_seconds,
                            'retry_after': wait_time,
                            'current_requests': len(self.request_times[client_ip][endpoint_key])
                        }
                    }), 429
                
                # บันทึก request ปัจจุบัน
                self.request_times[client_ip][endpoint_key].append(current_time)
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator


# Centralized rate limit configuration
ENDPOINT_RATE_LIMITS = {
    # Scan endpoints
    'scan_barcode': {'max_requests': 180, 'per_seconds': 60},  # 3 scans/second
    'get_scan_history': {'max_requests': 180, 'per_seconds': 60},  # เหมือนกับ scans เพราะใช้งานหนัก
    'get_today_summary': {'max_requests': 180, 'per_seconds': 60},  # เหมือนกับ scans เพราะใช้งานหนัก
    'update_scan_record': {'max_requests': 180, 'per_seconds': 60},  # เหมือนกับ scans เพราะใช้งานหนัก
    
    # Job endpoints
    'get_job_types': {'max_requests': 60, 'per_seconds': 60},
    'get_sub_job_types': {'max_requests': 180, 'per_seconds': 60},
    'create_job_type': {'max_requests': 60, 'per_seconds': 60},
    'create_sub_job_type': {'max_requests': 180, 'per_seconds': 60},
    
    # Report endpoints
    'generate_report': {'max_requests': 60, 'per_seconds': 60},
    'export_report': {'max_requests': 60, 'per_seconds': 60},
    'get_monthly_summary': {'max_requests': 60, 'per_seconds': 60},
    'get_user_activity_report': {'max_requests': 60, 'per_seconds': 60},
    
    # Default fallback
    'default': {'max_requests': 60, 'per_seconds': 60}
}

# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(max_requests: int = 60, per_seconds: int = 60, show_page: bool = False):
    """Rate limiting decorator function"""
    return rate_limiter.limit(max_requests, per_seconds, show_page)


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
    endpoint_info = {}
    
    for endpoint_key, requests in rate_limiter.request_times[client_ip].items():
        recent_requests = [
            req_time for req_time in requests
            if req_time > current_time - 60  # requests in last minute
        ]
        endpoint_info[endpoint_key] = {
            'requests_in_last_minute': len(recent_requests),
            'total_requests': len(requests)
        }
    
    return {
        'client_ip': client_ip,
        'endpoints': endpoint_info
    }


def clear_expired_requests():
    """ลบ request records ที่หมดอายุ"""
    current_time = time.time()
    cutoff_time = current_time - 3600  # Keep records for 1 hour
    
    for client_ip in list(rate_limiter.request_times.keys()):
        for endpoint_key in list(rate_limiter.request_times[client_ip].keys()):
            rate_limiter.request_times[client_ip][endpoint_key] = [
                req_time for req_time in rate_limiter.request_times[client_ip][endpoint_key]
                if req_time > cutoff_time
            ]
            
            # Remove empty endpoint entries
            if not rate_limiter.request_times[client_ip][endpoint_key]:
                del rate_limiter.request_times[client_ip][endpoint_key]
        
        # Remove empty client entries
        if not rate_limiter.request_times[client_ip]:
            del rate_limiter.request_times[client_ip]