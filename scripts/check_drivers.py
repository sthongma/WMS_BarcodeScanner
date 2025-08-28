#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ตรวจสอบ ODBC Drivers สำหรับ SQL Server
รันสคริปต์นี้เพื่อตรวจสอบ drivers ที่มีอยู่
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.utils.driver_checker import ODBCDriverChecker
    
    def main():
        print("=" * 60)
        print("🔍 ตรวจสอบ ODBC Drivers สำหรับ SQL Server")
        print("=" * 60)
        
        checker = ODBCDriverChecker()
        
        # แสดงข้อมูล drivers
        print(checker.show_driver_info())
        
        # ตรวจสอบ driver ที่เหมาะสม
        best_driver = checker.find_best_driver()
        
        if best_driver:
            print(f"\n✅ **สถานะ:** พร้อมใช้งาน")
            print(f"🎯 **Driver ที่จะใช้:** {best_driver}")
            
            # ทดสอบการเชื่อมต่อ
            print(f"\n🔗 **ทดสอบการเชื่อมต่อ:**")
            try:
                # อ่าน config จากไฟล์
                config_file = "config/sql_config.json"
                if os.path.exists(config_file):
                    import json
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    connection_string = checker.create_connection_string(
                        config['server'],
                        config['database'],
                        config['auth_type'],
                        config.get('username', ''),
                        config.get('password', '')
                    )
                    
                    print(f"📋 **Connection String:**")
                    print(f"   {connection_string}")
                    
                    # ทดสอบการเชื่อมต่อ
                    import pyodbc
                    with pyodbc.connect(connection_string, timeout=5) as conn:
                        print("✅ **การเชื่อมต่อ:** สำเร็จ")
                        
                        # ทดสอบ query
                        cursor = conn.cursor()
                        cursor.execute("SELECT @@VERSION as version")
                        result = cursor.fetchone()
                        if result:
                            print(f"📊 **SQL Server Version:** {result[0][:100]}...")
                else:
                    print("⚠️ ไม่พบไฟล์ config/sql_config.json")
                    
            except Exception as e:
                print(f"❌ **การเชื่อมต่อ:** ล้มเหลว")
                print(f"   ข้อผิดพลาด: {str(e)}")
        else:
            print(f"\n❌ **สถานะ:** ไม่พร้อมใช้งาน")
            print(checker.get_installation_guide())
        
        print("\n" + "=" * 60)
        input("กด Enter เพื่อปิด...")
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ เกิดข้อผิดพลาดในการ import: {e}")
    print("กรุณาตรวจสอบว่าไฟล์ src/utils/driver_checker.py มีอยู่")
    input("กด Enter เพื่อปิด...")
except Exception as e:
    print(f"❌ เกิดข้อผิดพลาด: {e}")
    input("กด Enter เพื่อปิด...") 