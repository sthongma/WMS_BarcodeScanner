#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom Redis Session Interface for Flask
Compatible with all Flask versions
"""

import json
import pickle
from datetime import datetime, timedelta
from uuid import uuid4

from flask.sessions import SessionInterface, SessionMixin


class RedisSession(dict, SessionMixin):
    """Redis-backed session implementation"""
    
    def __init__(self, initial=None, sid=None, new=False):
        def on_update(self):
            self.modified = True
        
        dict.__init__(self, initial or ())
        self.modified = False
        self.new = new
        self.sid = sid


class RedisSessionInterface(SessionInterface):
    """Redis session interface for Flask"""
    
    serializer = json
    session_class = RedisSession
    
    def __init__(self, redis_client, key_prefix='wms_session:', use_signer=False):
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.use_signer = use_signer
        
    def generate_sid(self):
        return str(uuid4())
    
    def get_redis_expiration_time(self, app, session):
        if session.permanent:
            return app.permanent_session_lifetime
        return timedelta(hours=2)  # Default 2 hours
    
    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            sid = self.generate_sid()
            return self.session_class(sid=sid, new=True)
        
        try:
            key = self.key_prefix + sid
            val = self.redis.get(key)
            if val is not None:
                try:
                    data = self.serializer.loads(val)
                    return self.session_class(data, sid=sid)
                except (ValueError, TypeError):
                    # Invalid data, create new session
                    pass
        except Exception:
            # Redis error, create new session
            pass
        
        return self.session_class(sid=sid, new=True)
    
    def save_session(self, app, session, response):
        if not session:
            if session.modified:
                try:
                    key = self.key_prefix + session.sid
                    self.redis.delete(key)
                except Exception:
                    pass
            return
        
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)
        samesite = self.get_cookie_samesite(app)
        
        # Calculate expiration
        expires = self.get_expiration_time(app, session)
        
        # Save to Redis
        try:
            key = self.key_prefix + session.sid
            val = self.serializer.dumps(dict(session))
            
            if expires:
                expire_seconds = int((expires - datetime.utcnow()).total_seconds())
                if expire_seconds > 0:
                    self.redis.setex(key, expire_seconds, val)
                else:
                    # Already expired, don't save
                    return
            else:
                self.redis.set(key, val)
        except Exception:
            # Redis save failed, still set cookie for fallback
            pass
        
        # Set cookie
        response.set_cookie(
            app.session_cookie_name,
            session.sid,
            expires=expires,
            httponly=httponly,
            domain=domain,
            path=path,
            secure=secure,
            samesite=samesite
        )