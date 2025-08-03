#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connection Configuration Module
Handles database connection configuration
"""

import json
import os
import tkinter.messagebox as messagebox
from typing import Dict, Any, Optional


class ConnectionConfig:
    """จัดการการตั้งค่าการเชื่อมต่อฐานข้อมูล"""
    
    CONFIG_FILE = "config/sql_config.json"
    
    def __init__(self):
        self.config = None
        self.load_config()
    
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
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการโหลดการตั้งค่า: {str(e)}")
            return False
    
    def save_config(self) -> bool:
        """บันทึกการตั้งค่าลงไฟล์"""
        try:
            # สร้างโฟลเดอร์ config ถ้ายังไม่มี
            os.makedirs(os.path.dirname(self.CONFIG_FILE), exist_ok=True)
            
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการบันทึกการตั้งค่า: {str(e)}")
            return False
    
    def get_connection_string(self, auth_type: Optional[str] = None) -> str:
        """สร้าง connection string ตามการตั้งค่า"""
        if not self.config:
            return ""
        
        auth_type = auth_type or self.config['auth_type']
        
        if auth_type == "Windows":
            return (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.config['server']};"
                f"DATABASE={self.config['database']};"
                f"Trusted_Connection=yes;"
                f"TrustServerCertificate=yes;"
            )
        else:  # SQL Authentication
            return (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.config['server']};"
                f"DATABASE={self.config['database']};"
                f"UID={self.config['username']};"
                f"PWD={self.config['password']};"
                f"TrustServerCertificate=yes;"
            )
    
    def get_current_user(self) -> str:
        """รับชื่อผู้ใช้ปัจจุบัน"""
        if self.config and self.config['auth_type'] == "Windows":
            return os.environ.get('USERNAME', 'WindowsUser')
        elif self.config:
            return self.config.get('username', 'SQLUser')
        return 'Unknown'
    
    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """อัพเดทการตั้งค่า"""
        try:
            self.config.update(new_config)
            return self.save_config()
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการอัพเดทการตั้งค่า: {str(e)}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """รับการตั้งค่าปัจจุบัน"""
        return self.config.copy() if self.config else {}
    
    def reset_to_default(self) -> bool:
        """รีเซ็ตการตั้งค่าเป็นค่าเริ่มต้น"""
        try:
            self.config = {
                "server": os.environ.get('COMPUTERNAME', 'localhost') + '\\SQLEXPRESS',
                "database": "WMS_EP",
                "auth_type": "SQL",
                "username": "",
                "password": ""
            }
            return self.save_config()
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการรีเซ็ตการตั้งค่า: {str(e)}")
            return False 