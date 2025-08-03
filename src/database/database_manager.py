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