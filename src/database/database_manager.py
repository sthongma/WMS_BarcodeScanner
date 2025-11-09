#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Manager Module
Handles all database operations and connections
"""

import pyodbc
import tkinter.messagebox as messagebox
from typing import Dict, List, Optional, Any, Tuple
from .connection_config import ConnectionConfig


class DatabaseManager:
    """จัดการการเชื่อมต่อและดำเนินการกับฐานข้อมูล"""

    # Config file constant for backwards compatibility
    CONFIG_FILE = "config/sql_config.json"

    def __init__(self, connection_info: Optional[Dict[str, Any]] = None):
        self.config_manager = ConnectionConfig()
        self.connection_string = ""
        self.current_user = ""

        if connection_info:
            # ใช้ข้อมูลการเชื่อมต่อจาก login
            self.config_manager.config = connection_info['config']
            self.connection_string = connection_info['connection_string']
            self.current_user = connection_info['current_user']
        else:
            # ใช้การตั้งค่าจากไฟล์
            self.connection_string = self.config_manager.get_connection_string()
            self.current_user = self.config_manager.get_current_user()

    @property
    def config(self) -> Optional[Dict[str, Any]]:
        """Get config for backwards compatibility"""
        return self.config_manager.config

    @config.setter
    def config(self, value: Dict[str, Any]):
        """Set config for backwards compatibility"""
        self.config_manager.config = value
    
    def test_connection(self) -> bool:
        """ทดสอบการเชื่อมต่อฐานข้อมูล"""
        try:
            with pyodbc.connect(self.connection_string) as conn:
                return True
        except Exception as e:
            messagebox.showerror("Error", f"ไม่สามารถเชื่อมต่อฐานข้อมูลได้: {str(e)}")
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
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการดำเนินการ query: {str(e)}")
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
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการดำเนินการ query: {str(e)}")
            return 0
    
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
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการดำเนินการ stored procedure: {str(e)}")
            return []
    
    def get_connection_info(self) -> Dict[str, Any]:
        """รับข้อมูลการเชื่อมต่อปัจจุบัน"""
        return {
            'config': self.config_manager.get_config(),
            'connection_string': self.connection_string,
            'current_user': self.current_user
        }
    
    def update_connection(self, new_config: Dict[str, Any]) -> bool:
        """อัพเดทการเชื่อมต่อ"""
        try:
            # อัพเดทการตั้งค่า
            if self.config_manager.update_config(new_config):
                # สร้าง connection string ใหม่
                self.connection_string = self.config_manager.get_connection_string()
                self.current_user = self.config_manager.get_current_user()
                return True
            return False
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการอัพเดทการเชื่อมต่อ: {str(e)}")
            return False

    # ========================================================================
    # Convenience methods for backwards compatibility with main_window.py
    # ========================================================================

    def load_config(self) -> bool:
        """โหลดการตั้งค่าจากไฟล์ (delegates to config_manager)"""
        result = self.config_manager.load_config()
        if result:
            # Update connection string after loading config
            self.update_connection_string()
        return result

    def save_config(self) -> bool:
        """บันทึกการตั้งค่าลงไฟล์ (delegates to config_manager)"""
        return self.config_manager.save_config()

    def get_config(self) -> Dict[str, Any]:
        """รับการตั้งค่าปัจจุบัน (delegates to config_manager)"""
        return self.config_manager.get_config()

    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """อัพเดทการตั้งค่าใหม่ (alias for update_connection)"""
        return self.update_connection(new_config)

    def reset_to_default(self) -> bool:
        """รีเซ็ตการตั้งค่าเป็นค่าเริ่มต้น (delegates to config_manager)"""
        result = self.config_manager.reset_to_default()
        if result:
            # Update connection string after reset
            self.update_connection_string()
        return result

    def update_connection_string(self):
        """อัพเดท connection string ตามการตั้งค่า"""
        self.connection_string = self.config_manager.get_connection_string()
        self.current_user = self.config_manager.get_current_user() 