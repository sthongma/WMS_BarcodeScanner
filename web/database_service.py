#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Database Service
Handles database operations specific to web application
"""

import logging
from flask import session
from src.database.database_manager import DatabaseManager
from config_utils.config_manager import config_manager

logger = logging.getLogger(__name__)


def get_db_manager(context: str = None):
    """ดึง database manager (Singleton) สำหรับ web application"""
    try:
        # ใช้ข้อมูลจาก session เท่านั้น (ไม่ fallback ไป config file)
        if 'db_config' in session:
            config = session['db_config']
            connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config['server']};DATABASE={config['database']};UID={config['username']};PWD={config.get('password', '')}"
            
            connection_info = {
                'config': config,
                'connection_string': connection_string,
                'current_user': config['username']
            }
            
            # Log การเรียกใช้ get_db_manager พร้อม context
            if context:
                logger.debug(f"📡 get_db_manager called from: {context}")
            
            # ใช้ Singleton DatabaseManager
            db_manager = DatabaseManager.get_instance(connection_info)
            if hasattr(db_manager, 'update_connection_from_info'):
                db_manager.update_connection_from_info(connection_info, context)
            return db_manager
        else:
            # ไม่มี session = ต้อง login ก่อน
            return None
        
    except Exception as e:
        logger.error(f"Error getting database manager: {str(e)}")
        return None


def initialize_database():
    """เริ่มต้นการเชื่อมต่อฐานข้อมูล - ไม่ทำอะไร เพราะต้อง login ก่อน"""
    # ไม่โหลด config อัตโนมัติ - ให้ผู้ใช้ login ก่อน
    logger.info("INIT: ไม่เชื่อมต่อฐานข้อมูลอัตโนมัติ - รอการ login")
    return True


def ensure_tables_exist(db_manager=None):
    """ตรวจสอบและสร้างตารางที่จำเป็น"""
    if not db_manager:
        db_manager = get_db_manager()
        if not db_manager:
            logger.error("ไม่สามารถดึง database manager ได้")
            return False
    
    try:
        # Use JobService to ensure tables exist
        from src.services.job_service import JobService
        job_service = JobService()
        
        if job_service.ensure_tables_exist():
            logger.info("OK: ตรวจสอบตารางเรียบร้อย")
            
            # ตรวจสอบตาราง scan_logs
            try:
                check_query = "SELECT COUNT(*) as count FROM scan_logs"
                db_manager.execute_query(check_query)
                logger.info("OK: ตาราง scan_logs มีอยู่แล้ว")
            except:
                logger.info("INFO: ตาราง scan_logs ไม่มีอยู่ จะสร้างใหม่...")
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
                db_manager.execute_non_query(create_scan_logs_query)
                logger.info("OK: สร้างตาราง scan_logs สำเร็จ")
                
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
                        db_manager.execute_non_query(index_query)
                    except:
                        pass  # Index อาจมีอยู่แล้ว
                
                logger.info("OK: สร้าง indexes สำเร็จ")
            
            return True
        else:
            logger.error("ERROR: ไม่สามารถตรวจสอบตารางได้")
            return False
            
    except Exception as e:
        logger.error(f"WARNING: เกิดข้อผิดพลาดในการตรวจสอบตาราง {e}")
        return False


def get_connection_status():
    """ตรวจสอบสถานะการเชื่อมต่อ"""
    try:
        db_manager = get_db_manager()
        if db_manager and db_manager.test_connection():
            return {'connected': True, 'message': 'เชื่อมต่อฐานข้อมูลสำเร็จ'}
        else:
            return {'connected': False, 'message': 'ไม่สามารถเชื่อมต่อฐานข้อมูลได้'}
    except Exception as e:
        logger.error(f"Error checking connection status: {str(e)}")
        return {'connected': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}


def cleanup_expired_sessions():
    """ทำความสะอาด session ที่หมดอายุ"""
    # This would be implemented based on your session storage mechanism
    pass