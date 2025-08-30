#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scan Routes
Handles scanning and history endpoints
"""

import logging
from flask import Blueprint, request, jsonify
from src.services.scan_service import ScanService
from middleware.rate_limiter import auto_rate_limit

logger = logging.getLogger(__name__)

scan_bp = Blueprint('scan', __name__)

# Initialize scan service
scan_service = ScanService()


@scan_bp.route('/api/scan', methods=['POST'])
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
        
        # Process scan using ScanService
        result = scan_service.process_scan(
            barcode=barcode,
            job_id=job_type_id,
            sub_job_id=sub_job_type_id,
            notes=note
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
@auto_rate_limit
def get_scan_history():
    """API สำหรับดึงประวัติการสแกน"""
    try:
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
@auto_rate_limit
def get_today_summary():
    """API สำหรับดึงสรุปงานที่สแกนวันนี้"""
    try:
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
@auto_rate_limit
def update_scan_record(record_id):
    """API สำหรับอัปเดตข้อมูลการสแกน"""
    try:
        data = request.get_json()
        notes = data.get('notes', '').strip()
        
        result = scan_service.update_scan_record(record_id, notes)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error updating scan record: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        })


