#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scan Service
Handles scanning business logic and data processing
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, date
from ..database.database_manager import DatabaseManager
from .job_service import JobService


class ScanService:
    """บริการจัดการการสแกน"""
    
    def __init__(self):
        self.db = DatabaseManager.get_instance()
        self.job_service = JobService()
    
    def process_scan(self, barcode: str, job_id: int, sub_job_id: Optional[int] = None, 
                    notes: str = None, user_id: str = None) -> Dict[str, Any]:
        """ประมวลผลการสแกนบาร์โค้ด"""
        try:
            # Validate inputs
            if not barcode or not barcode.strip():
                return {'success': False, 'message': 'บาร์โค้ดไม่สามารถเป็นค่าว่างได้'}
            
            if not job_id:
                return {'success': False, 'message': 'กรุณาเลือกประเภทงาน'}
            
            barcode = barcode.strip()
            
            # Check job dependencies
            dep_result = self.job_service.check_job_dependencies(barcode, job_id)
            if not dep_result['success']:
                return dep_result
            
            # Check for duplicates
            dup_result = self.check_duplicate_scan(barcode, job_id, sub_job_id)
            if not dup_result['success']:
                return dup_result
            
            # Get job type name
            job_type_name = self.get_job_type_name(job_id)
            if not job_type_name:
                return {'success': False, 'message': 'ไม่พบข้อมูลประเภทงาน'}
            
            # Save scan record
            save_result = self.save_scan_record(barcode, job_id, sub_job_id, job_type_name, notes, user_id)
            
            return save_result
            
        except Exception as e:
            return {'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}
    
    def check_duplicate_scan(self, barcode: str, job_id: int, sub_job_id: Optional[int] = None) -> Dict[str, Any]:
        """ตรวจสอบการสแกนซ้ำ"""
        try:
            if sub_job_id:
                # Check for specific sub job type
                query = """
                    SELECT sl.*, jt.job_name, sjt.sub_job_name
                    FROM scan_logs sl
                    LEFT JOIN job_types jt ON sl.job_id = jt.id
                    LEFT JOIN sub_job_types sjt ON sl.sub_job_id = sjt.id
                    WHERE sl.barcode = ? AND sl.job_id = ? AND sl.sub_job_id = ?
                    ORDER BY sl.scan_date DESC
                """
                results = self.db.execute_query(query, (barcode, job_id, sub_job_id))
            else:
                # Check for main job only (no sub job)
                query = """
                    SELECT sl.*, jt.job_name, sjt.sub_job_name
                    FROM scan_logs sl
                    LEFT JOIN job_types jt ON sl.job_id = jt.id
                    LEFT JOIN sub_job_types sjt ON sl.sub_job_id = sjt.id
                    WHERE sl.barcode = ? AND sl.job_id = ? AND sl.sub_job_id IS NULL
                    ORDER BY sl.scan_date DESC
                """
                results = self.db.execute_query(query, (barcode, job_id))
            
            if results:
                existing_record = results[0]
                job_display = existing_record['job_name'] or existing_record.get('job_type', '')
                sub_job_display = existing_record.get('sub_job_name') or 'ไม่มี'
                
                return {
                    'success': False,
                    'message': f'บาร์โค้ด {barcode} ถูกสแกนในงาน "{job_display} > {sub_job_display}" แล้ว',
                    'duplicate': True,
                    'existing_record': {
                        'scan_date': existing_record['scan_date'].isoformat(),
                        'job_type_name': job_display,
                        'sub_job_type_name': sub_job_display,
                        'user_id': existing_record['user_id']
                    }
                }
            
            return {'success': True, 'message': 'ไม่พบการสแกนซ้ำ'}
            
        except Exception as e:
            return {'success': False, 'message': f'เกิดข้อผิดพลาดในการตรวจสอบการสแกนซ้ำ: {str(e)}'}
    
    def save_scan_record(self, barcode: str, job_id: int, sub_job_id: Optional[int], 
                        job_type_name: str, notes: str = None, user_id: str = None) -> Dict[str, Any]:
        """บันทึกข้อมูลการสแกน"""
        try:
            # Get current user if not provided
            if not user_id:
                user_id = self.db.current_user or 'system'
            
            # Clean notes
            clean_notes = notes.strip() if notes else None
            
            # Insert record
            query = """
                INSERT INTO scan_logs (barcode, scan_date, job_type, user_id, job_id, sub_job_id, notes)
                VALUES (?, GETDATE(), ?, ?, ?, ?, ?)
            """
            
            rows_affected = self.db.execute_non_query(query, (
                barcode, job_type_name, user_id, job_id, sub_job_id, clean_notes
            ))
            
            if rows_affected > 0:
                return {
                    'success': True,
                    'message': f'บันทึกการสแกนบาร์โค้ด {barcode} สำเร็จ'
                }
            else:
                return {
                    'success': False,
                    'message': 'ไม่สามารถบันทึกข้อมูลได้'
                }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'เกิดข้อผิดพลาดในการบันทึก: {str(e)}'
            }
    
    def get_job_type_name(self, job_id: int) -> Optional[str]:
        """ดึงชื่อประเภทงานจาก ID"""
        try:
            query = "SELECT job_name FROM job_types WHERE id = ?"
            results = self.db.execute_query(query, (job_id,))
            
            if results:
                return results[0]['job_name']
            
            return None
            
        except Exception as e:
            print(f"Error getting job type name: {str(e)}")
            return None
    
    def get_scan_history(self, limit: int = 50, date_filter: str = None, 
                        job_id: int = None, sub_job_id: int = None, 
                        barcode_filter: str = None, notes_filter: str = None,
                        today_only: bool = True) -> List[Dict[str, Any]]:
        """ดึงประวัติการสแกน"""
        try:
            query = """
                SELECT TOP (?) 
                    sl.id,
                    sl.barcode,
                    sl.scan_date,
                    jt.job_name as job_type_name,
                    ISNULL(sjt.sub_job_name, 'ไม่มี') as sub_job_type_name,
                    sl.notes,
                    sl.user_id,
                    CASE 
                        WHEN sl.scan_date >= DATEADD(MINUTE, -5, GETDATE()) THEN 'ใหม่'
                        ELSE 'ปกติ'
                    END as status
                FROM scan_logs sl
                LEFT JOIN job_types jt ON sl.job_id = jt.id
                LEFT JOIN sub_job_types sjt ON sl.sub_job_id = sjt.id
                WHERE 1=1
            """
            
            params = [limit]
            
            # Add today filter if enabled (default behavior)
            if today_only:
                query += " AND CAST(sl.scan_date AS DATE) = CAST(GETDATE() AS DATE)"
            
            # Add specific date filter (overrides today_only if provided)
            if date_filter:
                query += " AND CAST(sl.scan_date AS DATE) = ?"
                params.append(date_filter)
            
            # Add job filter
            if job_id:
                query += " AND sl.job_id = ?"
                params.append(job_id)
            
            # Add sub job filter
            if sub_job_id:
                query += " AND sl.sub_job_id = ?"
                params.append(sub_job_id)
            
            # Add barcode filter
            if barcode_filter:
                query += " AND sl.barcode LIKE ?"
                params.append(f"%{barcode_filter}%")
            
            # Add notes filter
            if notes_filter:
                query += " AND sl.notes LIKE ?"
                params.append(f"%{notes_filter}%")
            
            query += " ORDER BY sl.scan_date DESC"
            
            results = self.db.execute_query(query, tuple(params))
            
            history = []
            for row in results:
                history.append({
                    'id': row['id'],
                    'barcode': row['barcode'],
                    'scan_date': row['scan_date'],
                    'job_type_name': row['job_type_name'],
                    'sub_job_type_name': row['sub_job_type_name'],
                    'notes': row['notes'] or '',
                    'user_id': row['user_id'],
                    'status': row['status']
                })
            
            return history
            
        except Exception as e:
            print(f"Error getting scan history: {str(e)}")
            return []
    
    def get_today_summary(self, job_id: int, sub_job_id: Optional[int] = None, 
                         notes_filter: str = None) -> Dict[str, Any]:
        """ดึงสรุปการสแกนวันนี้"""
        try:
            # Build query
            if sub_job_id:
                query = """
                    SELECT COUNT(*) as total_count
                    FROM scan_logs sl
                    WHERE sl.job_id = ? 
                    AND sl.sub_job_id = ?
                    AND CAST(sl.scan_date AS DATE) = CAST(GETDATE() AS DATE)
                """
                params = [job_id, sub_job_id]
            else:
                query = """
                    SELECT COUNT(*) as total_count
                    FROM scan_logs sl
                    WHERE sl.job_id = ? 
                    AND CAST(sl.scan_date AS DATE) = CAST(GETDATE() AS DATE)
                """
                params = [job_id]
            
            # Add notes filter
            if notes_filter and notes_filter.strip():
                query += " AND sl.notes LIKE ?"
                params.append(f"%{notes_filter.strip()}%")
            
            results = self.db.execute_query(query, tuple(params))
            total_count = results[0]['total_count'] if results else 0
            
            # Get job type info
            job_query = "SELECT job_name FROM job_types WHERE id = ?"
            job_result = self.db.execute_query(job_query, (job_id,))
            job_type_name = job_result[0]['job_name'] if job_result else 'ไม่ทราบ'
            
            sub_job_type_name = 'ไม่มี'
            if sub_job_id:
                sub_job_query = "SELECT sub_job_name FROM sub_job_types WHERE id = ?"
                sub_job_result = self.db.execute_query(sub_job_query, (sub_job_id,))
                if sub_job_result:
                    sub_job_type_name = sub_job_result[0]['sub_job_name']
            
            return {
                'success': True,
                'data': {
                    'total_count': total_count,
                    'job_type_name': job_type_name,
                    'sub_job_type_name': sub_job_type_name,
                    'note_filter': notes_filter.strip() if notes_filter and notes_filter.strip() else None,
                    'date': datetime.now().strftime('%Y-%m-%d')
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'เกิดข้อผิดพลาดในการดึงสรุป: {str(e)}'
            }
    
    def update_scan_record(self, record_id: int, notes: str = None) -> Dict[str, Any]:
        """อัปเดตข้อมูลการสแกน"""
        try:
            clean_notes = notes.strip() if notes else None
            
            query = "UPDATE scan_logs SET notes = ? WHERE id = ?"
            rows_affected = self.db.execute_non_query(query, (clean_notes, record_id))
            
            if rows_affected > 0:
                return {
                    'success': True,
                    'message': 'อัปเดตข้อมูลสำเร็จ'
                }
            else:
                return {
                    'success': False,
                    'message': 'ไม่พบข้อมูลที่ต้องการอัปเดต'
                }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'เกิดข้อผิดพลาดในการอัปเดต: {str(e)}'
            }
    
    def delete_scan_record(self, record_id: int) -> Dict[str, Any]:
        """ลบข้อมูลการสแกน"""
        try:
            query = "DELETE FROM scan_logs WHERE id = ?"
            rows_affected = self.db.execute_non_query(query, (record_id,))
            
            if rows_affected > 0:
                return {
                    'success': True,
                    'message': 'ลบข้อมูลสำเร็จ'
                }
            else:
                return {
                    'success': False,
                    'message': 'ไม่พบข้อมูลที่ต้องการลบ'
                }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'เกิดข้อผิดพลาดในการลบ: {str(e)}'
            }