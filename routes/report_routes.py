#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Report Routes
Handles report generation and export endpoints
"""

import logging
from flask import Blueprint, request, jsonify
from src.services.report_service import ReportService
from middleware.rate_limiter import auto_rate_limit
from middleware.auth_middleware import require_auth

logger = logging.getLogger(__name__)

report_bp = Blueprint('report', __name__)

# Initialize report service
report_service = ReportService("Route: report_routes global")


@report_bp.route('/api/report', methods=['POST'])
@require_auth
@auto_rate_limit
def generate_report():
    """API สำหรับสร้างรายงาน"""
    try:
        data = request.get_json()
        report_date = data.get('report_date')
        job_type_id = data.get('job_type_id')
        sub_job_type_id = data.get('sub_job_type_id')
        note_filter = data.get('note_filter')
        
        # Validate required fields
        if not report_date:
            return jsonify({
                'success': False, 
                'message': 'กรุณาเลือกวันที่'
            })
        
        if not job_type_id:
            return jsonify({
                'success': False, 
                'message': 'กรุณาเลือกงานหลัก'
            })
        
        # Convert IDs to integers
        try:
            job_type_id = int(job_type_id)
            sub_job_type_id = int(sub_job_type_id) if sub_job_type_id else None
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'ID ไม่ถูกต้อง'
            })
        
        # Generate report using ReportService
        result = report_service.generate_report(
            report_date=report_date,
            job_id=job_type_id,
            sub_job_id=sub_job_type_id,
            note_filter=note_filter
        )
        
        if result['success']:
            # Convert datetime objects to strings for JSON serialization
            for record in result['data']:
                if hasattr(record['scan_date'], 'isoformat'):
                    record['scan_date'] = record['scan_date'].isoformat()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ เกิดข้อผิดพลาดในการสร้างรายงาน: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'เกิดข้อผิดพลาดในการสร้างรายงาน: {str(e)}'
        })


@report_bp.route('/api/report/export', methods=['POST'])
@auto_rate_limit
def export_report():
    """API สำหรับส่งออกรายงาน"""
    try:
        data = request.get_json()
        report_data = data.get('report_data', [])
        summary = data.get('summary', {})
        filename = data.get('filename', 'report.xlsx')
        
        if not report_data and not summary:
            return jsonify({
                'success': False,
                'message': 'ไม่มีข้อมูลสำหรับส่งออก'
            })
        
        # Export using ReportService
        result = report_service.export_to_excel(
            report_data=report_data,
            summary=summary,
            filename=filename
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error exporting report: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาดในการส่งออก: {str(e)}'
        })


@report_bp.route('/api/report/monthly/<int:year>/<int:month>')
@auto_rate_limit
def get_monthly_summary(year, month):
    """API สำหรับดึงสรุปรายเดือน"""
    try:
        # Validate year and month
        if not (1900 <= year <= 2100) or not (1 <= month <= 12):
            return jsonify({
                'success': False,
                'message': 'ปีหรือเดือนไม่ถูกต้อง'
            })
        
        result = report_service.get_monthly_summary(year, month)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting monthly summary: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        })


@report_bp.route('/api/report/user_activity')
@auto_rate_limit
def get_user_activity_report():
    """API สำหรับดึงรายงานกิจกรรมผู้ใช้"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({
                'success': False,
                'message': 'กรุณาระบุวันที่เริ่มต้นและสิ้นสุด'
            })
        
        result = report_service.get_user_activity_report(start_date, end_date)
        
        # Convert datetime objects to strings for JSON serialization
        if result['success']:
            for activity in result['data']['user_activities']:
                if hasattr(activity['first_scan'], 'isoformat'):
                    activity['first_scan'] = activity['first_scan'].isoformat()
                if hasattr(activity['last_scan'], 'isoformat'):
                    activity['last_scan'] = activity['last_scan'].isoformat()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting user activity report: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        })