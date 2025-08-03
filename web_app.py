#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WMS Barcode Scanner Web Application
สำหรับใช้งานบน Android ผ่านเว็บเบราว์เซอร์
"""

import sys
import os
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import json
from datetime import datetime
import threading

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.database_manager import DatabaseManager
from src.models.data_models import ScanRecord

app = Flask(__name__)
app.secret_key = 'wms_scanner_secret_key_2024'
CORS(app)

# Global database manager
db_manager = None

def load_database_config():
    """โหลดการตั้งค่าฐานข้อมูลจากไฟล์ config"""
    try:
        config_path = os.path.join('config', 'sql_config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # ตรวจสอบว่ามีข้อมูลที่จำเป็นครบหรือไม่
            required_fields = ['server', 'database']
            for field in required_fields:
                if field not in config:
                    print(f"❌ ไม่พบข้อมูล {field} ในไฟล์ config")
                    return None
            
            print(f"✅ โหลด config สำเร็จ: {config['server']}/{config['database']}")
            return config
        else:
            print(f"⚠️ ไม่พบไฟล์ config: {config_path}")
            return None
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการโหลด config: {e}")
        return None

def create_connection_string(config):
    """สร้าง connection string จาก config"""
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
    global db_manager
    try:
        config = load_database_config()
        if config:
            connection_string = create_connection_string(config)
            if connection_string:
                print(f"🔗 กำลังเชื่อมต่อ: {config['server']}/{config['database']}")
                
                # สร้าง connection_info สำหรับ DatabaseManager
                connection_info = {
                    'config': config,
                    'connection_string': connection_string,
                    'current_user': config.get('username', 'system')
                }
                
                db_manager = DatabaseManager(connection_info)
                if db_manager.test_connection():
                    print("✅ เชื่อมต่อฐานข้อมูลสำเร็จ")
                    return True
                else:
                    print("❌ การทดสอบการเชื่อมต่อล้มเหลว")
                    return False
            else:
                print("❌ ไม่สามารถสร้าง connection string ได้")
                return False
        else:
            print("❌ ไม่สามารถโหลดการตั้งค่าฐานข้อมูลได้")
            return False
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อฐานข้อมูล: {e}")
        return False

@app.route('/')
def index():
    """หน้าแรกของแอปพลิเคชัน"""
    return render_template('index.html')

@app.route('/api/init')
def initialize_app():
    """API สำหรับเริ่มต้นแอปพลิเคชัน"""
    try:
        if initialize_database():
            return jsonify({
                'success': True, 
                'message': 'เชื่อมต่อฐานข้อมูลสำเร็จ',
                'connected': True
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'ไม่สามารถเชื่อมต่อฐานข้อมูลได้',
                'connected': False
            })
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'เกิดข้อผิดพลาด: {str(e)}',
            'connected': False
        })

@app.route('/api/login', methods=['POST'])
def login():
    """API สำหรับ login"""
    try:
        data = request.get_json()
        server = data.get('server')
        database = data.get('database')
        username = data.get('username')
        password = data.get('password')
        
        # สร้าง config object
        config = {
            'server': server,
            'database': database,
            'auth_type': 'SQL',
            'username': username,
            'password': password
        }
        
        # สร้าง connection string
        connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
        
        # ทดสอบการเชื่อมต่อ
        global db_manager
        
        # สร้าง connection_info สำหรับ DatabaseManager
        connection_info = {
            'config': config,
            'connection_string': connection_string,
            'current_user': username
        }
        
        db_manager = DatabaseManager(connection_info)
        if db_manager.test_connection():
            # บันทึกข้อมูลใน session
            session['db_config'] = {
                'server': server,
                'database': database,
                'username': username
            }
            
            return jsonify({'success': True, 'message': 'เชื่อมต่อฐานข้อมูลสำเร็จ'})
        else:
            return jsonify({'success': False, 'message': 'การทดสอบการเชื่อมต่อล้มเหลว'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'})

@app.route('/api/job_types')
def get_job_types():
    """API สำหรับดึงรายการ Job Types"""
    try:
        if not db_manager:
            print("❌ ไม่มี db_manager")
            return jsonify({'success': False, 'message': 'ไม่มีการเชื่อมต่อฐานข้อมูล'})
        
        print("🔍 กำลังดึงข้อมูล Job Types...")
        query = "SELECT id, name FROM job_types WHERE is_active = 1 ORDER BY name"
        print(f"📝 Query: {query}")
        
        results = db_manager.execute_query(query)
        print(f"📊 ผลลัพธ์: {len(results) if results else 0} รายการ")
        
        if results:
            for row in results:
                print(f"  - ID: {row['id']}, Name: {row['name']}")
        
        job_types = [{'id': row['id'], 'name': row['name']} for row in results] if results else []
        return jsonify({'success': True, 'data': job_types})
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดใน get_job_types: {str(e)}")
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'})

@app.route('/api/sub_job_types/<int:job_type_id>')
def get_sub_job_types(job_type_id):
    """API สำหรับดึงรายการ Sub Job Types"""
    try:
        if not db_manager:
            print("❌ ไม่มี db_manager")
            return jsonify({'success': False, 'message': 'ไม่มีการเชื่อมต่อฐานข้อมูล'})
        
        print(f"🔍 กำลังดึงข้อมูล Sub Job Types สำหรับ Job Type ID: {job_type_id}")
        query = "SELECT id, name FROM sub_job_types WHERE job_type_id = ? AND is_active = 1 ORDER BY name"
        print(f"📝 Query: {query}")
        print(f"🔢 Parameter: job_type_id = {job_type_id}")
        
        results = db_manager.execute_query(query, (job_type_id,))
        print(f"📊 ผลลัพธ์: {len(results) if results else 0} รายการ")
        
        if results:
            for row in results:
                print(f"  - ID: {row['id']}, Name: {row['name']}")
        
        sub_job_types = [{'id': row['id'], 'name': row['name']} for row in results] if results else []
        return jsonify({'success': True, 'data': sub_job_types})
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดใน get_sub_job_types: {str(e)}")
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'})

@app.route('/api/scan', methods=['POST'])
def scan_barcode():
    """API สำหรับสแกนบาร์โค้ด"""
    try:
        if not db_manager:
            return jsonify({'success': False, 'message': 'ไม่มีการเชื่อมต่อฐานข้อมูล'})
        
        data = request.get_json()
        barcode = data.get('barcode')
        job_type_id = data.get('job_type_id')
        sub_job_type_id = data.get('sub_job_type_id')
        note = data.get('note', '')  # หมายเหตุ (ไม่บังคับ)
        
        if not all([barcode, job_type_id, sub_job_type_id]):
            return jsonify({'success': False, 'message': 'กรุณากรอกข้อมูลให้ครบถ้วน'})
        
        # ตรวจสอบว่าบาร์โค้ดนี้ถูกสแกนไปแล้วหรือไม่
        check_query = """
            SELECT id, scan_datetime, job_type_name, sub_job_type_name 
            FROM scan_records 
            WHERE barcode = ? 
            ORDER BY scan_datetime DESC 
            LIMIT 1
        """
        existing = db_manager.execute_query(check_query, (barcode,))
        
        if existing:
            existing_record = existing[0]
            return jsonify({
                'success': False, 
                'message': 'บาร์โค้ดนี้ถูกสแกนไปแล้ว',
                'duplicate': True,
                'existing_record': {
                    'scan_datetime': existing_record['scan_datetime'].isoformat(),
                    'job_type_name': existing_record['job_type_name'],
                    'sub_job_type_name': existing_record['sub_job_type_name']
                }
            })
        
        # บันทึกการสแกนใหม่ (รวมหมายเหตุ)
        insert_query = """
            INSERT INTO scan_records (barcode, job_type_id, sub_job_type_id, scan_datetime, created_at, note)
            VALUES (?, ?, ?, GETDATE(), GETDATE(), ?)
        """
        db_manager.execute_query(insert_query, (barcode, job_type_id, sub_job_type_id, note))
        
        return jsonify({'success': True, 'message': 'บันทึกการสแกนสำเร็จ'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'})

@app.route('/api/history')
def get_scan_history():
    """API สำหรับดึงประวัติการสแกน"""
    try:
        if not db_manager:
            return jsonify({'success': False, 'message': 'ไม่มีการเชื่อมต่อฐานข้อมูล'})
        
        query = """
            SELECT TOP 50 
                sr.scan_datetime,
                sr.barcode,
                jt.name as job_type_name,
                sjt.name as sub_job_type_name,
                sr.note,
                CASE 
                    WHEN sr.scan_datetime >= DATEADD(MINUTE, -5, GETDATE()) THEN 'ใหม่'
                    ELSE 'ปกติ'
                END as status
            FROM scan_records sr
            JOIN job_types jt ON sr.job_type_id = jt.id
            JOIN sub_job_types sjt ON sr.sub_job_type_id = sjt.id
            ORDER BY sr.scan_datetime DESC
        """
        results = db_manager.execute_query(query)
        
        history = []
        for row in results:
            history.append({
                'scan_datetime': row['scan_datetime'].isoformat(),
                'barcode': row['barcode'],
                'job_type_name': row['job_type_name'],
                'sub_job_type_name': row['sub_job_type_name'],
                'note': row['note'] or '',
                'status': row['status']
            })
        
        return jsonify({'success': True, 'data': history})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'})

@app.route('/api/status')
def get_status():
    """API สำหรับตรวจสอบสถานะการเชื่อมต่อ"""
    try:
        if db_manager:
            db_manager.test_connection()
            return jsonify({'success': True, 'connected': True})
        else:
            return jsonify({'success': True, 'connected': False})
    except:
        return jsonify({'success': True, 'connected': False})

if __name__ == '__main__':
    # สร้างโฟลเดอร์ templates ถ้ายังไม่มี
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("🚀 เริ่มต้น WMS Barcode Scanner Web Application")
    print("📱 สามารถเข้าถึงได้ที่: http://localhost:5000")
    print("📱 สำหรับ Android: http://[IP_ADDRESS]:5000")
    print("💡 ใช้ IP Address ของเครื่องนี้แทน [IP_ADDRESS]")
    
    # เริ่มต้นการเชื่อมต่อฐานข้อมูล
    print("🔗 กำลังเชื่อมต่อฐานข้อมูล...")
    if initialize_database():
        print("✅ พร้อมใช้งาน - ฐานข้อมูลเชื่อมต่อสำเร็จ")
    else:
        print("⚠️ แอปพลิเคชันจะทำงานในโหมด Offline")
    
    app.run(host='0.0.0.0', port=5000, debug=True) 