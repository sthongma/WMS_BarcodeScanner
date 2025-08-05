#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ODBC Driver Checker
ตรวจสอบและแก้ไขปัญหา ODBC drivers
"""

import pyodbc
import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
from typing import List, Dict

class ODBCDriverChecker:
    """ตรวจสอบและจัดการ ODBC drivers"""
    
    def __init__(self):
        self.available_drivers = []
        self.recommended_drivers = [
            "ODBC Driver 17 for SQL Server",
            "ODBC Driver 18 for SQL Server", 
            "ODBC Driver 13 for SQL Server",
            "SQL Server Native Client 11.0",
            "SQL Server"
        ]
    
    def get_available_drivers(self) -> List[str]:
        """รับรายการ ODBC drivers ที่มีอยู่"""
        try:
            self.available_drivers = pyodbc.drivers()
            return self.available_drivers
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการตรวจสอบ drivers: {e}")
            return []
    
    def check_sql_server_drivers(self) -> Dict[str, bool]:
        """ตรวจสอบ SQL Server drivers ที่มีอยู่"""
        drivers = self.get_available_drivers()
        result = {}
        
        for driver in self.recommended_drivers:
            result[driver] = driver in drivers
        
        return result
    
    def find_best_driver(self) -> str:
        """หาข้อดีที่สุด driver ที่มีอยู่"""
        available = self.get_available_drivers()
        
        # เรียงลำดับความสำคัญ
        for driver in self.recommended_drivers:
            if driver in available:
                return driver
        
        # ถ้าไม่มี driver ที่แนะนำ ให้ใช้ driver แรกที่มี
        sql_drivers = [d for d in available if 'SQL Server' in d or 'SQL' in d]
        if sql_drivers:
            return sql_drivers[0]
        
        return ""
    
    def create_connection_string(self, server: str, database: str, 
                               auth_type: str, username: str = "", 
                               password: str = "") -> str:
        """สร้าง connection string ด้วย driver ที่เหมาะสม"""
        best_driver = self.find_best_driver()
        
        if not best_driver:
            raise Exception("ไม่พบ ODBC Driver สำหรับ SQL Server")
        
        if auth_type == "Windows":
            return (
                f"DRIVER={{{best_driver}}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"Trusted_Connection=yes;"
                f"TrustServerCertificate=yes;"
            )
        else:
            return (
                f"DRIVER={{{best_driver}}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
                f"TrustServerCertificate=yes;"
            )
    
    def show_driver_info(self):
        """แสดงข้อมูล drivers ที่มีอยู่"""
        drivers = self.get_available_drivers()
        sql_drivers = self.check_sql_server_drivers()
        best_driver = self.find_best_driver()
        
        info = f"""📋 **ข้อมูล ODBC Drivers**

🔍 **Drivers ที่มีอยู่ทั้งหมด ({len(drivers)}):**
"""
        
        for driver in drivers:
            info += f"  • {driver}\n"
        
        info += f"\n🎯 **SQL Server Drivers:**\n"
        for driver, available in sql_drivers.items():
            status = "✅ มี" if available else "❌ ไม่มี"
            info += f"  • {driver}: {status}\n"
        
        info += f"\n🏆 **Driver ที่แนะนำ:** {best_driver or 'ไม่พบ'}"
        
        if not best_driver:
            info += "\n\n⚠️ **คำแนะนำ:** กรุณาติดตั้ง ODBC Driver for SQL Server"
        
        return info
    
    def get_installation_guide(self) -> str:
        """คู่มือการติดตั้ง ODBC Driver"""
        return """
📥 **คู่มือการติดตั้ง ODBC Driver for SQL Server**

**วิธีที่ 1: ดาวน์โหลดจาก Microsoft**
1. ไปที่: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
2. เลือก "ODBC Driver 17 for SQL Server"
3. ดาวน์โหลดและติดตั้ง

**วิธีที่ 2: ใช้ winget (Windows 10/11)**
```cmd
winget install Microsoft.ODBCDriver17
```

**วิธีที่ 3: ใช้ Chocolatey**
```cmd
choco install msodbcsql17
```

**หลังจากติดตั้งแล้ว:**
1. รีสตาร์ทคอมพิวเตอร์
2. รันโปรแกรมใหม่
3. ตรวจสอบการเชื่อมต่อ

**หมายเหตุ:** ต้องมีสิทธิ์ Administrator ในการติดตั้ง
"""

def main():
    """ฟังก์ชันหลักสำหรับทดสอบ"""
    checker = ODBCDriverChecker()
    
    print("=== ODBC Driver Checker ===")
    print(checker.show_driver_info())
    
    if not checker.find_best_driver():
        print("\n" + checker.get_installation_guide())

if __name__ == "__main__":
    main() 