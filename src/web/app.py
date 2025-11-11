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
from typing import Optional

# Load environment variables from .env file (if available)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, skip loading .env file
    pass

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.database_manager import DatabaseManager
from src.database import (
    JobTypeRepository,
    SubJobRepository,
    ScanLogRepository,
    DependencyRepository
)
from src.services import (
    ScanService,
    DependencyService,
    ReportService
)
from src.models.data_models import ScanRecord

app = Flask(__name__)

# Configuration from environment variables with fallback to defaults
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'wms_scanner_secret_key_2024')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_UPLOAD_SIZE', '10')) * 1024 * 1024  # MB to bytes

# CORS configuration
cors_origins = os.getenv('CORS_ORIGINS', '*')
if cors_origins == '*':
    CORS(app)
else:
    CORS(app, origins=cors_origins.split(','))

# Global database manager, repositories, and services
db_manager = None
job_type_repo = None
sub_job_repo = None
scan_log_repo = None
dependency_repo = None
scan_service = None
dependency_service = None
report_service = None

def get_database_config() -> Optional[dict]:
    """
    Get database configuration from environment variables or config file.
    Priority: Environment Variables > config/sql_config.json
    """
    # Try to get config from environment variables first
    db_server = os.getenv('DB_SERVER')
    db_database = os.getenv('DB_DATABASE')
    db_auth_type = os.getenv('DB_AUTH_TYPE', 'SQL')

    if db_server and db_database:
        print("📋 Using database configuration from environment variables")
        config = {
            'server': db_server,
            'database': db_database,
            'auth_type': db_auth_type
        }

        if db_auth_type == 'SQL':
            db_username = os.getenv('DB_USERNAME')
            db_password = os.getenv('DB_PASSWORD')
            if not db_username or not db_password:
                print("⚠️ DB_USERNAME or DB_PASSWORD not set in environment variables")
                return None
            config['username'] = db_username
            config['password'] = db_password

        # Build connection string
        driver = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
        if db_auth_type == 'SQL':
            connection_string = f"DRIVER={{{driver}}};SERVER={db_server};DATABASE={db_database};UID={db_username};PWD={db_password}"
            current_user = db_username
        else:
            connection_string = f"DRIVER={{{driver}}};SERVER={db_server};DATABASE={db_database};Trusted_Connection=yes"
            current_user = os.getenv('USERNAME', 'Windows User')

        return {
            'config': config,
            'connection_string': connection_string,
            'current_user': current_user
        }

    # Fallback to config file (legacy method)
    print("📋 Trying to load database configuration from config/sql_config.json")
    return None

def initialize_database():
    """เริ่มต้นการเชื่อมต่อฐานข้อมูล"""
    global db_manager, job_type_repo, sub_job_repo, scan_log_repo, dependency_repo
    global scan_service, dependency_service, report_service
    try:
        print("🔗 กำลังเชื่อมต่อฐานข้อมูล...")

        # Try to get config from environment variables first
        connection_info = get_database_config()

        # สร้าง DatabaseManager (จะโหลด config จากไฟล์โดยอัตโนมัติถ้าไม่มี connection_info)
        db_manager = DatabaseManager(connection_info) if connection_info else DatabaseManager()

        if db_manager.test_connection():
            config = db_manager.get_config()
            print(f"✅ เชื่อมต่อฐานข้อมูลสำเร็จ: {config.get('server', '')}/{config.get('database', '')}")

            # สร้าง repository instances
            job_type_repo = JobTypeRepository(db_manager)
            sub_job_repo = SubJobRepository(db_manager)
            scan_log_repo = ScanLogRepository(db_manager)
            dependency_repo = DependencyRepository(db_manager)
            print("✅ สร้าง repositories สำเร็จ")

            # สร้าง service instances
            scan_service = ScanService(
                scan_log_repo=scan_log_repo,
                sub_job_repo=sub_job_repo,
                dependency_repo=dependency_repo
            )
            dependency_service = DependencyService(
                dependency_repo=dependency_repo,
                job_type_repo=job_type_repo
            )
            report_service = ReportService(
                scan_log_repo=scan_log_repo,
                job_type_repo=job_type_repo,
                sub_job_repo=sub_job_repo
            )
            print("✅ สร้าง services สำเร็จ")

            # ตรวจสอบและสร้างตารางที่จำเป็น
            ensure_tables_exist()

            return True
        else:
            print("❌ การทดสอบการเชื่อมต่อล้มเหลว")
            return False
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อฐานข้อมูล: {e}")
        return False

def check_dependencies(barcode, job_type_id):
    """ตรวจสอบ Dependencies ของงาน (เหมือน Desktop App)"""
    try:
        # ตรวจสอบ Dependencies ผ่าน DependencyRepository
        required_jobs = dependency_repo.get_required_jobs(job_type_id)

        if not required_jobs:
            # ไม่มี dependencies สามารถสแกนได้
            return {'success': True, 'message': 'ไม่มี dependencies'}

        # ตรวจสอบว่าทุกงานที่จำเป็นถูกสแกนแล้วหรือไม่
        for required_job in required_jobs:
            required_job_id = required_job['required_job_id']
            required_job_name = required_job['job_name']

            # ตรวจสอบว่างานที่จำเป็นถูกสแกนแล้วหรือไม่ ผ่าน ScanLogRepository
            duplicate = scan_log_repo.check_duplicate(
                barcode=barcode,
                job_id=required_job_id,
                hours=24*365  # ตรวจสอบย้อนหลัง 1 ปี (ไม่จำกัดเวลา)
            )

            if duplicate is None:
                # งานที่จำเป็นยังไม่ถูกสแกน
                print(f"❌ ไม่มีงาน {required_job_name} สำหรับบาร์โค้ด {barcode}")
                return {
                    'success': False,
                    'message': f'ไม่สามารถสแกนได้ - ต้องสแกนงาน "{required_job_name}" ก่อน'
                }

        # ทุก dependencies ถูกต้อง
        return {'success': True, 'message': 'Dependencies ถูกต้อง'}

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการตรวจสอบ Dependencies: {str(e)}")
        return {'success': False, 'message': f'เกิดข้อผิดพลาดในการตรวจสอบ Dependencies: {str(e)}'}

def ensure_tables_exist():
    """ตรวจสอบและสร้างตารางที่จำเป็น"""
    try:
        # สร้างตารางผ่าน repositories
        if job_type_repo.ensure_table_exists():
            print("✅ ตาราง job_types พร้อมใช้งาน")

        if sub_job_repo.ensure_table_exists():
            print("✅ ตาราง sub_job_types พร้อมใช้งาน")

        if scan_log_repo.ensure_table_exists():
            print("✅ ตาราง scan_logs พร้อมใช้งาน")

            # สร้าง indexes สำหรับ scan_logs
            if scan_log_repo.ensure_indexes_exist():
                print("✅ สร้าง indexes สำเร็จ")

        if dependency_repo.ensure_table_exists():
            print("✅ ตาราง job_dependencies พร้อมใช้งาน")

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
        if not job_type_repo:
            print("❌ ไม่มี job_type_repo")
            return jsonify({'success': False, 'message': 'ไม่มีการเชื่อมต่อฐานข้อมูล'})

        print("🔍 กำลังดึงข้อมูล Job Types...")
        results = job_type_repo.get_all_job_types()
        print(f"📊 ผลลัพธ์: {len(results) if results else 0} รายการ")

        # ถ้าไม่มีข้อมูล ให้เพิ่มข้อมูลตัวอย่าง
        if not results:
            print("⚠️ ไม่พบข้อมูล Job Types จะเพิ่มข้อมูลตัวอย่าง...")

            sample_data = [
                '1.Release',
                '2.Inprocess',
                '3.Outbound',
                '4.Loading',
                '5.Return',
                '6.Repack'
            ]

            for job_name in sample_data:
                try:
                    if not job_type_repo.job_name_exists(job_name):
                        job_type_repo.create_job_type(job_name)
                        print(f"✅ เพิ่ม Job Type: {job_name}")
                except Exception as e:
                    print(f"⚠️ ไม่สามารถเพิ่ม Job Type {job_name}: {str(e)}")

            # ดึงข้อมูลใหม่
            results = job_type_repo.get_all_job_types()
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
        if not sub_job_repo:
            print("❌ ไม่มี sub_job_repo")
            return jsonify({'success': False, 'message': 'ไม่มีการเชื่อมต่อฐานข้อมูล'})

        print(f"🔍 กำลังดึงข้อมูล Sub Job Types สำหรับ Job Type ID: {job_type_id}")

        results = sub_job_repo.get_by_main_job(job_type_id, active_only=True)
        print(f"📊 ผลลัพธ์: {len(results) if results else 0} รายการ")

        # ถ้าไม่มีข้อมูล ให้เพิ่มข้อมูลตัวอย่าง
        if not results:
            print("⚠️ ไม่พบข้อมูล Sub Job Types จะเพิ่มข้อมูลตัวอย่าง...")

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
                        if not sub_job_repo.duplicate_exists(job_type_id, sub_job_name[0]):
                            sub_job_repo.create_sub_job(job_type_id, sub_job_name[0])
                            print(f"✅ เพิ่ม Sub Job Type: {sub_job_name[0]} สำหรับ Job Type ID: {job_type_id}")
                    except Exception as e:
                        print(f"⚠️ ไม่สามารถเพิ่ม Sub Job Type {sub_job_name[0]}: {str(e)}")

                # ดึงข้อมูลใหม่
                results = sub_job_repo.get_by_main_job(job_type_id, active_only=True)
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
    """API สำหรับสแกนบาร์โค้ด using ScanService"""
    try:
        print(f"🔍 เริ่มต้นการสแกนบาร์โค้ด...")

        if not scan_service:
            print("❌ ไม่มี scan service")
            return jsonify({'success': False, 'message': 'ไม่มีการเชื่อมต่อฐานข้อมูล'})

        data = request.get_json()
        barcode = data.get('barcode')
        job_type_id = data.get('job_type_id')
        sub_job_type_id = data.get('sub_job_type_id')
        note = data.get('note', '')

        print(f"📝 ข้อมูลที่ได้รับ: barcode={barcode}, job_type_id={job_type_id}, sub_job_type_id={sub_job_type_id}, note={note}")

        # Basic validation
        if not barcode:
            return jsonify({'success': False, 'message': 'กรุณากรอกบาร์โค้ด'})

        if not job_type_id:
            return jsonify({'success': False, 'message': 'กรุณาเลือก Job Type'})

        # Get job type info
        job_info = job_type_repo.find_by_id(job_type_id)
        if not job_info:
            return jsonify({'success': False, 'message': 'ไม่พบ Job Type ที่เลือก'})

        job_type_name = job_info['job_name']

        # Get sub job type info if provided
        sub_job_type_name = None
        if sub_job_type_id:
            sub_info = sub_job_repo.get_details(sub_job_type_id)
            if sub_info:
                sub_job_type_name = sub_info['sub_job_name']

        # Use ScanService to process the scan (handles all business logic)
        result = scan_service.process_scan(
            barcode=barcode,
            job_type_name=job_type_name,
            job_id=job_type_id,
            sub_job_type_name=sub_job_type_name or "",
            user_id=db_manager.current_user,
            notes=note
        )

        # Handle the result
        if not result['success']:
            print(f"❌ Scan failed: {result['message']}")
            # Check if it's a duplicate
            if 'ซ้ำ' in result['message'] or 'duplicate' in result['message'].lower():
                duplicate_info = result['data'].get('duplicate_info', {})
                return jsonify({
                    'success': False,
                    'message': result['message'],
                    'duplicate': True,
                    'existing_record': {
                        'scan_date': duplicate_info.get('scan_date', ''),
                        'job_type_name': job_type_name,
                        'sub_job_type_name': sub_job_type_name or 'ไม่มี',
                        'user_id': duplicate_info.get('user_id', '')
                    }
                })
            else:
                return jsonify({'success': False, 'message': result['message']})

        print(f"✅ บันทึกสำเร็จ")
        return jsonify({'success': True, 'message': f'บันทึกการสแกนบาร์โค้ด: {barcode}'})

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'ไม่สามารถบันทึกการสแกน: {str(e)}'})

@app.route('/api/history')
def get_scan_history():
    """API สำหรับดึงประวัติการสแกน - ทำงานเหมือน Desktop App"""
    try:
        if not db_manager:
            return jsonify({'success': False, 'message': 'ไม่มีการเชื่อมต่อฐานข้อมูล'})

        # ใช้ db_manager โดยตรงเพื่อรวม job_type_name (get_recent_scans ไม่มี JOIN กับ job_types)
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
                'scan_date': row['scan_date'].isoformat() if hasattr(row['scan_date'], 'isoformat') else str(row['scan_date']),
                'barcode': row['barcode'],
                'job_type_name': row['job_type_name'],
                'sub_job_type_name': row['sub_job_type_name'],
                'notes': row.get('notes') or '',
                'user_id': row['user_id'],
                'status': row['status']
            })

        return jsonify({'success': True, 'data': history})

    except Exception as e:
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'})

@app.route('/health')
def health_check():
    """Health check endpoint for Docker/Kubernetes"""
    try:
        # Basic health check - just return 200 if app is running
        return jsonify({
            'status': 'healthy',
            'service': 'wms-barcode-scanner-web',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503

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

@app.route('/api/today_summary')
def get_today_summary():
    """API สำหรับดึงสรุปงานที่สแกนวันนี้"""
    try:
        if not scan_log_repo or not job_type_repo or not sub_job_repo:
            return jsonify({'success': False, 'message': 'ไม่มีการเชื่อมต่อฐานข้อมูล'})

        job_type_id = request.args.get('job_type_id')
        sub_job_type_id = request.args.get('sub_job_type_id')
        note_filter = request.args.get('note_filter')

        if not job_type_id:
            return jsonify({'success': True, 'data': {'total_count': 0, 'message': 'กรุณาเลือก Job Type'}})

        # ใช้ get_today_summary_count จาก repository (ไม่รองรับ note_filter)
        # ถ้ามี note_filter ต้องใช้ db_manager โดยตรง
        if note_filter and note_filter.strip():
            # ใช้ db_manager สำหรับกรณีมี note_filter
            if sub_job_type_id and sub_job_type_id != '':
                count_query = """
                    SELECT COUNT(*) as total_count
                    FROM scan_logs sl
                    WHERE sl.job_id = ?
                    AND sl.sub_job_id = ?
                    AND CAST(sl.scan_date AS DATE) = CAST(GETDATE() AS DATE)
                    AND sl.notes LIKE ?
                """
                params = (job_type_id, sub_job_type_id, f"%{note_filter.strip()}%")
            else:
                count_query = """
                    SELECT COUNT(*) as total_count
                    FROM scan_logs sl
                    WHERE sl.job_id = ?
                    AND CAST(sl.scan_date AS DATE) = CAST(GETDATE() AS DATE)
                    AND sl.notes LIKE ?
                """
                params = (job_type_id, f"%{note_filter.strip()}%")

            result = db_manager.execute_query(count_query, params)
            total_count = result[0]['total_count'] if result else 0
        else:
            # ใช้ repository สำหรับกรณีไม่มี note_filter
            total_count = scan_log_repo.get_today_summary_count(
                job_id=job_type_id,
                sub_job_id=sub_job_type_id if sub_job_type_id and sub_job_type_id != '' else None
            )

        # ดึงข้อมูล Job Type และ Sub Job Type สำหรับแสดงผล
        job_type_query = "SELECT job_name FROM job_types WHERE id = ?"
        job_result = db_manager.execute_query(job_type_query, (job_type_id,))
        job_type_name = job_result[0]['job_name'] if job_result else 'ไม่ทราบ'

        sub_job_type_name = 'ไม่มี'
        if sub_job_type_id and sub_job_type_id != '':
            sub_result = sub_job_repo.get_details(sub_job_type_id)
            if sub_result:
                sub_job_type_name = sub_result['sub_job_name']

        return jsonify({
            'success': True,
            'data': {
                'total_count': total_count,
                'job_type_name': job_type_name,
                'sub_job_type_name': sub_job_type_name,
                'note_filter': note_filter.strip() if note_filter and note_filter.strip() else None,
                'date': datetime.now().strftime('%Y-%m-%d')
            }
        })

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการดึงสรุปงานวันนี้: {str(e)}")
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาดในการดึงสรุปงานวันนี้: {str(e)}'})

@app.route('/api/report', methods=['POST'])
def generate_report():
    """API สำหรับสร้างรายงาน"""
    try:
        if not scan_log_repo or not job_type_repo or not sub_job_repo:
            return jsonify({'success': False, 'message': 'ไม่มีการเชื่อมต่อฐานข้อมูล'})

        data = request.get_json()
        report_date = data.get('report_date')
        job_type_id = data.get('job_type_id')
        sub_job_type_id = data.get('sub_job_type_id')
        note_filter = data.get('note_filter')

        if not report_date:
            return jsonify({'success': False, 'message': 'กรุณาเลือกวันที่'})

        if not job_type_id:
            return jsonify({'success': False, 'message': 'กรุณาเลือกงานหลัก'})

        # แปลงวันที่เป็นรูปแบบที่เหมาะสม
        try:
            from datetime import datetime
            report_date_obj = datetime.strptime(report_date, '%Y-%m-%d')
            start_date = report_date_obj.strftime('%Y-%m-%d 00:00:00')
            end_date = report_date_obj.strftime('%Y-%m-%d 23:59:59')
        except:
            return jsonify({'success': False, 'message': 'รูปแบบวันที่ไม่ถูกต้อง'})

        # ดึงข้อมูล Job Type และ Sub Job Type
        job_type_query = "SELECT job_name FROM job_types WHERE id = ?"
        job_result = db_manager.execute_query(job_type_query, (job_type_id,))
        if not job_result:
            return jsonify({'success': False, 'message': 'ไม่พบงานหลักที่เลือก'})

        job_type_name = job_result[0]['job_name']
        sub_job_type_name = None

        if sub_job_type_id:
            sub_result = sub_job_repo.get_details(sub_job_type_id)
            if sub_result:
                sub_job_type_name = sub_result['sub_job_name']
            else:
                return jsonify({'success': False, 'message': 'ไม่พบงานรองที่เลือก'})

        # ใช้ repository สำหรับดึงข้อมูลรายงาน (ไม่รองรับ note_filter)
        # ถ้ามี note_filter ต้องใช้ db_manager โดยตรง
        if note_filter and note_filter.strip():
            # ใช้ db_manager สำหรับกรณีมี note_filter
            if sub_job_type_id:
                # มีงานรอง
                report_query = """
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
                    AND CAST(sl.scan_date AS DATE) = ?
                    AND sl.notes LIKE ?
                    ORDER BY sl.scan_date DESC
                """
                params = (job_type_id, sub_job_type_id, report_date, f"%{note_filter.strip()}%")
            else:
                # ไม่มีงานรอง - แสดงเฉพาะงานหลัก (ไม่กรอง sub_job_id)
                report_query = """
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
                    AND sl.notes LIKE ?
                    ORDER BY sl.scan_date DESC
                """
                params = (job_type_id, report_date, f"%{note_filter.strip()}%")

            results = db_manager.execute_query(report_query, params)
        else:
            # ใช้ repository สำหรับกรณีไม่มี note_filter
            if sub_job_type_id:
                # มีงานรอง - ใช้ get_report_with_sub_job
                results = scan_log_repo.get_report_with_sub_job(
                    start_date=start_date,
                    end_date=end_date,
                    job_id=job_type_id,
                    sub_job_id=sub_job_type_id
                )
            else:
                # ไม่มีงานรอง - ใช้ get_report_main_job_only
                results = scan_log_repo.get_report_main_job_only(
                    start_date=start_date,
                    end_date=end_date,
                    job_id=job_type_id
                )

            # เพิ่ม job_type_name และ sub_job_type_name ให้กับผลลัพธ์
            for row in results:
                if 'job_type_name' not in row:
                    row['job_type_name'] = job_type_name
                if 'sub_job_type_name' not in row:
                    if sub_job_type_id:
                        row['sub_job_type_name'] = sub_job_type_name
                    else:
                        row['sub_job_type_name'] = 'ไม่มี'

        # นับจำนวนรวม
        total_count = len(results) if results else 0

        # แปลงข้อมูลสำหรับส่งกลับ
        report_data = []
        for row in results:
            report_data.append({
                'barcode': row['barcode'],
                'scan_date': row['scan_date'].isoformat() if hasattr(row['scan_date'], 'isoformat') else str(row['scan_date']),
                'notes': row.get('notes') or '',
                'user_id': row['user_id'],
                'job_type_name': row['job_type_name'],
                'sub_job_type_name': row.get('sub_job_type_name') or 'ไม่มี'
            })

        # สร้างข้อมูลสรุป
        summary = {
            'report_date': report_date,
            'job_type_name': job_type_name,
            'sub_job_type_name': sub_job_type_name or 'ไม่มี',
            'note_filter': note_filter.strip() if note_filter and note_filter.strip() else None,
            'total_count': total_count,
            'generated_at': datetime.now().isoformat()
        }

        return jsonify({
            'success': True,
            'summary': summary,
            'data': report_data
        })

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการสร้างรายงาน: {str(e)}")
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาดในการสร้างรายงาน: {str(e)}'})

if __name__ == '__main__':
    # สร้างโฟลเดอร์ templates ถ้ายังไม่มี
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)

    # Get Flask configuration from environment variables
    flask_host = os.getenv('FLASK_HOST', '0.0.0.0')
    flask_port = int(os.getenv('FLASK_PORT', '5000'))
    flask_debug = os.getenv('FLASK_DEBUG', '0') == '1'
    flask_env = os.getenv('FLASK_ENV', 'development')

    print("🚀 เริ่มต้น WMS Barcode Scanner Web Application")
    print(f"🌍 Environment: {flask_env}")
    print(f"📱 สามารถเข้าถึงได้ที่: http://localhost:{flask_port}")
    print(f"📱 สำหรับ Android: http://[IP_ADDRESS]:{flask_port}")
    print("💡 ใช้ IP Address ของเครื่องนี้แทน [IP_ADDRESS]")
    print(f"🔧 Debug mode: {'ON' if flask_debug else 'OFF'}")

    # เริ่มต้นการเชื่อมต่อฐานข้อมูล
    print("🔗 กำลังเชื่อมต่อฐานข้อมูล...")
    if initialize_database():
        print("✅ พร้อมใช้งาน - ฐานข้อมูลเชื่อมต่อสำเร็จ")
    else:
        print("⚠️ แอปพลิเคชันจะทำงานในโหมด Offline")

    app.run(host=flask_host, port=flask_port, debug=flask_debug) 