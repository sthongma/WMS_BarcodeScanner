#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Manager Module
Unified Singleton Database Manager for WMS Barcode Scanner
Handles all database operations and connections
"""

import pyodbc
import json
import os
import threading
from typing import Dict, List, Optional, Any, Tuple

# Use appropriate message box based on environment
try:
    import tkinter.messagebox as messagebox
except ImportError:
    # For web application or headless environment
    messagebox = None


class DatabaseManager:
    """จัดการการเชื่อมต่อและดำเนินการกับฐานข้อมูล แบบ Singleton Pattern"""
    
    _instance = None
    _lock = threading.Lock()
    CONFIG_FILE = "config/sql_config.json"
    
    def __new__(cls, connection_info: Optional[Dict[str, Any]] = None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, connection_info: Optional[Dict[str, Any]] = None):
        # Prevent re-initialization if already initialized
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.config = None
        self.connection_string = ""
        self.current_user = ""
        self._initialized = False
        
        if connection_info:
            # Use connection info from login
            self.config = connection_info['config']
            self.connection_string = connection_info['connection_string']
            self.current_user = connection_info['current_user']
        else:
            # Fallback to loading from file
            self.load_config()
            self.update_connection_string()
        
        self._initialized = True
    
    def load_config(self) -> bool:
        """โหลดการตั้งค่าจากไฟล์"""
        try:
            default_config = {
                "server": os.environ.get('COMPUTERNAME', 'localhost') + '\\SQLEXPRESS',
                "database": "WMS_EP",
                "auth_type": "SQL",  # Windows หรือ SQL
                "username": "",
                "password": ""
            }
            
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.config = default_config.copy()
                    self.config.update(saved_config)
            else:
                self.config = default_config.copy()
                self.save_config()
            
            return True
        except Exception as e:
            self._show_error(f"เกิดข้อผิดพลาดในการโหลดการตั้งค่า: {str(e)}")
            return False
    
    def save_config(self) -> bool:
        """บันทึกการตั้งค่าลงไฟล์"""
        try:
            os.makedirs(os.path.dirname(self.CONFIG_FILE), exist_ok=True)
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            self._show_error(f"เกิดข้อผิดพลาดในการบันทึกการตั้งค่า: {str(e)}")
            return False
    
    def update_connection_string(self):
        """อัพเดท connection string ตามการตั้งค่า"""
        if not self.config:
            return
        
        if self.config['auth_type'] == "Windows":
            self.connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.config['server']};"
                f"DATABASE={self.config['database']};"
                f"Trusted_Connection=yes;"
                f"TrustServerCertificate=yes;"
            )
            self.current_user = os.environ.get('USERNAME', 'WindowsUser')
        else:  # SQL Authentication
            self.connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.config['server']};"
                f"DATABASE={self.config['database']};"
                f"UID={self.config['username']};"
                f"PWD={self.config['password']};"
                f"TrustServerCertificate=yes;"
            )
            self.current_user = self.config['username']
    
    def test_connection(self) -> bool:
        """ทดสอบการเชื่อมต่อฐานข้อมูล"""
        try:
            with pyodbc.connect(self.connection_string, timeout=5) as conn:
                return True
        except Exception as e:
            # สำหรับ web app ไม่แสดง popup เพราะจะแสดงบน server
            # แค่ log error และ return False เพื่อให้ caller จัดการ
            if messagebox and hasattr(self, '_show_gui_errors'):
                # แสดง messagebox เฉพาะเมื่อเป็น desktop app
                messagebox.showerror("Error", f"ไม่สามารถเชื่อมต่อฐานข้อมูลได้: {str(e)}")
            # Log error สำหรับ debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Database connection failed: {str(e)}")
            return False
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict]:
        """ดำเนินการ query และส่งคืนผลลัพธ์เป็น list ของ dictionary"""
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                # รับชื่อคอลัมน์
                columns = [column[0] for column in cursor.description]
                
                # แปลงผลลัพธ์เป็น list ของ dictionary
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                
                return results
        except Exception as e:
            self._show_error(f"เกิดข้อผิดพลาดในการดำเนินการ query: {str(e)}")
            return []
    
    def execute_non_query(self, query: str, params: Tuple = ()) -> int:
        """ดำเนินการ query ที่ไม่ส่งคืนผลลัพธ์ (INSERT, UPDATE, DELETE)"""
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            self._show_error(f"เกิดข้อผิดพลาดในการดำเนินการ query: {str(e)}")
            raise Exception(f"Database execution error: {str(e)}")
    
    def execute_sp(self, sp_name: str, params: Tuple = ()) -> List[Dict]:
        """ดำเนินการ stored procedure"""
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                
                # สร้าง parameter string สำหรับ stored procedure
                param_placeholders = ','.join(['?' for _ in params])
                query = f"EXEC {sp_name} {param_placeholders}"
                
                cursor.execute(query, params)
                
                # รับชื่อคอลัมน์
                columns = [column[0] for column in cursor.description]
                
                # แปลงผลลัพธ์เป็น list ของ dictionary
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                
                return results
        except Exception as e:
            self._show_error(f"เกิดข้อผิดพลาดในการดำเนินการ stored procedure: {str(e)}")
            return []
    
    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """อัพเดทการตั้งค่าใหม่"""
        try:
            self.config.update(new_config)
            self.update_connection_string()
            return self.save_config()
        except Exception as e:
            self._show_error(f"เกิดข้อผิดพลาดในการอัพเดทการตั้งค่า: {str(e)}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """รับการตั้งค่าปัจจุบัน"""
        return self.config.copy() if self.config else {}
    
    def reset_to_default(self) -> bool:
        """รีเซ็ตการตั้งค่าเป็นค่าเริ่มต้น"""
        try:
            default_config = {
                "server": os.environ.get('COMPUTERNAME', 'localhost') + '\\SQLEXPRESS',
                "database": "WMS_EP",
                "auth_type": "Windows",
                "username": "",
                "password": ""
            }
            self.config = default_config
            self.update_connection_string()
            return self.save_config()
        except Exception as e:
            self._show_error(f"เกิดข้อผิดพลาดในการรีเซ็ตการตั้งค่า: {str(e)}")
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """รับข้อมูลการเชื่อมต่อปัจจุบัน"""
        return {
            'config': self.get_config(),
            'connection_string': self.connection_string,
            'current_user': self.current_user
        }
    
    def update_connection(self, new_config: Dict[str, Any]) -> bool:
        """อัพเดทการเชื่อมต่อ"""
        return self.update_config(new_config)
    
    def _show_error(self, message: str):
        """แสดง error message ตาม environment"""
        if messagebox and hasattr(self, '_show_gui_errors'):
            # แสดง messagebox เฉพาะเมื่อเป็น desktop app
            messagebox.showerror("Error", message)
        else:
            # สำหรับ web app แค่ log error
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Database error: {message}")
    
    @classmethod
    def get_instance(cls, connection_info: Optional[Dict[str, Any]] = None):
        """รับ instance ของ DatabaseManager (สำหรับความชัดเจน)"""
        return cls(connection_info) 