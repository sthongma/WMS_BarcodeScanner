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


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(max_requests: int = 60, per_seconds: int = 60):
    """Rate limiting decorator function"""
    return rate_limiter.limit(max_requests, per_seconds)


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