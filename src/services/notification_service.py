#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notification Service
Handles notification data management and retrieval
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd
from database.database_manager import DatabaseManager


class NotificationService:
    """บริการจัดการข้อมูล notification popup"""

    def __init__(self, context: str = "Service: NotificationService", db_manager=None):
        if db_manager:
            self.db = db_manager
        else:
            self.db = DatabaseManager.get_instance(None, context)

    def get_notification_for_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        ค้นหา notification สำหรับบาร์โค้ดที่ระบุ

        Args:
            barcode: รหัสบาร์โค้ด

        Returns:
            Dict ของ notification หรือ None ถ้าไม่พบ
        """
        try:
            if not barcode or not barcode.strip():
                return None

            barcode = barcode.strip()

            query = """
                SELECT TOP 1
                    id,
                    barcode,
                    event_type,
                    popup_type,
                    title,
                    message,
                    is_enabled
                FROM notification_data
                WHERE barcode = ?
                    AND is_enabled = 1
                ORDER BY created_date DESC
            """

            results = self.db.execute_query(query, (barcode,))

            if results and len(results) > 0:
                result = results[0]
                return {
                    'id': result['id'],
                    'barcode': result['barcode'],
                    'event_type': result['event_type'],
                    'popup_type': result['popup_type'],
                    'title': result['title'],
                    'message': result['message'],
                    'is_enabled': result['is_enabled']
                }

            return None

        except Exception as e:
            print(f"Error getting notification for barcode {barcode}: {e}")
            return None

    def get_all_notifications(self) -> List[Dict[str, Any]]:
        """
        ดึงรายการ notification ทั้งหมด

        Returns:
            List ของ notification dicts
        """
        try:
            query = """
                SELECT
                    id,
                    barcode,
                    event_type,
                    popup_type,
                    title,
                    message,
                    is_enabled,
                    created_date,
                    created_by
                FROM notification_data
                ORDER BY created_date DESC
            """

            print(f"[NotificationService] กำลังดึงข้อมูล notification จากฐานข้อมูล...")
            results = self.db.execute_query(query)
            print(f"[NotificationService] ดึงข้อมูลสำเร็จ: พบ {len(results) if results else 0} รายการ")

            notifications = []
            for row in results:
                notifications.append({
                    'id': row['id'],
                    'barcode': row['barcode'],
                    'event_type': row['event_type'],
                    'popup_type': row['popup_type'],
                    'title': row['title'],
                    'message': row['message'],
                    'is_enabled': row['is_enabled'],
                    'created_date': row['created_date'],
                    'created_by': row['created_by']
                })

            return notifications

        except Exception as e:
            print(f"[NotificationService] Error getting all notifications: {e}")
            import traceback
            traceback.print_exc()
            return []

    def import_notifications(self, excel_file: str, user_id: str) -> Dict[str, Any]:
        """
        นำเข้าข้อมูล notification จาก Excel โดยล้างข้อมูลเก่าทั้งหมดก่อน

        Args:
            excel_file: path ของไฟล์ Excel
            user_id: ผู้ใช้ที่ทำการนำเข้า

        Returns:
            Dict ผลลัพธ์การนำเข้า
        """
        try:
            print(f"[NotificationService] เริ่มนำเข้าไฟล์: {excel_file}")

            # อ่านไฟล์ Excel
            df = pd.read_excel(excel_file)
            print(f"[NotificationService] อ่านไฟล์ Excel สำเร็จ: {len(df)} แถว")

            # ตรวจสอบ columns ที่จำเป็น
            required_columns = ['barcode', 'event_type', 'popup_type', 'title', 'message']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                print(f"[NotificationService] ขาด columns: {missing_columns}")
                return {
                    'success': False,
                    'message': f'ไฟล์ Excel ต้องมี columns: {", ".join(missing_columns)}'
                }

            # ลบแถวที่ข้อมูลว่าง
            df = df.dropna(subset=required_columns)
            print(f"[NotificationService] หลังลบแถวว่าง: {len(df)} แถว")

            if df.empty:
                return {
                    'success': False,
                    'message': 'ไม่พบข้อมูลในไฟล์ Excel'
                }

            # Validate event_type และ popup_type
            valid_event_types = ['success', 'error', 'duplicate', 'warning']
            valid_popup_types = ['modal', 'toast']

            invalid_events = df[~df['event_type'].isin(valid_event_types)]
            if not invalid_events.empty:
                return {
                    'success': False,
                    'message': f'event_type ต้องเป็น: {", ".join(valid_event_types)}'
                }

            invalid_popups = df[~df['popup_type'].isin(valid_popup_types)]
            if not invalid_popups.empty:
                return {
                    'success': False,
                    'message': f'popup_type ต้องเป็น: {", ".join(valid_popup_types)}'
                }

            # ตรวจสอบความยาว title
            long_titles = df[df['title'].str.len() > 255]
            if not long_titles.empty:
                return {
                    'success': False,
                    'message': 'title ต้องไม่เกิน 255 ตัวอักษร'
                }

            # ล้างข้อมูลเก่าทั้งหมด
            print(f"[NotificationService] กำลังลบข้อมูลเก่าทั้งหมด...")
            truncate_query = "TRUNCATE TABLE notification_data"
            self.db.execute_non_query(truncate_query)
            print(f"[NotificationService] ลบข้อมูลเก่าเสร็จสิ้น")

            # นำเข้าข้อมูลใหม่
            insert_query = """
                INSERT INTO notification_data
                (barcode, event_type, popup_type, title, message, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """

            inserted_count = 0
            errors = []

            print(f"[NotificationService] กำลังนำเข้าข้อมูล {len(df)} รายการ...")
            for index, row in df.iterrows():
                try:
                    self.db.execute_non_query(
                        insert_query,
                        (
                            str(row['barcode']).strip(),
                            row['event_type'].strip().lower(),
                            row['popup_type'].strip().lower(),
                            row['title'].strip(),
                            row['message'].strip(),
                            user_id
                        )
                    )
                    inserted_count += 1
                    if inserted_count % 10 == 0:
                        print(f"[NotificationService] นำเข้าแล้ว {inserted_count} รายการ...")
                except Exception as e:
                    errors.append(f"แถว {index + 2}: {str(e)}")
                    print(f"[NotificationService] ข้อผิดพลาดแถว {index + 2}: {e}")

            print(f"[NotificationService] นำเข้าเสร็จสิ้น: {inserted_count} รายการ")

            if errors:
                return {
                    'success': False,
                    'message': f'นำเข้าสำเร็จ {inserted_count} รายการ, มีข้อผิดพลาด {len(errors)} รายการ',
                    'errors': errors
                }

            return {
                'success': True,
                'message': f'นำเข้าข้อมูลสำเร็จ {inserted_count} รายการ (ข้อมูลเก่าถูกลบทั้งหมด)'
            }

        except Exception as e:
            print(f"[NotificationService] เกิดข้อผิดพลาดในการนำเข้า: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f'เกิดข้อผิดพลาดในการนำเข้า: {str(e)}'
            }

    def delete_notification(self, notification_id: int) -> Dict[str, Any]:
        """
        ลบ notification รายการเดียว

        Args:
            notification_id: ID ของ notification

        Returns:
            Dict ผลลัพธ์การลบ
        """
        try:
            print(f"[NotificationService] กำลังลบ notification ID: {notification_id}")
            query = "DELETE FROM notification_data WHERE id = ?"
            self.db.execute_non_query(query, (notification_id,))
            print(f"[NotificationService] ลบ notification ID {notification_id} สำเร็จ")

            return {
                'success': True,
                'message': 'ลบรายการสำเร็จ'
            }

        except Exception as e:
            print(f"[NotificationService] เกิดข้อผิดพลาดในการลบ: {e}")
            return {
                'success': False,
                'message': f'เกิดข้อผิดพลาดในการลบ: {str(e)}'
            }

    def clear_all_notifications(self) -> Dict[str, Any]:
        """
        ล้าง notification ทั้งหมด

        Returns:
            Dict ผลลัพธ์การลบ
        """
        try:
            print(f"[NotificationService] กำลังล้างข้อมูล notification ทั้งหมด...")
            query = "TRUNCATE TABLE notification_data"
            self.db.execute_non_query(query)
            print(f"[NotificationService] ล้างข้อมูล notification ทั้งหมดสำเร็จ")

            return {
                'success': True,
                'message': 'ล้างข้อมูลทั้งหมดสำเร็จ'
            }

        except Exception as e:
            print(f"[NotificationService] เกิดข้อผิดพลาดในการล้างข้อมูล: {e}")
            return {
                'success': False,
                'message': f'เกิดข้อผิดพลาดในการล้างข้อมูล: {str(e)}'
            }

    def toggle_notification(self, notification_id: int, is_enabled: bool) -> Dict[str, Any]:
        """
        เปิด/ปิด notification

        Args:
            notification_id: ID ของ notification
            is_enabled: True = เปิดใช้งาน, False = ปิดใช้งาน

        Returns:
            Dict ผลลัพธ์
        """
        try:
            query = "UPDATE notification_data SET is_enabled = ? WHERE id = ?"
            self.db.execute_non_query(query, (is_enabled, notification_id))

            status = "เปิดใช้งาน" if is_enabled else "ปิดใช้งาน"
            return {
                'success': True,
                'message': f'{status}รายการสำเร็จ'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'เกิดข้อผิดพลาด: {str(e)}'
            }
