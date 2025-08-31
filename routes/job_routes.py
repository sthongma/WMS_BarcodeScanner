#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Job Routes
Handles job types and sub job types endpoints
"""

import logging
from flask import Blueprint, jsonify
from src.services.job_service import JobService
from middleware.rate_limiter import auto_rate_limit
from middleware.auth_middleware import require_auth

logger = logging.getLogger(__name__)

job_bp = Blueprint('job', __name__)

# Initialize job service
job_service = JobService()


@job_bp.route('/api/job_types')
@require_auth
@auto_rate_limit
def get_job_types():
    """API สำหรับดึงรายการ Job Types"""
    try:
        logger.info("🔍 [API: /api/job_types] ผู้ใช้ดึงรายการ Job Types")
        
        # Get database manager with context
        from web.database_service import get_db_manager
        db_manager = get_db_manager("API: /api/job_types")
        
        # Use JobService to get job types
        job_types = job_service.get_all_job_types()
        
        if not job_types:
            logger.info("⚠️ ไม่พบข้อมูล Job Types จะเพิ่มข้อมูลตัวอย่าง...")
            
            # Ensure tables exist and create sample data
            if job_service.ensure_tables_exist():
                # Try to get job types again
                job_types = job_service.get_all_job_types()
                
                # If still empty, create sample data
                if not job_types:
                    sample_jobs = [
                        '1.Release', '2.Inprocess', '3.Outbound', 
                        '4.Loading', '5.Return', '6.Repack'
                    ]
                    
                    for job_name in sample_jobs:
                        job_service.create_job_type(job_name)
                    
                    # Get job types after creating samples
                    job_types = job_service.get_all_job_types()
        
        logger.info(f"📊 ผลลัพธ์: {len(job_types)} รายการ")
        
        for job in job_types:
            logger.info(f"  - ID: {job['id']}, Name: {job['name']}")
        
        return jsonify({
            'success': True, 
            'data': job_types
        })
        
    except Exception as e:
        logger.error(f"❌ เกิดข้อผิดพลาดใน get_job_types: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        })


@job_bp.route('/api/sub_job_types/<int:job_type_id>')
@require_auth
@auto_rate_limit
def get_sub_job_types(job_type_id):
    """API สำหรับดึงรายการ Sub Job Types"""
    try:
        logger.info(f"🔍 [API: /api/sub_job_types/{job_type_id}] ผู้ใช้ดึง Sub Job Types สำหรับ Job Type ID: {job_type_id}")
        
        # Get database manager with context
        from web.database_service import get_db_manager
        db_manager = get_db_manager(f"API: /api/sub_job_types/{job_type_id}")
        
        # Use JobService to get sub job types
        sub_job_types = job_service.get_sub_job_types(job_type_id)
        
        if not sub_job_types:
            logger.info("⚠️ ไม่พบข้อมูล Sub Job Types จะเพิ่มข้อมูลตัวอย่าง...")
            
            # Sample sub jobs for each job type
            sample_sub_jobs = {
                1: [('รับสินค้าปกติ',), ('รับสินค้าด่วน',)],
                2: [('จัดส่งภายในประเทศ',), ('จัดส่งต่างประเทศ',)],
                3: [('ส่งออกปกติ',), ('ส่งออกด่วน',)],
                4: [('โหลดรถปกติ',), ('โหลดรถด่วน',)],
                5: [('คืนสินค้าปกติ',), ('คืนสินค้าด่วน',)],
                6: [('แพ็คใหม่',), ('แพ็คซ่อม',)]
            }
            
            if job_type_id in sample_sub_jobs:
                for sub_job_name_tuple in sample_sub_jobs[job_type_id]:
                    sub_job_name = sub_job_name_tuple[0]
                    success = job_service.create_sub_job_type(
                        job_type_id, 
                        sub_job_name, 
                        f"ตัวอย่างงานรอง: {sub_job_name}"
                    )
                    if success:
                        logger.info(f"✅ เพิ่ม Sub Job Type: {sub_job_name}")
                    else:
                        logger.warning(f"⚠️ ไม่สามารถเพิ่ม Sub Job Type {sub_job_name}")
                
                # Get sub job types after creating samples
                sub_job_types = job_service.get_sub_job_types(job_type_id)
        
        logger.info(f"📊 ผลลัพธ์: {len(sub_job_types)} รายการ")
        
        for sub_job in sub_job_types:
            logger.info(f"  - ID: {sub_job['id']}, Name: {sub_job['name']}")
        
        return jsonify({
            'success': True, 
            'data': sub_job_types
        })
        
    except Exception as e:
        logger.error(f"❌ เกิดข้อผิดพลาดใน get_sub_job_types: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        })


@job_bp.route('/api/job_types', methods=['POST'])
@require_auth
@auto_rate_limit
def create_job_type():
    """API สำหรับสร้าง Job Type ใหม่"""
    try:
        from flask import request
        
        data = request.get_json()
        job_name = data.get('job_name', '').strip()
        
        if not job_name:
            return jsonify({
                'success': False,
                'message': 'กรุณาระบุชื่องาน'
            })
        
        success = job_service.create_job_type(job_name)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'สร้างงาน "{job_name}" สำเร็จ'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'ไม่สามารถสร้างงานได้'
            })
            
    except Exception as e:
        logger.error(f"Error creating job type: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        })


@job_bp.route('/api/sub_job_types', methods=['POST'])
@require_auth
@auto_rate_limit
def create_sub_job_type():
    """API สำหรับสร้าง Sub Job Type ใหม่"""
    try:
        from flask import request
        
        data = request.get_json()
        main_job_id = data.get('main_job_id')
        sub_job_name = data.get('sub_job_name', '').strip()
        description = data.get('description', '').strip()
        
        if not main_job_id or not sub_job_name:
            return jsonify({
                'success': False,
                'message': 'กรุณาระบุงานหลักและชื่องานรอง'
            })
        
        success = job_service.create_sub_job_type(
            main_job_id, 
            sub_job_name, 
            description if description else None
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'สร้างงานรอง "{sub_job_name}" สำเร็จ'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'ไม่สามารถสร้างงานรองได้'
            })
            
    except Exception as e:
        logger.error(f"Error creating sub job type: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        })