#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notification Service
Handles notification data management and retrieval
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import pandas as pd
from database.database_manager import DatabaseManager
import logging


class NotificationService:
    """บริการจัดการข้อมูล notification popup

    เพิ่มรองรับการผูกกับประเภทงาน (job_id) และประเภทงานย่อย (sub_job_id) เพื่อให้แสดงเฉพาะตามบริบท
    """

    def __init__(self, context: str = "Service: NotificationService", db_manager=None):
        if db_manager:
            self.db = db_manager
        else:
            self.db = DatabaseManager.get_instance(None, context)
        # module logger - let the global logging configuration control verbosity
        self.logger = logging.getLogger(__name__)

    def ensure_job_columns(self) -> None:
        """(Disabled) เดิมใช้เพิ่มคอลัมน์ job_id/sub_job_id อัตโนมัติ ตอนนี้ schema ถูกกำหนดในไฟล์ .sql แล้ว"""
        return

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
                    note_fill,
                    is_enabled,
                    job_id,
                    sub_job_id
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
                    'note_fill': result.get('note_fill'),
                    'is_enabled': result['is_enabled'],
                    'job_id': result.get('job_id'),
                    'sub_job_id': result.get('sub_job_id')
                }

            return None

        except Exception as e:
            self.logger.exception(f"Error getting notification for barcode {barcode}: {e}")
            return None

    def get_notification_for_barcode_with_job(self, barcode: str, job_id: Optional[int] = None, sub_job_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """ค้นหา notification โดยพิจารณา job_id / sub_job_id (null = ไม่จำกัด)

        Logic: เลือกแถวที่ barcode ตรง และ (job_id IS NULL OR job_id = ?) และ (sub_job_id IS NULL OR sub_job_id = ?)
        ให้ priority กับแถวที่ match job_id/sub_job_id มากกว่าแถวที่เป็น NULL (ORDER BY)"""
        try:
            if not barcode or not barcode.strip():
                return None
            barcode = barcode.strip()

            # สร้างเงื่อนไขตามค่าที่รับมา: ถ้าไม่ได้ส่ง job_id ให้อนุญาตเฉพาะแถว job_id IS NULL
            conditions = ["barcode = ?", "is_enabled = 1"]
            params: List[Any] = [barcode]

            if job_id is None:
                conditions.append("(job_id IS NULL)")
            else:
                conditions.append("(job_id IS NULL OR job_id = ?)")
                params.append(job_id)

            if sub_job_id is None:
                conditions.append("(sub_job_id IS NULL)")
            else:
                conditions.append("(sub_job_id IS NULL OR sub_job_id = ?)")
                params.append(sub_job_id)

            where_clause = " AND ".join(conditions)

            # ใช้คะแนนจัดลำดับให้แถวที่ match เฉพาะทางขึ้นก่อน
            query = f"""
                SELECT TOP 1 * FROM (
                    SELECT
                        id, barcode, event_type, popup_type, title, message, note_fill, is_enabled, job_id, sub_job_id, created_date,
                        (CASE WHEN (? IS NOT NULL AND job_id = ?) THEN 2 ELSE 0 END +
                         CASE WHEN (? IS NOT NULL AND sub_job_id = ?) THEN 2 ELSE 0 END) AS match_score
                    FROM notification_data
                    WHERE {where_clause}
                ) t
                ORDER BY match_score DESC, created_date DESC
            """

            # เพิ่มพารามิเตอร์สำหรับ match_score (ต้องส่งซ้ำ)
            score_params: List[Any] = [job_id, job_id, sub_job_id, sub_job_id]
            final_params = score_params + params
            results = self.db.execute_query(query, tuple(final_params))
            if results:
                r = results[0]
                return {
                    'id': r['id'],
                    'barcode': r['barcode'],
                    'event_type': r['event_type'],
                    'popup_type': r['popup_type'],
                    'title': r['title'],
                    'message': r['message'],
                    'note_fill': r.get('note_fill'),
                    'is_enabled': r['is_enabled'],
                    'job_id': r.get('job_id'),
                    'sub_job_id': r.get('sub_job_id')
                }
            return None
        except Exception as e:
            self.logger.exception(f"Error getting notification for barcode+job {barcode}: {e}")
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
                    note_fill,
                    is_enabled,
                    job_id,
                    sub_job_id,
                    created_date,
                    created_by
                FROM notification_data
                ORDER BY created_date DESC
            """

            self.logger.debug("[NotificationService] กำลังดึงข้อมูล notification จากฐานข้อมูล...")
            results = self.db.execute_query(query)
            self.logger.debug(f"[NotificationService] ดึงข้อมูลสำเร็จ: พบ {len(results) if results else 0} รายการ")

            notifications = []
            for row in results:
                notifications.append({
                    'id': row['id'],
                    'barcode': row['barcode'],
                    'event_type': row['event_type'],
                    'popup_type': row['popup_type'],
                    'title': row['title'],
                    'message': row['message'],
                    'note_fill': row.get('note_fill'),
                    'is_enabled': row['is_enabled'],
                    'job_id': row.get('job_id'),
                    'sub_job_id': row.get('sub_job_id'),
                    'created_date': row['created_date'],
                    'created_by': row['created_by']
                })

            return notifications

        except Exception as e:
            self.logger.exception(f"[NotificationService] Error getting all notifications: {e}")
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
            self.logger.info(f"[NotificationService] เริ่มนำเข้าไฟล์: {excel_file}")

            # อ่านไฟล์ Excel (ข้อมูลทั้งหมดเป็น text)
            df = pd.read_excel(excel_file, dtype=str, keep_default_na=False)
            self.logger.debug(f"[NotificationService] อ่านไฟล์ Excel สำเร็จ: {len(df)} แถว")

            # ตรวจสอบ columns ที่จำเป็น
            required_columns = ['barcode', 'event_type', 'popup_type', 'title', 'message']
            optional_columns = ['is_enabled', 'job_id', 'sub_job_id', 'note_fill']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                self.logger.warning(f"[NotificationService] ขาด columns: {missing_columns}")
                return {
                    'success': False,
                    'message': f'ไฟล์ Excel ต้องมี columns: {", ".join(missing_columns)}'
                }

            # ลบแถวที่ข้อมูลว่าง
            df = df.dropna(subset=required_columns)
            self.logger.debug(f"[NotificationService] หลังลบแถวว่าง: {len(df)} แถว")

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
            self.logger.debug(f"[NotificationService] กำลังลบข้อมูลเก่าทั้งหมด...")
            truncate_query = "TRUNCATE TABLE notification_data"
            self.db.execute_non_query(truncate_query)
            self.logger.debug(f"[NotificationService] ลบข้อมูลเก่าเสร็จสิ้น")

            # นำเข้าข้อมูลใหม่
            insert_query = """
                INSERT INTO notification_data
                (barcode, event_type, popup_type, title, message, note_fill, is_enabled, job_id, sub_job_id, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            inserted_count = 0
            errors = []

            self.logger.info(f"[NotificationService] กำลังนำเข้าข้อมูล {len(df)} รายการ...")
            for index, row in df.iterrows():
                try:
                    # is_enabled default True if column absent or NaN
                    is_enabled_val = True
                    if 'is_enabled' in df.columns:
                        val = row.get('is_enabled')
                        if isinstance(val, (int, bool)):
                            is_enabled_val = bool(val)
                        elif isinstance(val, str):
                            is_enabled_val = val.strip().lower() in ['1', 'true', 'yes', 't', 'เปิด', 'enable']

                    # job_id/sub_job_id (nullable)
                    job_id_val: Optional[int] = None
                    sub_job_id_val: Optional[int] = None
                    if 'job_id' in df.columns:
                        jv = row.get('job_id')
                        if pd.notna(jv) and str(jv).strip() != '':
                            try:
                                job_id_val = int(jv)
                            except ValueError:
                                raise ValueError(f"job_id ไม่ใช่ตัวเลข: {jv}")
                    if 'sub_job_id' in df.columns:
                        sv = row.get('sub_job_id')
                        if pd.notna(sv) and str(sv).strip() != '':
                            try:
                                sub_job_id_val = int(sv)
                            except ValueError:
                                raise ValueError(f"sub_job_id ไม่ใช่ตัวเลข: {sv}")

                    # note_fill (nullable)
                    note_fill_val: Optional[str] = None
                    if 'note_fill' in df.columns:
                        nf = row.get('note_fill')
                        if pd.notna(nf) and str(nf).strip() != '':
                            note_fill_val = str(nf).strip()

                    self.db.execute_non_query(
                        insert_query,
                        (
                            str(row['barcode']).strip(),
                            row['event_type'].strip().lower(),
                            row['popup_type'].strip().lower(),
                            row['title'].strip(),
                            row['message'].strip(),
                            note_fill_val,
                            1 if is_enabled_val else 0,
                            job_id_val,
                            sub_job_id_val,
                            user_id
                        )
                    )
                    inserted_count += 1
                    if inserted_count % 10 == 0:
                        self.logger.debug(f"[NotificationService] นำเข้าแล้ว {inserted_count} รายการ...")
                except Exception as e:
                    errors.append(f"แถว {index + 2}: {str(e)}")
                    self.logger.error(f"[NotificationService] ข้อผิดพลาดแถว {index + 2}: {e}")

            self.logger.info(f"[NotificationService] นำเข้าเสร็จสิ้น: {inserted_count} รายการ")

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
            self.logger.exception(f"[NotificationService] เกิดข้อผิดพลาดในการนำเข้า: {e}")
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
            self.logger.debug(f"[NotificationService] กำลังลบ notification ID: {notification_id}")
            query = "DELETE FROM notification_data WHERE id = ?"
            self.db.execute_non_query(query, (notification_id,))
            self.logger.info(f"[NotificationService] ลบ notification ID {notification_id} สำเร็จ")

            return {
                'success': True,
                'message': 'ลบรายการสำเร็จ'
            }

        except Exception as e:
            self.logger.exception(f"[NotificationService] เกิดข้อผิดพลาดในการลบ: {e}")
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
            self.logger.debug(f"[NotificationService] กำลังล้างข้อมูล notification ทั้งหมด...")
            query = "TRUNCATE TABLE notification_data"
            self.db.execute_non_query(query)
            self.logger.info(f"[NotificationService] ล้างข้อมูล notification ทั้งหมดสำเร็จ")

            return {
                'success': True,
                'message': 'ล้างข้อมูลทั้งหมดสำเร็จ'
            }

        except Exception as e:
            self.logger.exception(f"[NotificationService] เกิดข้อผิดพลาดในการล้างข้อมูล: {e}")
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

    # ---------------------- Export Function ----------------------
    def export_notifications(self, output_path: str) -> Dict[str, Any]:
        """ส่งออกข้อมูล notification ทั้งหมดเป็นไฟล์ Excel (สำหรับแก้ไขแล้วนำเข้ากลับ)

        Columns: barcode, event_type, popup_type, title, message, note_fill, is_enabled, job_id, sub_job_id
        (ไม่ใส่ created_date เพื่อให้ไฟล์ใช้งานง่ายขึ้น)
        """
        try:
            self.logger.info('[NotificationService] เริ่มส่งออกข้อมูล notification')
            # columns อยู่แล้วใน schema ไม่ต้องตรวจสอบ
            data = self.get_all_notifications()
            if not data:
                return {'success': False, 'message': 'ไม่มีข้อมูลสำหรับส่งออก'}

            export_rows = []
            for r in data:
                export_rows.append({
                    'barcode': r['barcode'],
                    'event_type': r['event_type'],
                    'popup_type': r['popup_type'],
                    'title': r['title'],
                    'message': r['message'],
                    'note_fill': r.get('note_fill'),
                    'is_enabled': r['is_enabled'],
                    'job_id': r.get('job_id'),
                    'sub_job_id': r.get('sub_job_id')
                })
            df = pd.DataFrame(export_rows)
            df.to_excel(output_path, index=False)
            self.logger.info(f'[NotificationService] ส่งออกสำเร็จ -> {output_path}')
            return {'success': True, 'message': 'ส่งออกข้อมูลสำเร็จ', 'file': output_path}
        except Exception as e:
            self.logger.exception(f'[NotificationService] ส่งออกข้อมูลล้มเหลว: {e}')
            return {'success': False, 'message': f'เกิดข้อผิดพลาดในการส่งออก: {e}'}
