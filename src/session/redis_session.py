#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis Session Storage for WMS Barcode Scanner
High-performance session management with Redis backend
"""

import redis
import json
import pickle
import logging
from typing import Any, Optional, Dict
from flask import session
from datetime import timedelta

logger = logging.getLogger(__name__)


class RedisSessionManager:
    """Redis-based session manager for Flask applications"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0", 
                 session_timeout: int = 7200):  # 2 hours default
        self.redis_url = redis_url
        self.session_timeout = session_timeout
        self._redis_client = None
        self._connection_pool = None
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection with pool"""
        try:
            # Create connection pool for better performance
            self._connection_pool = redis.ConnectionPool.from_url(
                self.redis_url,
                max_connections=20,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                decode_responses=False  # Keep binary for pickle
            )
            
            self._redis_client = redis.Redis(
                connection_pool=self._connection_pool,
                decode_responses=False
            )
            
            # Test connection
            self._redis_client.ping()
            logger.info(f"🚀 Redis session storage initialized: {self.redis_url}")
            
        except redis.ConnectionError as e:
            logger.warning(f"⚠️ Redis not available, falling back to file sessions: {e}")
            self._redis_client = None
        except Exception as e:
            logger.error(f"❌ Failed to initialize Redis: {e}")
            self._redis_client = None
    
    def is_available(self) -> bool:
        """Check if Redis is available"""
        if not self._redis_client:
            return False
        try:
            self._redis_client.ping()
            return True
        except:
            return False
    
    def set_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Store session data in Redis"""
        if not self.is_available():
            return False
        
        try:
            # Serialize session data
            serialized_data = pickle.dumps(session_data)
            
            # Store with expiration
            key = f"session:{session_id}"
            self._redis_client.setex(
                key, 
                self.session_timeout, 
                serialized_data
            )
            
            logger.debug(f"📝 Session stored: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store session {session_id}: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data from Redis"""
        if not self.is_available():
            return None
        
        try:
            key = f"session:{session_id}"
            serialized_data = self._redis_client.get(key)
            
            if serialized_data:
                # Extend session expiration on access
                self._redis_client.expire(key, self.session_timeout)
                
                # Deserialize and return
                session_data = pickle.loads(serialized_data)
                logger.debug(f"📖 Session retrieved: {session_id}")
                return session_data
            else:
                logger.debug(f"🚫 Session not found: {session_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to retrieve session {session_id}: {e}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session from Redis"""
        if not self.is_available():
            return False
        
        try:
            key = f"session:{session_id}"
            result = self._redis_client.delete(key)
            
            if result:
                logger.debug(f"🗑️ Session deleted: {session_id}")
            else:
                logger.debug(f"🚫 Session not found for deletion: {session_id}")
            
            return bool(result)
            
        except Exception as e:
            logger.error(f"❌ Failed to delete session {session_id}: {e}")
            return False
    
    def clear_expired_sessions(self) -> int:
        """Clear expired sessions (Redis handles this automatically)"""
        # Redis handles expiration automatically, but we can get stats
        if not self.is_available():
            return 0
        
        try:
            # Count current sessions
            keys = self._redis_client.keys("session:*")
            logger.info(f"📊 Active sessions: {len(keys)}")
            return len(keys)
            
        except Exception as e:
            logger.error(f"❌ Failed to count sessions: {e}")
            return 0
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session storage statistics"""
        if not self.is_available():
            return {
                'status': 'Redis unavailable',
                'active_sessions': 0,
                'memory_usage': 0,
                'connection_pool_size': 0
            }
        
        try:
            # Get Redis info
            info = self._redis_client.info()
            
            # Count sessions
            session_keys = self._redis_client.keys("session:*")
            
            return {
                'status': 'Connected',
                'redis_version': info.get('redis_version', 'unknown'),
                'active_sessions': len(session_keys),
                'memory_usage_mb': round(info.get('used_memory', 0) / 1024 / 1024, 2),
                'connection_pool_size': self._connection_pool.connection_kwargs if self._connection_pool else 0,
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'hit_ratio': round((info.get('keyspace_hits', 0) / max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0), 1)) * 100, 2)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get session stats: {e}")
            return {
                'status': f'Error: {e}',
                'active_sessions': 0
            }
    
    def cleanup_all_sessions(self) -> bool:
        """Clear all session data (use with caution)"""
        if not self.is_available():
            return False
        
        try:
            keys = self._redis_client.keys("session:*")
            if keys:
                deleted = self._redis_client.delete(*keys)
                logger.info(f"🧹 Cleared {deleted} sessions")
            else:
                logger.info("🧹 No sessions to clear")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to clear sessions: {e}")
            return False
    
    def close(self):
        """Close Redis connection"""
        if self._connection_pool:
            self._connection_pool.disconnect()
            logger.info("🛑 Redis connection pool closed")


# Global session manager instance
redis_session_manager = None


def get_redis_session_manager(redis_url: str = "redis://localhost:6379/0") -> RedisSessionManager:
    """Get global Redis session manager instance"""
    global redis_session_manager
    
    if redis_session_manager is None:
        redis_session_manager = RedisSessionManager(redis_url)
    
    return redis_session_manager


def configure_flask_redis_sessions(app, redis_url: str = "redis://localhost:6379/0"):
    """Configure Flask app to use Redis sessions with proper fallback"""
    try:
        # Try Redis first, but with graceful fallback
        import redis
        
        # Test Redis connection
        try:
            redis_client = redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=2)
            redis_client.ping()  # Test connection
            
            # Use custom Redis session implementation
            from .custom_redis_session import RedisSessionInterface
            
            app.session_interface = RedisSessionInterface(redis_client)
            app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
            
            logger.info(f"✅ Custom Redis sessions configured: {redis_url}")
            return True
            
        except (redis.ConnectionError, redis.TimeoutError, ConnectionRefusedError) as e:
            logger.warning(f"⚠️ Redis not available ({e}), using default Flask sessions")
            
            # Use default Flask sessions (in-memory, but stable)
            logger.info("📁 Using default Flask sessions as fallback")
            return True
        
    except ImportError as e:
        logger.warning(f"⚠️ Redis not available ({e}), using default Flask sessions")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Session configuration failed: {e}, using default Flask sessions")
        return True