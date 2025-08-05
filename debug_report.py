#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug Script สำหรับตรวจสอบข้อมูลรายงาน
ตรวจสอบข้อมูลในฐานข้อมูลและทดสอบคิวรี
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

def check_table_data(db_manager):
    """ตรวจสอบข้อมูลในตารางต่างๆ"""
    print("\n🔍 ตรวจสอบข้อมูลในตาราง...")
    
    # ตรวจสอบ job_types
    print("\n📊 ข้อมูลในตาราง job_types:")
    try:
        job_types = db_manager.execute_query("SELECT * FROM job_types ORDER BY id")
        if job_types:
            for job in job_types:
                print(f"  ID: {job['id']}, Name: {job['job_name']}")
        else:
            print("  ไม่มีข้อมูล")
    except Exception as e:
        print(f"  ❌ เกิดข้อผิดพลาด: {e}")
    
    # ตรวจสอบ sub_job_types
    print("\n📊 ข้อมูลในตาราง sub_job_types:")
    try:
        sub_jobs = db_manager.execute_query("SELECT * FROM sub_job_types WHERE is_active = 1 ORDER BY main_job_id, id")
        if sub_jobs:
            for sub_job in sub_jobs:
                print(f"  ID: {sub_job['id']}, Main Job ID: {sub_job['main_job_id']}, Name: {sub_job['sub_job_name']}")
        else:
            print("  ไม่มีข้อมูล")
    except Exception as e:
        print(f"  ❌ เกิดข้อผิดพลาด: {e}")
    
    # ตรวจสอบ scan_logs
    print("\n📊 ข้อมูลในตาราง scan_logs (ล่าสุด 10 รายการ):")
    try:
        scan_logs = db_manager.execute_query("""
            SELECT TOP 10 
                sl.id, sl.barcode, sl.scan_date, sl.job_type, sl.user_id, 
                sl.job_id, sl.sub_job_id, sl.notes
            FROM scan_logs sl 
            ORDER BY sl.scan_date DESC
        """)
        if scan_logs:
            for log in scan_logs:
                print(f"  ID: {log['id']}, Barcode: {log['barcode']}, Job Type: {log['job_type']}, Job ID: {log['job_id']}, Sub Job ID: {log['sub_job_id']}, Date: {log['scan_date']}")
        else:
            print("  ไม่มีข้อมูล")
    except Exception as e:
        print(f"  ❌ เกิดข้อผิดพลาด: {e}")
    
    # ตรวจสอบข้อมูลในวันที่ 2025-08-05
    print("\n📊 ข้อมูลในวันที่ 2025-08-05:")
    try:
        scan_logs_today = db_manager.execute_query("""
            SELECT 
                sl.id, sl.barcode, sl.scan_date, sl.job_type, sl.user_id, 
                sl.job_id, sl.sub_job_id, sl.notes
            FROM scan_logs sl 
            WHERE CAST(sl.scan_date AS DATE) = '2025-08-05'
            ORDER BY sl.scan_date DESC
        """)
        if scan_logs_today:
            print(f"  พบ {len(scan_logs_today)} รายการ")
            for log in scan_logs_today:
                print(f"    ID: {log['id']}, Barcode: {log['barcode']}, Job Type: {log['job_type']}, Job ID: {log['job_id']}, Sub Job ID: {log['sub_job_id']}, Date: {log['scan_date']}")
        else:
            print("  ไม่มีข้อมูล")
    except Exception as e:
        print(f"  ❌ เกิดข้อผิดพลาด: {e}")
    
    # ตรวจสอบข้อมูล Release (Job ID = 1)
    print("\n📊 ข้อมูล Release (Job ID = 1) ในวันที่ 2025-08-05:")
    try:
        release_data = db_manager.execute_query("""
            SELECT 
                sl.id, sl.barcode, sl.scan_date, sl.job_type, sl.user_id, 
                sl.job_id, sl.sub_job_id, sl.notes
            FROM scan_logs sl 
            WHERE sl.job_id = 1 
            AND CAST(sl.scan_date AS DATE) = '2025-08-05'
            ORDER BY sl.scan_date DESC
        """)
        if release_data:
            print(f"  พบ {len(release_data)} รายการ")
            for log in release_data:
                print(f"    ID: {log['id']}, Barcode: {log['barcode']}, Job Type: {log['job_type']}, Job ID: {log['job_id']}, Sub Job ID: {log['sub_job_id']}, Date: {log['scan_date']}")
        else:
            print("  ไม่มีข้อมูล")
    except Exception as e:
        print(f"  ❌ เกิดข้อผิดพลาด: {e}")
    
    # ตรวจสอบข้อมูล DHL (Sub Job ID = 7)
    print("\n📊 ข้อมูล DHL (Sub Job ID = 7) ในวันที่ 2025-08-05:")
    try:
        dhl_data = db_manager.execute_query("""
            SELECT 
                sl.id, sl.barcode, sl.scan_date, sl.job_type, sl.user_id, 
                sl.job_id, sl.sub_job_id, sl.notes
            FROM scan_logs sl 
            WHERE sl.sub_job_id = 7 
            AND CAST(sl.scan_date AS DATE) = '2025-08-05'
            ORDER BY sl.scan_date DESC
        """)
        if dhl_data:
            print(f"  พบ {len(dhl_data)} รายการ")
            for log in dhl_data:
                print(f"    ID: {log['id']}, Barcode: {log['barcode']}, Job Type: {log['job_type']}, Job ID: {log['job_id']}, Sub Job ID: {log['sub_job_id']}, Date: {log['scan_date']}")
        else:
            print("  ไม่มีข้อมูล")
    except Exception as e:
        print(f"  ❌ เกิดข้อผิดพลาด: {e}")

def test_report_queries(db_manager):
    """ทดสอบคิวรีรายงาน"""
    print("\n🧪 ทดสอบคิวรีรายงาน...")
    
    # ข้อมูลทดสอบ
    test_date = datetime.now().strftime('%Y-%m-%d')
    start_date = f"{test_date} 00:00:00"
    end_date = f"{test_date} 23:59:59"
    job_type_id = 1  # Release
    sub_job_type_id = 7  # DHL
    
    print(f"📅 วันที่ทดสอบ: {test_date}")
    print(f"🔢 Job Type ID: {job_type_id}")
    print(f"🔢 Sub Job Type ID: {sub_job_type_id}")
    
    # ทดสอบคิวรีสำหรับงานรอง
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
    except Exception as e:
        print(f"  ❌ เกิดข้อผิดพลาด: {e}")
    
    # ทดสอบคิวรีสำหรับงานหลักเท่านั้น
    print("\n📊 ทดสอบคิวรีสำหรับงานหลักเท่านั้น (ไม่มี sub_job_id):")
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
        AND sl.sub_job_id IS NULL
        AND sl.scan_date BETWEEN ? AND ?
        ORDER BY sl.scan_date DESC
    """
    
    try:
        results2 = db_manager.execute_query(query2, (job_type_id, start_date, end_date))
        print(f"  ผลลัพธ์: {len(results2) if results2 else 0} รายการ")
        if results2:
            for i, row in enumerate(results2[:3]):  # แสดง 3 รายการแรก
                print(f"    {i+1}. {row['barcode']} - {row['job_type_name']} > {row['sub_job_type_name']}")
    except Exception as e:
        print(f"  ❌ เกิดข้อผิดพลาด: {e}")
    
    # ทดสอบคิวรีแบบง่าย (ไม่กรอง sub_job_id)
    print("\n📊 ทดสอบคิวรีแบบง่าย (ไม่กรอง sub_job_id):")
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
        AND sl.scan_date BETWEEN ? AND ?
        ORDER BY sl.scan_date DESC
    """
    
    try:
        results3 = db_manager.execute_query(query3, (job_type_id, start_date, end_date))
        print(f"  ผลลัพธ์: {len(results3) if results3 else 0} รายการ")
        if results3:
            for i, row in enumerate(results3[:3]):  # แสดง 3 รายการแรก
                print(f"    {i+1}. {row['barcode']} - {row['job_type_name']} > {row['sub_job_type_name']}")
    except Exception as e:
        print(f"  ❌ เกิดข้อผิดพลาด: {e}")

def check_data_consistency(db_manager):
    """ตรวจสอบความสอดคล้องของข้อมูล"""
    print("\n🔍 ตรวจสอบความสอดคล้องของข้อมูล...")
    
    # ตรวจสอบ scan_logs ที่ไม่มี job_id
    print("\n📊 scan_logs ที่ไม่มี job_id:")
    try:
        missing_job_id = db_manager.execute_query("SELECT COUNT(*) as count FROM scan_logs WHERE job_id IS NULL")
        if missing_job_id:
            print(f"  จำนวน: {missing_job_id[0]['count']}")
    except Exception as e:
        print(f"  ❌ เกิดข้อผิดพลาด: {e}")
    
    # ตรวจสอบ scan_logs ที่ไม่มี sub_job_id
    print("\n📊 scan_logs ที่ไม่มี sub_job_id:")
    try:
        missing_sub_job_id = db_manager.execute_query("SELECT COUNT(*) as count FROM scan_logs WHERE sub_job_id IS NULL")
        if missing_sub_job_id:
            print(f"  จำนวน: {missing_sub_job_id[0]['count']}")
    except Exception as e:
        print(f"  ❌ เกิดข้อผิดพลาด: {e}")
    
    # ตรวจสอบ scan_logs ที่มี job_id แต่ไม่มี sub_job_id
    print("\n📊 scan_logs ที่มี job_id แต่ไม่มี sub_job_id:")
    try:
        with_job_no_sub = db_manager.execute_query("""
            SELECT COUNT(*) as count 
            FROM scan_logs 
            WHERE job_id IS NOT NULL AND sub_job_id IS NULL
        """)
        if with_job_no_sub:
            print(f"  จำนวน: {with_job_no_sub[0]['count']}")
    except Exception as e:
        print(f"  ❌ เกิดข้อผิดพลาด: {e}")

def main():
    """ฟังก์ชันหลัก"""
    print("🚀 เริ่มตรวจสอบข้อมูลรายงาน WMS Barcode Scanner")
    print("=" * 60)
    
    # เชื่อมต่อฐานข้อมูล
    db_manager = initialize_database()
    if not db_manager:
        print("❌ ไม่สามารถเชื่อมต่อฐานข้อมูลได้")
        return
    
    # ตรวจสอบข้อมูลในตาราง
    check_table_data(db_manager)
    
    # ตรวจสอบความสอดคล้องของข้อมูล
    check_data_consistency(db_manager)
    
    # ทดสอบคิวรีรายงาน
    test_report_queries(db_manager)
    
    print("\n" + "=" * 60)
    print("✅ การตรวจสอบเสร็จสิ้น")

if __name__ == "__main__":
    main() 