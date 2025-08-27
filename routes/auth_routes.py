#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authentication Routes
Handles authentication and initialization endpoints
"""

import logging
from flask import Blueprint, request, jsonify, session
from src.database.database_manager import DatabaseManager
from config_utils.config_manager import config_manager
from middleware.rate_limiter import rate_limit

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/init')
@rate_limit(max_requests=50, per_seconds=60)
def initialize_app():
    """API สำหรับเริ่มต้นแอปพลิเคชัน"""
    try:
        logger.info("กำลังเริ่มต้นแอปพลิเคชัน...")
        
        # Load database config
        config = config_manager.load_database_config()
        if not config:
            return jsonify({
                'success': False, 
                'message': 'ไม่สามารถโหลดการตั้งค่าฐานข้อมูลได้',
                'connected': False
            })
        
        # Create connection info
        connection_info = config_manager.create_connection_info(config)
        
        # Test connection
        db_manager = DatabaseManager.get_instance(connection_info)
        if db_manager.test_connection():
            # Ensure required tables exist
            from web.database_service import ensure_tables_exist
            ensure_tables_exist(db_manager)
            
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
        logger.error(f"เกิดข้อผิดพลาดในการเริ่มต้นแอป: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'เกิดข้อผิดพลาด: {str(e)}',
            'connected': False
        })


@auth_bp.route('/api/login', methods=['POST'])
@rate_limit(max_requests=20, per_seconds=60)
def login():
    """API สำหรับ login"""
    try:
        data = request.get_json()
        server = data.get('server')
        database = data.get('database')
        username = data.get('username')
        password = data.get('password')
        
        # Validate input
        if not all([server, database, username, password]):
            return jsonify({
                'success': False, 
                'message': 'กรุณากรอกข้อมูลให้ครบถ้วน'
            })
        
        # สร้าง config object
        config = {
            'server': server,
            'database': database,
            'auth_type': 'SQL',
            'username': username,
            'password': password
        }
        
        # Create connection info and test connection
        connection_info = config_manager.create_connection_info(config)
        
        db_manager = DatabaseManager.get_instance(connection_info)
        if db_manager.test_connection():
            # บันทึกข้อมูลใน session
            session['db_config'] = {
                'server': server,
                'database': database,
                'username': username,
                'password': password  # ในการใช้งานจริงควร encrypt
            }
            session.permanent = True
            
            logger.info(f"User {username} logged in successfully")
            return jsonify({
                'success': True, 
                'message': 'เชื่อมต่อฐานข้อมูลสำเร็จ'
            })
        else:
            logger.warning(f"Login failed for user {username}")
            return jsonify({
                'success': False, 
                'message': 'การทดสอบการเชื่อมต่อล้มเหลว'
            })
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        })


@auth_bp.route('/api/status')
@rate_limit(max_requests=50, per_seconds=60)
def get_status():
    """API สำหรับตรวจสอบสถานะการเชื่อมต่อ"""
    try:
        from web.database_service import get_db_manager
        
        db_manager = get_db_manager()
        if db_manager and db_manager.test_connection():
            return jsonify({'success': True, 'connected': True})
        else:
            return jsonify({'success': True, 'connected': False})
    except:
        return jsonify({'success': True, 'connected': False})


@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    """API สำหรับ logout"""
    try:
        session.clear()
        return jsonify({
            'success': True,
            'message': 'ออกจากระบบสำเร็จ'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        })