#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notification Routes
Handles notification data endpoints
"""

import logging
import os
import tempfile
from flask import Blueprint, jsonify, request, send_file
from src.services.notification_service import NotificationService
from middleware.rate_limiter import auto_rate_limit
from middleware.auth_middleware import require_auth

logger = logging.getLogger(__name__)

notification_bp = Blueprint('notification', __name__)

# Initialize notification service
notification_service = NotificationService("Route: notification_routes global")


@notification_bp.route('/api/notifications', methods=['GET'])
@require_auth
@auto_rate_limit
def get_notifications():
    """API สำหรับดึงรายการ notification ทั้งหมด"""
    try:
        logger.info("🔍 [API: GET /api/notifications] ผู้ใช้ดึงรายการ notification")

        # Get database manager with context
        from web.database_service import get_db_manager
        db_manager = get_db_manager("API: GET /api/notifications")

        # Get all notifications
        notifications = notification_service.get_all_notifications()

        logger.info(f"📊 ผลลัพธ์: {len(notifications)} รายการ")

        return jsonify({
            'success': True,
            'data': notifications
        })

    except Exception as e:
        logger.error(f"❌ เกิดข้อผิดพลาดใน get_notifications: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        }), 500


@notification_bp.route('/api/notifications/export', methods=['GET'])
@require_auth
@auto_rate_limit
def export_notifications():
    """API ส่งออกข้อมูล notification เป็นไฟล์ Excel"""
    try:
        logger.info('📤 [API: GET /api/notifications/export] ส่งออกข้อมูล notification')
        # สร้างไฟล์ชั่วคราว
        tmp_dir = tempfile.gettempdir()
        file_path = os.path.join(tmp_dir, 'notification_export.xlsx')
        result = notification_service.export_notifications(file_path)
        if not result['success']:
            return jsonify(result), 400
        return send_file(file_path, as_attachment=True, download_name='notification_export.xlsx')
    except Exception as e:
        logger.exception(f'❌ เกิดข้อผิดพลาดใน export_notifications: {e}')
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {e}'}), 500


@notification_bp.route('/api/notifications/import', methods=['POST'])
@require_auth
@auto_rate_limit
def import_notifications():
    """API นำเข้าข้อมูล notification จากไฟล์ Excel ที่ส่งออก"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'ไม่พบไฟล์ในคำขอ (form field "file")'}), 400
        upload = request.files['file']
        if upload.filename == '':
            return jsonify({'success': False, 'message': 'ไฟล์ว่าง'}), 400

        # หา user_id จาก context (พยายามเดา) หรือใช้ค่าที่ส่งมา
        user_id = request.form.get('user_id') or request.args.get('user_id') or 'system'

        tmp_dir = tempfile.gettempdir()
        temp_path = os.path.join(tmp_dir, f'notification_import_{next(tempfile._get_candidate_names())}.xlsx')
        upload.save(temp_path)
        logger.info(f'📥 [API: POST /api/notifications/import] รับไฟล์ {upload.filename} -> {temp_path}')

        result = notification_service.import_notifications(temp_path, user_id)
        # ลบไฟล์ชั่วคราว
        try:
            os.remove(temp_path)
        except OSError:
            pass
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
    except Exception as e:
        logger.exception(f'❌ เกิดข้อผิดพลาดใน import_notifications: {e}')
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {e}'}), 500


@notification_bp.route('/api/notifications/<int:notification_id>', methods=['DELETE'])
@require_auth
@auto_rate_limit
def delete_notification(notification_id):
    """API สำหรับลบ notification รายการเดียว"""
    try:
        logger.info(f"🗑️ [API: DELETE /api/notifications/{notification_id}] ลบ notification")

        # Get database manager with context
        from web.database_service import get_db_manager
        db_manager = get_db_manager(f"API: DELETE /api/notifications/{notification_id}")

        # Delete notification
        result = notification_service.delete_notification(notification_id)

        if result['success']:
            logger.info(f"✅ ลบ notification ID {notification_id} สำเร็จ")
        else:
            logger.warning(f"⚠️ ลบ notification ID {notification_id} ไม่สำเร็จ: {result['message']}")

        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ เกิดข้อผิดพลาดใน delete_notification: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        }), 500


@notification_bp.route('/api/notifications/clear', methods=['POST'])
@require_auth
@auto_rate_limit
def clear_all_notifications():
    """API สำหรับล้าง notification ทั้งหมด"""
    try:
        logger.info("🗑️ [API: POST /api/notifications/clear] ล้าง notification ทั้งหมด")

        # Get database manager with context
        from web.database_service import get_db_manager
        db_manager = get_db_manager("API: POST /api/notifications/clear")

        # Clear all notifications
        result = notification_service.clear_all_notifications()

        if result['success']:
            logger.info("✅ ล้าง notification ทั้งหมดสำเร็จ")
        else:
            logger.warning(f"⚠️ ล้าง notification ไม่สำเร็จ: {result['message']}")

        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ เกิดข้อผิดพลาดใน clear_all_notifications: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        }), 500


@notification_bp.route('/api/notifications/<int:notification_id>/toggle', methods=['POST'])
@require_auth
@auto_rate_limit
def toggle_notification(notification_id):
    """API สำหรับเปิด/ปิด notification"""
    try:
        data = request.get_json()
        is_enabled = data.get('is_enabled', True)

        logger.info(f"🔄 [API: POST /api/notifications/{notification_id}/toggle] เปลี่ยนสถานะเป็น {is_enabled}")

        # Get database manager with context
        from web.database_service import get_db_manager
        db_manager = get_db_manager(f"API: POST /api/notifications/{notification_id}/toggle")

        # Toggle notification
        result = notification_service.toggle_notification(notification_id, is_enabled)

        if result['success']:
            logger.info(f"✅ เปลี่ยนสถานะ notification ID {notification_id} สำเร็จ")
        else:
            logger.warning(f"⚠️ เปลี่ยนสถานะ notification ID {notification_id} ไม่สำเร็จ: {result['message']}")

        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ เกิดข้อผิดพลาดใน toggle_notification: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        }), 500
