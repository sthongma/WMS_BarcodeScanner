#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scan Routes
Handles scanning and history endpoints
"""

import logging
from flask import Blueprint, request, jsonify, session
from src.services.scan_service import ScanService
from src.services.audit_service import AuditService
from middleware.rate_limiter import auto_rate_limit
from middleware.auth_middleware import require_auth, get_current_user

logger = logging.getLogger(__name__)

scan_bp = Blueprint('scan', __name__)

# Initialize services with context
scan_service = ScanService("Route: scan_routes global")
audit_service = AuditService("Route: scan_routes global")


@scan_bp.route('/api/scan', methods=['POST'])
@require_auth
@auto_rate_limit
def scan_barcode():
    """API สำหรับสแกนบาร์โค้ด"""
    try:
        logger.info("🔍 เริ่มต้นการสแกนบาร์โค้ด...")
        
        data = request.get_json()
        barcode = data.get('barcode', '').strip()
        job_type_id = data.get('job_type_id')
        sub_job_type_id = data.get('sub_job_type_id')
        note = data.get('note', '').strip()
        
        logger.info(f"📝 ข้อมูลที่ได้รับ: barcode={barcode}, job_type_id={job_type_id}, sub_job_type_id={sub_job_type_id}, note={note}")
        
        # Validate required fields
        if not barcode:
            return jsonify({
                'success': False, 
                'message': 'กรุณากรอกบาร์โค้ด'
            })
        
        if not job_type_id:
            return jsonify({
                'success': False, 
                'message': 'กรุณาเลือก Job Type'
            })
        
        # Get current user from session
        current_user = get_current_user()
        user_id = current_user['username'] if current_user else 'unknown'
        
        # Process scan using ScanService
        result = scan_service.process_scan(
            barcode=barcode,
            job_id=job_type_id,
            sub_job_id=sub_job_type_id,
            notes=note,
            user_id=user_id
        )
        
        if result['success']:
            logger.info(f"✅ สแกนสำเร็จ: {barcode}")
        else:
            logger.warning(f"❌ สแกนล้มเหลว: {result['message']}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ เกิดข้อผิดพลาดในการสแกน: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'ไม่สามารถบันทึกการสแกน: {str(e)}'
        })


@scan_bp.route('/api/history')
@require_auth
@auto_rate_limit
def get_scan_history():
    """API สำหรับดึงประวัติการสแกน"""
    try:
        logger.info("📊 [API: /api/scan_history] ผู้ใช้ดึงประวัติการสแกน")
        
        # Get query parameters
        limit = int(request.args.get('limit', 50))
        date_filter = request.args.get('date')
        job_id = request.args.get('job_id')
        sub_job_id = request.args.get('sub_job_id')
        barcode_filter = request.args.get('barcode')
        notes_filter = request.args.get('notes_filter')
        today_only = request.args.get('today_only', 'true').lower() == 'true'  # Default to true
        
        # Convert IDs to int if provided
        if job_id:
            try:
                job_id = int(job_id)
            except ValueError:
                job_id = None
        
        if sub_job_id:
            try:
                sub_job_id = int(sub_job_id)
            except ValueError:
                sub_job_id = None
        
        # Get database manager with context
        from web.database_service import get_db_manager
        db_manager = get_db_manager("API: /api/scan_history")
        
        # Get history using ScanService
        history = scan_service.get_scan_history(
            limit=limit,
            date_filter=date_filter,
            job_id=job_id,
            sub_job_id=sub_job_id,
            barcode_filter=barcode_filter,
            notes_filter=notes_filter,
            today_only=today_only
        )
        
        # Convert datetime objects to strings for JSON serialization
        for record in history:
            if hasattr(record['scan_date'], 'isoformat'):
                record['scan_date'] = record['scan_date'].isoformat()
        
        return jsonify({
            'success': True, 
            'data': history
        })
        
    except Exception as e:
        logger.error(f"Error getting scan history: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        })


@scan_bp.route('/api/today_summary')
@require_auth
@auto_rate_limit
def get_today_summary():
    """API สำหรับดึงสรุปงานที่สแกนวันนี้"""
    try:
        logger.info("📈 [API: /api/today_summary] ผู้ใช้ดึงสรุปงานวันนี้")
        
        job_type_id = request.args.get('job_type_id')
        sub_job_type_id = request.args.get('sub_job_type_id')
        note_filter = request.args.get('note_filter')
        
        if not job_type_id:
            return jsonify({
                'success': True, 
                'data': {
                    'total_count': 0, 
                    'message': 'กรุณาเลือก Job Type'
                }
            })
        
        # Convert to integers
        try:
            job_type_id = int(job_type_id)
            sub_job_type_id = int(sub_job_type_id) if sub_job_type_id else None
        except ValueError:
            return jsonify({
                'success': False, 
                'message': 'ID ไม่ถูกต้อง'
            })
        
        # Get database manager with context
        from web.database_service import get_db_manager
        db_manager = get_db_manager("API: /api/today_summary")
        
        # Get summary using ScanService
        result = scan_service.get_today_summary(
            job_id=job_type_id,
            sub_job_id=sub_job_type_id,
            notes_filter=note_filter
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ เกิดข้อผิดพลาดในการดึงสรุปงานวันนี้: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'เกิดข้อผิดพลาดในการดึงสรุปงานวันนี้: {str(e)}'
        })


@scan_bp.route('/api/scan/<int:record_id>', methods=['PUT'])
@require_auth
@auto_rate_limit
def update_scan_record(record_id):
    """API สำหรับอัปเดตข้อมูลการสแกน"""
    try:
        data = request.get_json()
        notes = data.get('notes', '').strip()
        
        # Get current user from session
        current_user = get_current_user()
        user_id = current_user['username'] if current_user else 'unknown'
        
        result = scan_service.update_scan_record(record_id, notes, user_id=user_id)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error updating scan record: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        })


@scan_bp.route('/api/audit_history')
@require_auth
@auto_rate_limit
def get_audit_history():
    """API สำหรับดึงประวัติการเปลี่ยนแปลงข้อมูลการสแกน"""
    try:
        # Get query parameters
        scan_record_id = request.args.get('scan_record_id')
        limit = int(request.args.get('limit', 50))
        action_type = request.args.get('action_type')
        changed_by = request.args.get('changed_by')
        date_filter = request.args.get('date')
        
        # Convert scan_record_id to int if provided
        if scan_record_id:
            try:
                scan_record_id = int(scan_record_id)
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'scan_record_id ต้องเป็นตัวเลข'
                })
        
        # Get audit history using AuditService
        audit_history = audit_service.get_scan_audit_history(
            scan_record_id=scan_record_id,
            limit=limit,
            action_type=action_type,
            changed_by=changed_by,
            date_filter=date_filter
        )
        
        # Convert datetime objects to strings for JSON serialization
        for record in audit_history:
            if hasattr(record['change_date'], 'isoformat'):
                record['change_date'] = record['change_date'].isoformat()
        
        return jsonify({
            'success': True,
            'data': audit_history
        })
        
    except Exception as e:
        logger.error(f"Error getting audit history: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        })


@scan_bp.route('/api/audit_summary')
@require_auth
@auto_rate_limit
def get_audit_summary():
    """API สำหรับดึงสรุปการเปลี่ยนแปลงของวันนี้"""
    try:
        date_filter = request.args.get('date')  # Optional date filter
        
        # Get summary using AuditService
        result = audit_service.get_scan_changes_summary(date_filter=date_filter)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting audit summary: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาดในการดึงสรุป: {str(e)}'
        })


