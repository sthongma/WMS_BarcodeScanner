#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sound Routes
Handles sound settings endpoints
"""

import logging
from flask import Blueprint, jsonify, request
from src.services.sound_service import SoundService
from middleware.rate_limiter import auto_rate_limit
from middleware.auth_middleware import require_auth

logger = logging.getLogger(__name__)

sound_bp = Blueprint('sound', __name__)

# Initialize sound service
sound_service = SoundService("Route: sound_routes global")


@sound_bp.route('/api/sound_settings', methods=['GET'])
@require_auth
@auto_rate_limit
def get_sound_settings():
    """API สำหรับดึงการตั้งค่าเสียงทั้งหมด"""
    try:
        logger.info("🔍 [API: GET /api/sound_settings] ผู้ใช้ดึงการตั้งค่าเสียง")

        # Get database manager with context
        from web.database_service import get_db_manager
        db_manager = get_db_manager("API: GET /api/sound_settings")

        # Use SoundService to get all sound settings
        settings = sound_service.get_all_sound_settings()

        logger.info(f"📊 ผลลัพธ์: {len(settings)} รายการ")

        return jsonify({
            'success': True,
            'data': settings
        })

    except Exception as e:
        logger.error(f"❌ เกิดข้อผิดพลาดใน get_sound_settings: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        }), 500


@sound_bp.route('/api/sound_settings', methods=['POST'])
@require_auth
@auto_rate_limit
def save_sound_setting():
    """API สำหรับบันทึกการตั้งค่าเสียง"""
    try:
        data = request.get_json()
        logger.info(f"💾 [API: POST /api/sound_settings] บันทึกการตั้งค่าเสียง: {data}")

        # Validate required fields
        if not data or 'event_type' not in data or 'sound_file' not in data:
            return jsonify({
                'success': False,
                'message': 'ข้อมูลไม่ครบถ้วน (ต้องมี event_type และ sound_file)'
            }), 400

        # Get database manager with context
        from web.database_service import get_db_manager
        db_manager = get_db_manager("API: POST /api/sound_settings")

        # Save sound setting
        result = sound_service.save_sound_setting(
            job_id=data.get('job_id'),
            sub_job_id=data.get('sub_job_id'),
            event_type=data['event_type'],
            sound_file=data['sound_file'],
            volume=data.get('volume', 1.0),
            is_enabled=data.get('is_enabled', True)
        )

        if result['success']:
            logger.info(f"✅ บันทึกสำเร็จ: {result['message']}")
        else:
            logger.warning(f"⚠️ บันทึกไม่สำเร็จ: {result['message']}")

        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ เกิดข้อผิดพลาดใน save_sound_setting: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        }), 500


@sound_bp.route('/api/sound_settings/<int:setting_id>', methods=['DELETE'])
@require_auth
@auto_rate_limit
def delete_sound_setting(setting_id):
    """API สำหรับลบการตั้งค่าเสียง"""
    try:
        logger.info(f"🗑️ [API: DELETE /api/sound_settings/{setting_id}] ลบการตั้งค่าเสียง ID: {setting_id}")

        # Get database manager with context
        from web.database_service import get_db_manager
        db_manager = get_db_manager(f"API: DELETE /api/sound_settings/{setting_id}")

        # Delete sound setting
        result = sound_service.delete_sound_setting(setting_id)

        if result['success']:
            logger.info(f"✅ ลบสำเร็จ: {result['message']}")
        else:
            logger.warning(f"⚠️ ลบไม่สำเร็จ: {result['message']}")

        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ เกิดข้อผิดพลาดใน delete_sound_setting: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        }), 500


@sound_bp.route('/api/sound_settings/<int:setting_id>/toggle', methods=['PUT'])
@require_auth
@auto_rate_limit
def toggle_sound_setting(setting_id):
    """API สำหรับเปิด/ปิดการตั้งค่าเสียง"""
    try:
        data = request.get_json()
        logger.info(f"🔄 [API: PUT /api/sound_settings/{setting_id}/toggle] เปลี่ยนสถานะ: {data}")

        # Validate required fields
        if not data or 'is_enabled' not in data:
            return jsonify({
                'success': False,
                'message': 'ข้อมูลไม่ครบถ้วน (ต้องมี is_enabled)'
            }), 400

        # Get database manager with context
        from web.database_service import get_db_manager
        db_manager = get_db_manager(f"API: PUT /api/sound_settings/{setting_id}/toggle")

        # Toggle sound setting
        result = sound_service.toggle_sound_setting(setting_id, data['is_enabled'])

        if result['success']:
            logger.info(f"✅ เปลี่ยนสถานะสำเร็จ: {result['message']}")
        else:
            logger.warning(f"⚠️ เปลี่ยนสถานะไม่สำเร็จ: {result['message']}")

        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ เกิดข้อผิดพลาดใน toggle_sound_setting: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        }), 500


@sound_bp.route('/api/sound_settings/available_sounds', methods=['GET'])
@require_auth
@auto_rate_limit
def get_available_sounds():
    """API สำหรับดึงรายการไฟล์เสียงที่มีในระบบ"""
    try:
        logger.info("🔍 [API: GET /api/sound_settings/available_sounds] ดึงรายการไฟล์เสียง")

        # Get available sounds
        sounds = sound_service.get_available_sounds()

        logger.info(f"📊 พบไฟล์เสียง: {len(sounds)} ไฟล์")

        return jsonify({
            'success': True,
            'data': sounds
        })

    except Exception as e:
        logger.error(f"❌ เกิดข้อผิดพลาดใน get_available_sounds: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        }), 500


@sound_bp.route('/api/sound_settings/by_job', methods=['GET'])
@require_auth
@auto_rate_limit
def get_sound_settings_by_job():
    """API สำหรับดึงการตั้งค่าเสียงตาม job_id หรือ sub_job_id"""
    try:
        job_id = request.args.get('job_id', type=int)
        sub_job_id = request.args.get('sub_job_id', type=int)

        logger.info(f"🔍 [API: GET /api/sound_settings/by_job] job_id={job_id}, sub_job_id={sub_job_id}")

        # Get database manager with context
        from web.database_service import get_db_manager
        db_manager = get_db_manager("API: GET /api/sound_settings/by_job")

        # Get sound settings by job
        settings = sound_service.get_sound_settings_by_job(job_id, sub_job_id)

        logger.info(f"📊 พบการตั้งค่า: {len(settings)} รายการ")

        return jsonify({
            'success': True,
            'data': settings
        })

    except Exception as e:
        logger.error(f"❌ เกิดข้อผิดพลาดใน get_sound_settings_by_job: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        }), 500
