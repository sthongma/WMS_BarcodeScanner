#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script สำหรับทดสอบคิวรีรายงานที่แก้ไขแล้ว
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.database_manager import DatabaseManager

def load_database_config():
    """โหลดการตั้งค่าฐานข้อมูล"""
    try:
        config_path = os.path.join('config', 'sql_config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        else:
            print(f"❌ ไม่พบไฟล์ config: {config_path}")
            return None
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการโหลด config: {e}")
        return None

def create_connection_string(config):
    """สร้าง connection string"""
    try:
        server = config.get('server', '')
        database = config.get('database', '')
        auth_type = config.get('auth_type', 'SQL')
        
        if auth_type == 'Windows':
            return f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes"
        else:
            username = config.get('username', '')
            password = config.get('password', '')
            return f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการสร้าง connection string: {e}")
        return None

def initialize_database():
    """เริ่มต้นการเชื่อมต่อฐานข้อมูล"""
    try:
        config = load_database_config()
        if config:
            connection_string = create_connection_string(config)
            if connection_string:
                print(f"🔗 กำลังเชื่อมต่อ: {config['server']}/{config['database']}")
                
                connection_info = {
                    'config': config,
                    'connection_string': connection_string,
                    'current_user': config.get('username', 'system')
                }
                
                db_manager = DatabaseManager(connection_info)
                if db_manager.test_connection():
                    print("✅ เชื่อมต่อฐานข้อมูลสำเร็จ")
                    return db_manager
                else:
                    print("❌ การทดสอบการเชื่อมต่อล้มเหลว")
                    return None
            else:
                print("❌ ไม่สามารถสร้าง connection string ได้")
                return None
        else:
            print("❌ ไม่สามารถโหลดการตั้งค่าฐานข้อมูลได้")
            return None
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อฐานข้อมูล: {e}")
        return None

def test_fixed_queries(db_manager):
    """ทดสอบคิวรีที่แก้ไขแล้ว"""
    print("\n🧪 ทดสอบคิวรีที่แก้ไขแล้ว...")
    
    # ข้อมูลทดสอบ
    test_date = "2025-08-05"
    start_date = f"{test_date} 00:00:00"
    end_date = f"{test_date} 23:59:59"
    job_type_id = 1  # Release
    sub_job_type_id = 7  # DHL
    
    print(f"📅 วันที่ทดสอบ: {test_date}")
    print(f"🔢 Job Type ID: {job_type_id}")
    print(f"🔢 Sub Job Type ID: {sub_job_type_id}")
    print(f"⏰ Start Date: {start_date}")
    print(f"⏰ End Date: {end_date}")
    
    # ทดสอบคิวรีสำหรับงานรอง (มี sub_job_id)
    print("\n📊 ทดสอบคิวรีสำหรับงานรอง (มี sub_job_id):")
    query1 = """
        SELECT 
            sl.barcode,
            sl.scan_date,
            sl.notes,
            sl.user_id,
            jt.job_name as job_type_name,
            sjt.sub_job_name as sub_job_type_name
        FROM scan_logs sl
        LEFT JOIN job_types jt ON sl.job_id = jt.id
        LEFT JOIN sub_job_types sjt ON sl.sub_job_id = sjt.id
        WHERE sl.job_id = ? 
        AND sl.sub_job_id = ?
        AND sl.scan_date BETWEEN ? AND ?
        ORDER BY sl.scan_date DESC
    """
    
    try:
        results1 = db_manager.execute_query(query1, (job_type_id, sub_job_type_id, start_date, end_date))
        print(f"  ผลลัพธ์: {len(results1) if results1 else 0} รายการ")
        if results1:
            for i, row in enumerate(results1[:3]):  # แสดง 3 รายการแรก
                print(f"    {i+1}. {row['barcode']} - {row['job_type_name']} > {row['sub_job_type_name']}")
        else:
            print("    ไม่มีข้อมูล")
    except Exception as e:
        print(f"  ❌ เกิดข้อผิดพลาด: {e}")
    
    # ทดสอบคิวรีสำหรับงานหลักเท่านั้น (ไม่กรอง sub_job_id)
    print("\n📊 ทดสอบคิวรีสำหรับงานหลักเท่านั้น (ไม่กรอง sub_job_id):")
    query2 = """
        SELECT 
            sl.barcode,
            sl.scan_date,
            sl.notes,
            sl.user_id,
            jt.job_name as job_type_name,
            ISNULL(sjt.sub_job_name, 'ไม่มี') as sub_job_type_name
        FROM scan_logs sl
        LEFT JOIN job_types jt ON sl.job_id = jt.id
        LEFT JOIN sub_job_types sjt ON sl.sub_job_id = sjt.id
        WHERE sl.job_id = ? 
        AND sl.scan_date BETWEEN ? AND ?
        ORDER BY sl.scan_date DESC
    """
    
    try:
        results2 = db_manager.execute_query(query2, (job_type_id, start_date, end_date))
        print(f"  ผลลัพธ์: {len(results2) if results2 else 0} รายการ")
        if results2:
            for i, row in enumerate(results2[:3]):  # แสดง 3 รายการแรก
                print(f"    {i+1}. {row['barcode']} - {row['job_type_name']} > {row['sub_job_type_name']}")
        else:
            print("    ไม่มีข้อมูล")
    except Exception as e:
        print(f"  ❌ เกิดข้อผิดพลาด: {e}")
    
    # ทดสอบคิวรีแบบใช้ CAST
    print("\n📊 ทดสอบคิวรีแบบใช้ CAST:")
    query3 = """
        SELECT 
            sl.barcode,
            sl.scan_date,
            sl.notes,
            sl.user_id,
            jt.job_name as job_type_name,
            ISNULL(sjt.sub_job_name, 'ไม่มี') as sub_job_type_name
        FROM scan_logs sl
        LEFT JOIN job_types jt ON sl.job_id = jt.id
        LEFT JOIN sub_job_types sjt ON sl.sub_job_id = sjt.id
        WHERE sl.job_id = ? 
        AND CAST(sl.scan_date AS DATE) = ?
        ORDER BY sl.scan_date DESC
    """
    
    try:
        results3 = db_manager.execute_query(query3, (job_type_id, test_date))
        print(f"  ผลลัพธ์: {len(results3) if results3 else 0} รายการ")
        if results3:
            for i, row in enumerate(results3[:3]):  # แสดง 3 รายการแรก
                print(f"    {i+1}. {row['barcode']} - {row['job_type_name']} > {row['sub_job_type_name']}")
        else:
            print("    ไม่มีข้อมูล")
    except Exception as e:
        print(f"  ❌ เกิดข้อผิดพลาด: {e}")
    
    # ทดสอบคิวรีสำหรับงานหลักอื่นๆ
    print("\n📊 ทดสอบคิวรีสำหรับงานหลักอื่นๆ:")
    for job_id in [2, 3, 4]:  # Inprocess, Outbound, Loading
        try:
            results = db_manager.execute_query(query3, (job_id, test_date))
            print(f"  Job ID {job_id}: {len(results) if results else 0} รายการ")
        except Exception as e:
            print(f"  Job ID {job_id}: ❌ {e}")

def main():
    """ฟังก์ชันหลัก"""
    print("🚀 เริ่มทดสอบคิวรีรายงานที่แก้ไขแล้ว")
    print("=" * 60)
    
    # เชื่อมต่อฐานข้อมูล
    db_manager = initialize_database()
    if not db_manager:
        print("❌ ไม่สามารถเชื่อมต่อฐานข้อมูลได้")
        return
    
    # ทดสอบคิวรีที่แก้ไขแล้ว
    test_fixed_queries(db_manager)
    
    print("\n" + "=" * 60)
    print("✅ การทดสอบเสร็จสิ้น")

if __name__ == "__main__":
    main() 