#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Connection Pool Manager
High-performance connection pooling for SQL Server
"""

import pyodbc
import threading
import time
import logging
from typing import Dict, Optional, Any
from queue import Queue, Empty
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class ConnectionPool:
    """Thread-safe database connection pool"""
    
    def __init__(self, connection_string: str, 
                 min_connections: int = 5,
                 max_connections: int = 20,
                 max_idle_time: int = 300):  # 5 minutes
        self.connection_string = connection_string
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.max_idle_time = max_idle_time
        
        self._pool = Queue(maxsize=max_connections)
        self._all_connections = set()
        self._lock = threading.RLock()
        self._created_connections = 0
        self._connection_info = {}  # Track connection creation time
        
        # Initialize minimum connections
        self._initialize_pool()
        
        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_idle_connections, daemon=True)
        self._cleanup_thread.start()
        
        logger.info(f"📊 Connection pool initialized: {min_connections}-{max_connections} connections")
    
    def _initialize_pool(self):
        """Create minimum number of connections"""
        with self._lock:
            for _ in range(self.min_connections):
                try:
                    conn = self._create_connection()
                    if conn:
                        self._pool.put(conn)
                        logger.debug(f"✅ Initialized connection {self._created_connections}")
                except Exception as e:
                    logger.error(f"Failed to initialize connection: {e}")
    
    def _create_connection(self) -> Optional[pyodbc.Connection]:
        """Create a new database connection"""
        try:
            with self._lock:
                if self._created_connections >= self.max_connections:
                    logger.warning(f"⚠️ Maximum connections ({self.max_connections}) reached")
                    return None
                
                conn = pyodbc.connect(
                    self.connection_string,
                    timeout=30,
                    autocommit=True
                )
                
                # Configure connection for optimal performance
                conn.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
                conn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
                conn.setencoding(encoding='utf-8')
                
                self._created_connections += 1
                self._all_connections.add(conn)
                self._connection_info[id(conn)] = {
                    'created_at': time.time(),
                    'last_used': time.time()
                }
                
                logger.debug(f"🆕 Created new connection {self._created_connections}/{self.max_connections}")
                return conn
                
        except Exception as e:
            logger.error(f"Failed to create connection: {e}")
            return None
    
    @contextmanager
    def get_connection(self):
        """Get connection from pool with context manager"""
        connection = None
        try:
            # Try to get existing connection
            try:
                connection = self._pool.get(timeout=5)  # Wait max 5 seconds
                
                # Test if connection is still valid
                if not self._test_connection(connection):
                    logger.warning("🔄 Connection invalid, creating new one")
                    self._remove_connection(connection)
                    connection = self._create_connection()
                    
            except Empty:
                # Pool is empty, create new connection if possible
                logger.debug("📊 Pool empty, creating new connection")
                connection = self._create_connection()
            
            if not connection:
                raise Exception("Unable to get database connection")
            
            # Update last used time
            with self._lock:
                if id(connection) in self._connection_info:
                    self._connection_info[id(connection)]['last_used'] = time.time()
            
            yield connection
            
        finally:
            # Return connection to pool
            if connection:
                try:
                    if self._test_connection(connection):
                        self._pool.put_nowait(connection)
                    else:
                        self._remove_connection(connection)
                except Exception as e:
                    logger.error(f"Error returning connection to pool: {e}")
                    self._remove_connection(connection)
    
    def _test_connection(self, connection) -> bool:
        """Test if connection is still valid"""
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except:
            return False
    
    def _remove_connection(self, connection):
        """Remove connection from pool and tracking"""
        with self._lock:
            try:
                if connection in self._all_connections:
                    self._all_connections.remove(connection)
                    self._created_connections -= 1
                
                conn_id = id(connection)
                if conn_id in self._connection_info:
                    del self._connection_info[conn_id]
                
                connection.close()
                logger.debug(f"🗑️ Removed connection {self._created_connections + 1}/{self.max_connections}")
                
            except Exception as e:
                logger.error(f"Error removing connection: {e}")
    
    def _cleanup_idle_connections(self):
        """Background thread to cleanup idle connections"""
        while True:
            try:
                time.sleep(60)  # Check every minute
                current_time = time.time()
                connections_to_remove = []
                
                with self._lock:
                    # Find idle connections (keeping minimum)
                    if self._created_connections > self.min_connections:
                        for conn_id, info in self._connection_info.items():
                            if current_time - info['last_used'] > self.max_idle_time:
                                connections_to_remove.append(conn_id)
                                if self._created_connections - len(connections_to_remove) <= self.min_connections:
                                    break
                
                # Remove idle connections
                if connections_to_remove:
                    logger.info(f"🧹 Cleaning up {len(connections_to_remove)} idle connections")
                    for conn_id in connections_to_remove:
                        for conn in list(self._all_connections):
                            if id(conn) == conn_id:
                                self._remove_connection(conn)
                                break
                
            except Exception as e:
                logger.error(f"Error in connection cleanup: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics"""
        with self._lock:
            return {
                'total_connections': self._created_connections,
                'available_connections': self._pool.qsize(),
                'max_connections': self.max_connections,
                'min_connections': self.min_connections,
                'pool_usage': f"{self._created_connections}/{self.max_connections}",
                'pool_utilization_percent': round((self._created_connections / self.max_connections) * 100, 2)
            }
    
    def close_all(self):
        """Close all connections in pool"""
        logger.info("🛑 Closing all database connections")
        with self._lock:
            # Close all connections
            for connection in list(self._all_connections):
                try:
                    connection.close()
                except:
                    pass
            
            # Clear tracking
            self._all_connections.clear()
            self._connection_info.clear()
            self._created_connections = 0
            
            # Clear queue
            while not self._pool.empty():
                try:
                    self._pool.get_nowait()
                except:
                    break