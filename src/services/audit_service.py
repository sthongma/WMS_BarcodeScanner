#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit Service
จัดการการบันทึกประวัติการเปลี่ยนแปลงข้อมูล (Audit Logs)
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class AuditService:
    """บริการจัดการ Audit Logs สำหรับการติดตามการเปลี่ยนแปลงข้อมูล"""
    
    def __init__(self):
        self.db = DatabaseManager.get_instance()
    
    def log_scan_change(self, scan_record_id: int, action_type: str, 
                       old_values: Dict[str, Any] = None, 
                       new_values: Dict[str, Any] = None,
                       changed_by: str = None, notes: str = None) -> Dict[str, Any]:
        """
        บันทึก audit log สำหรับการเปลี่ยนแปลงข้อมูลการสแกน
        
        Args:
            scan_record_id: ID ของ record ที่ถูกเปลี่ยนแปลง
            action_type: ประเภทการเปลี่ยนแปลง ('UPDATE' หรือ 'DELETE')
            old_values: ข้อมูลเดิม
            new_values: ข้อมูลใหม่ (สำหรับ UPDATE เท่านั้น)
            changed_by: ผู้ที่ทำการเปลี่ยนแปลง
            notes: หมายเหตุเพิ่มเติม
        """
        try:
            # Validate action type
            if action_type not in ['UPDATE', 'DELETE']:
                return {
                    'success': False,
                    'message': f'action_type ต้องเป็น UPDATE หรือ DELETE เท่านั้น'
                }
            
            # Get current user if not provided
            if not changed_by:
                changed_by = self.db.current_user or 'system'
            
            # Convert dictionaries to JSON strings
            old_values_json = json.dumps(old_values, ensure_ascii=False) if old_values else None
            new_values_json = json.dumps(new_values, ensure_ascii=False) if new_values else None
            
            # Insert audit log
            query = """
                INSERT INTO audit_logs (scan_record_id, action_type, old_values, new_values, changed_by, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            rows_affected = self.db.execute_non_query(query, (
                scan_record_id, action_type, old_values_json, new_values_json, changed_by, notes
            ))
            
            if rows_affected > 0:
                logger.info(f"Audit log recorded: {action_type} for scan_record_id {scan_record_id} by {changed_by}")
                return {
                    'success': True,
                    'message': 'บันทึก audit log สำเร็จ'
                }
            else:
                return {
                    'success': False,
                    'message': 'ไม่สามารถบันทึก audit log ได้'
                }
            
        except Exception as e:
            logger.error(f"Error logging audit change: {str(e)}")
            return {
                'success': False,
                'message': f'เกิดข้อผิดพลาดในการบันทึก audit log: {str(e)}'
            }
    
    def get_scan_audit_history(self, scan_record_id: int = None, 
                              limit: int = 50, 
                              action_type: str = None,
                              changed_by: str = None,
                              date_filter: str = None) -> List[Dict[str, Any]]:
        """
        ดึงประวัติการเปลี่ยนแปลงของข้อมูลการสแกน
        
        Args:
            scan_record_id: ID ของ record ที่ต้องการดูประวัติ (None = ทั้งหมด)
            limit: จำกัดจำนวน records ที่ดึง
            action_type: กรองตามประเภทการเปลี่ยนแปลง
            changed_by: กรองตามผู้ที่เปลี่ยนแปลง
            date_filter: กรองตามวันที่ (YYYY-MM-DD)
        """
        try:
            query = """
                SELECT TOP (?)
                    al.id,
                    al.scan_record_id,
                    al.action_type,
                    al.old_values,
                    al.new_values,
                    al.changed_by,
                    al.change_date,
                    al.notes
                FROM audit_logs al
                WHERE 1=1
            """
            
            params = [limit]
            
            # Add filters
            if scan_record_id:
                query += " AND al.scan_record_id = ?"
                params.append(scan_record_id)
            
            if action_type:
                query += " AND al.action_type = ?"
                params.append(action_type)
            
            if changed_by:
                query += " AND al.changed_by = ?"
                params.append(changed_by)
            
            if date_filter:
                query += " AND CAST(al.change_date AS DATE) = ?"
                params.append(date_filter)
            
            query += " ORDER BY al.change_date DESC"
            
            results = self.db.execute_query(query, tuple(params))
            
            audit_history = []
            for row in results:
                # Parse JSON values
                old_values = None
                new_values = None
                
                try:
                    if row['old_values']:
                        old_values = json.loads(row['old_values'])
                except json.JSONDecodeError:
                    old_values = {'error': 'Invalid JSON in old_values'}
                
                try:
                    if row['new_values']:
                        new_values = json.loads(row['new_values'])
                except json.JSONDecodeError:
                    new_values = {'error': 'Invalid JSON in new_values'}
                
                audit_history.append({
                    'id': row['id'],
                    'scan_record_id': row['scan_record_id'],
                    'action_type': row['action_type'],
                    'old_values': old_values,
                    'new_values': new_values,
                    'changed_by': row['changed_by'],
                    'change_date': row['change_date'],
                    'notes': row['notes']
                })
            
            return audit_history
            
        except Exception as e:
            logger.error(f"Error getting audit history: {str(e)}")
            return []
    
    def get_scan_changes_summary(self, date_filter: str = None) -> Dict[str, Any]:
        """
        ดึงสรุปการเปลี่ยนแปลงของวันที่กำหนด
        
        Args:
            date_filter: วันที่ (YYYY-MM-DD) หรือ None สำหรับวันนี้
        """
        try:
            query = """
                SELECT 
                    al.action_type,
                    COUNT(*) as count,
                    COUNT(DISTINCT al.changed_by) as unique_users,
                    COUNT(DISTINCT al.scan_record_id) as unique_records
                FROM audit_logs al
                WHERE 1=1
            """
            
            params = []
            
            if date_filter:
                query += " AND CAST(al.change_date AS DATE) = ?"
                params.append(date_filter)
            else:
                query += " AND CAST(al.change_date AS DATE) = CAST(GETDATE() AS DATE)"
            
            query += " GROUP BY al.action_type"
            
            results = self.db.execute_query(query, tuple(params))
            
            summary = {
                'date': date_filter or datetime.now().strftime('%Y-%m-%d'),
                'total_changes': 0,
                'updates': 0,
                'deletes': 0,
                'unique_users': set(),
                'unique_records': set()
            }
            
            for row in results:
                action_type = row['action_type']
                count = row['count']
                
                summary['total_changes'] += count
                
                if action_type == 'UPDATE':
                    summary['updates'] = count
                elif action_type == 'DELETE':
                    summary['deletes'] = count
            
            # Get total unique users and records for the date
            total_query = """
                SELECT 
                    COUNT(DISTINCT al.changed_by) as total_unique_users,
                    COUNT(DISTINCT al.scan_record_id) as total_unique_records
                FROM audit_logs al
                WHERE 1=1
            """
            
            if date_filter:
                total_query += " AND CAST(al.change_date AS DATE) = ?"
                total_results = self.db.execute_query(total_query, (date_filter,))
            else:
                total_query += " AND CAST(al.change_date AS DATE) = CAST(GETDATE() AS DATE)"
                total_results = self.db.execute_query(total_query, ())
            
            if total_results:
                summary['total_unique_users'] = total_results[0]['total_unique_users']
                summary['total_unique_records'] = total_results[0]['total_unique_records']
            else:
                summary['total_unique_users'] = 0
                summary['total_unique_records'] = 0
            
            # Remove set objects for JSON serialization
            del summary['unique_users']
            del summary['unique_records']
            
            return {
                'success': True,
                'data': summary
            }
            
        except Exception as e:
            logger.error(f"Error getting changes summary: {str(e)}")
            return {
                'success': False,
                'message': f'เกิดข้อผิดพลาดในการดึงสรุป: {str(e)}'
            }