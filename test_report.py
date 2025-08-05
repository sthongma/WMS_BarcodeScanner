#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script สำหรับแท็บรายงาน
ทดสอบการทำงานของ API รายงาน
"""

import requests
import json
from datetime import datetime, timedelta

# URL ของแอปพลิเคชัน
BASE_URL = "http://localhost:5000"

def test_report_api():
    """ทดสอบ API รายงาน"""
    print("🧪 เริ่มทดสอบ API รายงาน...")
    
    # ข้อมูลทดสอบ
    test_data = {
        "report_date": datetime.now().strftime('%Y-%m-%d'),
        "job_type_id": 1,  # Release
        "sub_job_type_id": 7  # DHL (เปลี่ยนจาก 1 เป็น 7)
    }
    
    try:
        # ทดสอบ API รายงาน
        print(f"📊 ทดสอบ API รายงาน...")
        print(f"📝 ข้อมูล: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/api/report",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("✅ API รายงานทำงานได้")
                print(f"📋 สรุป: {data['summary']}")
                print(f"📊 จำนวนข้อมูล: {len(data['data'])} รายการ")
                
                # แสดงข้อมูลตัวอย่าง
                if data['data']:
                    print("\n📝 ข้อมูลตัวอย่าง:")
                    for i, item in enumerate(data['data'][:3]):  # แสดง 3 รายการแรก
                        print(f"  {i+1}. {item['barcode']} - {item['job_type_name']} > {item['sub_job_type_name']}")
                else:
                    print("ℹ️ ไม่มีข้อมูลการสแกนในวันที่เลือก")
            else:
                print(f"❌ API รายงานล้มเหลว: {data['message']}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ไม่สามารถเชื่อมต่อกับแอปพลิเคชันได้")
        print("💡 ตรวจสอบว่าแอปพลิเคชันทำงานอยู่หรือไม่")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {str(e)}")

def test_job_types_api():
    """ทดสอบ API Job Types"""
    print("\n🔍 ทดสอบ API Job Types...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/job_types")
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("✅ API Job Types ทำงานได้")
                print(f"📊 จำนวน Job Types: {len(data['data'])}")
                for job_type in data['data']:
                    print(f"  - {job_type['id']}: {job_type['name']}")
            else:
                print(f"❌ API Job Types ล้มเหลว: {data['message']}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {str(e)}")

def test_sub_job_types_api():
    """ทดสอบ API Sub Job Types"""
    print("\n🔍 ทดสอบ API Sub Job Types...")
    
    try:
        # ทดสอบกับ Job Type ID = 1
        response = requests.get(f"{BASE_URL}/api/sub_job_types/1")
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("✅ API Sub Job Types ทำงานได้")
                print(f"📊 จำนวน Sub Job Types: {len(data['data'])}")
                for sub_job_type in data['data']:
                    print(f"  - {sub_job_type['id']}: {sub_job_type['name']}")
            else:
                print(f"❌ API Sub Job Types ล้มเหลว: {data['message']}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {str(e)}")

def test_web_interface():
    """ทดสอบหน้าเว็บ"""
    print("\n🌐 ทดสอบหน้าเว็บ...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        
        if response.status_code == 200:
            print("✅ หน้าเว็บโหลดได้")
            if "แท็บรายงาน" in response.text or "รายงาน" in response.text:
                print("✅ แท็บรายงานมีอยู่ในหน้าเว็บ")
            else:
                print("⚠️ ไม่พบแท็บรายงานในหน้าเว็บ")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {str(e)}")

def main():
    """ฟังก์ชันหลัก"""
    print("🚀 เริ่มทดสอบแท็บรายงาน WMS Barcode Scanner")
    print("=" * 50)
    
    # ทดสอบ API ต่างๆ
    test_job_types_api()
    test_sub_job_types_api()
    test_report_api()
    test_web_interface()
    
    print("\n" + "=" * 50)
    print("✅ การทดสอบเสร็จสิ้น")
    print("\n💡 คำแนะนำ:")
    print("1. เปิดเว็บเบราว์เซอร์ไปที่ http://localhost:5000")
    print("2. คลิกแท็บ '📊 รายงาน'")
    print("3. เลือกวันที่และประเภทงาน")
    print("4. คลิก 'ดูรายงาน' เพื่อทดสอบการทำงาน")

if __name__ == "__main__":
    main() 