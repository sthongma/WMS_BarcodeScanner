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
                    
                    # ตรวจสอบและสร้างตารางที่จำเป็น
                    ensure_tables_exist()
                    
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

def ensure_tables_exist():
    """ตรวจสอบและสร้างตารางที่จำเป็น"""
    try:
        # ตรวจสอบตาราง scan_logs
        try:
            check_query = "SELECT COUNT(*) as count FROM scan_logs"
            db_manager.execute_query(check_query)
            print("✅ ตาราง scan_logs มีอยู่แล้ว")
        except:
            print("❌ ตาราง scan_logs ไม่มีอยู่ จะสร้างใหม่...")
            create_scan_logs_query = """
            CREATE TABLE scan_logs (
                id INT IDENTITY(1,1) PRIMARY KEY,
                barcode VARCHAR(100) NOT NULL,
                scan_date DATETIME NOT NULL DEFAULT GETDATE(),
                job_type VARCHAR(100) NOT NULL,
                user_id VARCHAR(50) NOT NULL,
                job_id INT NULL,
                sub_job_id INT NULL,
                notes NVARCHAR(1000) NULL,
                CONSTRAINT FK_scan_logs_job_id 
                    FOREIGN KEY (job_id) REFERENCES job_types(id),
                CONSTRAINT FK_scan_logs_sub_job 
                    FOREIGN KEY (sub_job_id) REFERENCES sub_job_types(id)
            )
            """
            db_manager.execute_query(create_scan_logs_query)
            print("✅ สร้างตาราง scan_logs สำเร็จ")
            
            # สร้าง indexes
            indexes = [
                "CREATE INDEX IX_scan_logs_barcode ON scan_logs (barcode)",
                "CREATE INDEX IX_scan_logs_scan_date ON scan_logs (scan_date)",
                "CREATE INDEX IX_scan_logs_job_type ON scan_logs (job_type)",
                "CREATE INDEX IX_scan_logs_user_id ON scan_logs (user_id)",
                "CREATE INDEX IX_scan_logs_job_id ON scan_logs (job_id)",
                "CREATE INDEX IX_scan_logs_sub_job_id ON scan_logs(sub_job_id)"
            ]
            
            for index_query in indexes:
                try:
                    db_manager.execute_query(index_query)
                except:
                    pass  # Index อาจมีอยู่แล้ว
            
            print("✅ สร้าง indexes สำเร็จ")
            
    except Exception as e:
        print(f"⚠️ เกิดข้อผิดพลาดในการตรวจสอบตาราง: {e}")

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
        query = "SELECT id, job_name FROM job_types ORDER BY job_name"
        print(f"📝 Query: {query}")
        
        results = db_manager.execute_query(query)
        print(f"📊 ผลลัพธ์: {len(results) if results else 0} รายการ")
        
        # ถ้าไม่มีข้อมูล ให้เพิ่มข้อมูลตัวอย่าง
        if not results:
            print("⚠️ ไม่พบข้อมูล Job Types จะเพิ่มข้อมูลตัวอย่าง...")
            
            # ตรวจสอบว่าตารางมีอยู่หรือไม่
            try:
                check_table_query = "SELECT COUNT(*) as count FROM job_types"
                db_manager.execute_query(check_table_query)
                print("✅ ตาราง job_types มีอยู่แล้ว")
            except:
                print("❌ ตาราง job_types ไม่มีอยู่ จะสร้างใหม่...")
                create_table_query = """
                CREATE TABLE job_types (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    job_name VARCHAR(100) NOT NULL UNIQUE
                )
                """
                db_manager.execute_query(create_table_query)
                print("✅ สร้างตาราง job_types สำเร็จ")
            
            sample_data = [
                ('1.Release',),
                ('2.Inprocess',),
                ('3.Outbound',),
                ('4.Loading',),
                ('5.Return',),
                ('6.Repack',)
            ]
            
            for job_name in sample_data:
                try:
                    insert_query = "INSERT INTO job_types (job_name) VALUES (?)"
                    db_manager.execute_query(insert_query, job_name)
                    print(f"✅ เพิ่ม Job Type: {job_name[0]}")
                except Exception as e:
                    print(f"⚠️ ไม่สามารถเพิ่ม Job Type {job_name[0]}: {str(e)}")
            
            # ดึงข้อมูลใหม่
            results = db_manager.execute_query(query)
            print(f"📊 ผลลัพธ์ใหม่: {len(results) if results else 0} รายการ")
        
        if results:
            for row in results:
                print(f"  - ID: {row['id']}, Name: {row['job_name']}")
        
        job_types = [{'id': row['id'], 'name': row['job_name']} for row in results] if results else []
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
        query = "SELECT id, sub_job_name FROM sub_job_types WHERE main_job_id = ? AND is_active = 1 ORDER BY sub_job_name"
        print(f"📝 Query: {query}")
        print(f"🔢 Parameter: job_type_id = {job_type_id}")
        
        results = db_manager.execute_query(query, (job_type_id,))
        print(f"📊 ผลลัพธ์: {len(results) if results else 0} รายการ")
        
        # ถ้าไม่มีข้อมูล ให้เพิ่มข้อมูลตัวอย่าง
        if not results:
            print("⚠️ ไม่พบข้อมูล Sub Job Types จะเพิ่มข้อมูลตัวอย่าง...")
            
            # ตรวจสอบว่าตารางมีอยู่หรือไม่
            try:
                check_table_query = "SELECT COUNT(*) as count FROM sub_job_types"
                db_manager.execute_query(check_table_query)
                print("✅ ตาราง sub_job_types มีอยู่แล้ว")
            except:
                print("❌ ตาราง sub_job_types ไม่มีอยู่ จะสร้างใหม่...")
                create_table_query = """
                CREATE TABLE sub_job_types (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    main_job_id INT NOT NULL,
                    sub_job_name NVARCHAR(255) NOT NULL,
                    description NVARCHAR(500) NULL,
                    created_date DATETIME2 DEFAULT GETDATE(),
                    updated_date DATETIME2 DEFAULT GETDATE(),
                    is_active BIT DEFAULT 1,
                    CONSTRAINT FK_sub_job_types_main_job 
                        FOREIGN KEY (main_job_id) REFERENCES job_types(id) 
                        ON DELETE CASCADE,
                    CONSTRAINT UQ_sub_job_types_name_per_main 
                        UNIQUE (main_job_id, sub_job_name)
                )
                """
                db_manager.execute_query(create_table_query)
                print("✅ สร้างตาราง sub_job_types สำเร็จ")
            
            # ข้อมูลตัวอย่างตาม Job Type
            sample_sub_jobs = {
                1: [('รับสินค้าปกติ',), ('รับสินค้าด่วน',)],
                2: [('จัดส่งภายในประเทศ',), ('จัดส่งต่างประเทศ',)],
                3: [('ส่งออกปกติ',), ('ส่งออกด่วน',)],
                4: [('โหลดรถปกติ',), ('โหลดรถด่วน',)],
                5: [('คืนสินค้าปกติ',), ('คืนสินค้าด่วน',)],
                6: [('แพ็คใหม่',), ('แพ็คซ่อม',)]
            }
            
            if job_type_id in sample_sub_jobs:
                for sub_job_name in sample_sub_jobs[job_type_id]:
                    try:
                        insert_query = "INSERT INTO sub_job_types (main_job_id, sub_job_name, is_active) VALUES (?, ?, 1)"
                        db_manager.execute_query(insert_query, (job_type_id, sub_job_name[0]))
                        print(f"✅ เพิ่ม Sub Job Type: {sub_job_name[0]} สำหรับ Job Type ID: {job_type_id}")
                    except Exception as e:
                        print(f"⚠️ ไม่สามารถเพิ่ม Sub Job Type {sub_job_name[0]}: {str(e)}")
                
                # ดึงข้อมูลใหม่
                results = db_manager.execute_query(query, (job_type_id,))
                print(f"📊 ผลลัพธ์ใหม่: {len(results) if results else 0} รายการ")
        
        if results:
            for row in results:
                print(f"  - ID: {row['id']}, Name: {row['sub_job_name']}")
        
        sub_job_types = [{'id': row['id'], 'name': row['sub_job_name']} for row in results] if results else []
        return jsonify({'success': True, 'data': sub_job_types})
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดใน get_sub_job_types: {str(e)}")
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'})

@app.route('/api/scan', methods=['POST'])
def scan_barcode():
    """API สำหรับสแกนบาร์โค้ด - ทำงานเหมือน Desktop App"""
    try:
        if not db_manager:
            return jsonify({'success': False, 'message': 'ไม่มีการเชื่อมต่อฐานข้อมูล'})
        
        data = request.get_json()
        barcode = data.get('barcode')
        job_type_id = data.get('job_type_id')
        sub_job_type_id = data.get('sub_job_type_id')
        note = data.get('note', '')  # หมายเหตุ (ไม่บังคับ)
        
        if not barcode:
            return jsonify({'success': False, 'message': 'กรุณากรอกบาร์โค้ด'})
        
        if not job_type_id:
            return jsonify({'success': False, 'message': 'กรุณาเลือก Job Type'})
        
        # ตรวจสอบว่าบาร์โค้ดซ้ำหรือไม่ (เหมือน Desktop App)
        check_query = """
            SELECT sl.*, jt.job_name as job_type_name, sjt.sub_job_name as sub_job_type_name
            FROM scan_logs sl
            LEFT JOIN job_types jt ON sl.job_type = jt.job_name
            LEFT JOIN sub_job_types sjt ON sl.sub_job_id = sjt.id
            WHERE sl.barcode = ?
            ORDER BY sl.scan_date DESC
        """
        existing_records = db_manager.execute_query(check_query, (barcode,))
        
        if existing_records:
            existing_record = existing_records[0]
            return jsonify({
                'success': False, 
                'message': f'บาร์โค้ด {barcode} ถูกสแกนแล้ว',
                'duplicate': True,
                'existing_record': {
                    'scan_date': existing_record['scan_date'].isoformat(),
                    'job_type_name': existing_record['job_type_name'] or existing_record['job_type'],
                    'sub_job_type_name': existing_record['sub_job_type_name'] or 'ไม่มี',
                    'user_id': existing_record['user_id']
                }
            })
        
        # ดึงข้อมูล Job Type และ Sub Job Type
        job_type_query = "SELECT job_name FROM job_types WHERE id = ?"
        job_result = db_manager.execute_query(job_type_query, (job_type_id,))
        
        if not job_result:
            return jsonify({'success': False, 'message': 'ไม่พบ Job Type ที่เลือก'})
        
        job_type_name = job_result[0]['job_name']
        sub_job_type_name = None
        
        if sub_job_type_id:
            sub_job_query = "SELECT sub_job_name FROM sub_job_types WHERE id = ?"
            sub_result = db_manager.execute_query(sub_job_query, (sub_job_type_id,))
            if sub_result:
                sub_job_type_name = sub_result[0]['sub_job_name']
        
        # บันทึกการสแกน (เหมือน Desktop App)
        insert_query = """
            INSERT INTO scan_logs (barcode, scan_date, job_type, user_id, job_id, sub_job_id, notes)
            VALUES (?, GETDATE(), ?, ?, ?, ?, ?)
        """
        db_manager.execute_query(insert_query, (
            barcode, job_type_name, db_manager.current_user, 
            job_type_id, sub_job_type_id, note
        ))
        
        return jsonify({'success': True, 'message': f'บันทึกการสแกนบาร์โค้ด: {barcode}'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'ไม่สามารถบันทึกการสแกน: {str(e)}'})

@app.route('/api/history')
def get_scan_history():
    """API สำหรับดึงประวัติการสแกน - ทำงานเหมือน Desktop App"""
    try:
        if not db_manager:
            return jsonify({'success': False, 'message': 'ไม่มีการเชื่อมต่อฐานข้อมูล'})
        
        query = """
            SELECT TOP 50 
                sl.scan_date,
                sl.barcode,
                jt.job_name as job_type_name,
                ISNULL(sjt.sub_job_name, 'ไม่มี') as sub_job_type_name,
                sl.notes,
                sl.user_id,
                CASE 
                    WHEN sl.scan_date >= DATEADD(MINUTE, -5, GETDATE()) THEN 'ใหม่'
                    ELSE 'ปกติ'
                END as status
            FROM scan_logs sl
            LEFT JOIN job_types jt ON sl.job_type = jt.job_name
            LEFT JOIN sub_job_types sjt ON sl.sub_job_id = sjt.id
            ORDER BY sl.scan_date DESC
        """
        results = db_manager.execute_query(query)
        
        history = []
        for row in results:
            history.append({
                'scan_date': row['scan_date'].isoformat(),
                'barcode': row['barcode'],
                'job_type_name': row['job_type_name'],
                'sub_job_type_name': row['sub_job_type_name'],
                'notes': row['notes'] or '',
                'user_id': row['user_id'],
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