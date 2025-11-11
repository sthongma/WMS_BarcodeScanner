#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sound Service
Handles sound settings and audio configuration business logic
"""

import json
import os
from typing import Dict, Any, Optional, List
from database.database_manager import DatabaseManager
from src.models.data_models import SoundSetting


class SoundService:
    """บริการจัดการเสียงและการตั้งค่าเสียง"""

    def __init__(self, context: str = "Service: SoundService"):
        self.db = DatabaseManager.get_instance(None, context)
        self.config_file = "config/sound_config.json"
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """โหลดการตั้งค่าเสียงจาก config file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return self._get_default_config()
        except Exception as e:
            print(f"Error loading sound config: {str(e)}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """สร้างการตั้งค่าเริ่มต้น"""
        return {
            "global_settings": {
                "enabled": True,
                "default_volume": 0.8,
                "allow_overlap": False
            },
            "default_sounds": {
                "success": {"file": "/static/sounds/success.mp3", "volume": 0.8, "enabled": True},
                "error": {"file": "/static/error_2.mp3", "volume": 0.8, "enabled": True},
                "duplicate": {"file": "/static/sounds/duplicate.mp3", "volume": 0.8, "enabled": True},
                "warning": {"file": "/static/sounds/warning.mp3", "volume": 0.8, "enabled": True}
            }
        }

    def get_sound_for_event(self, job_id: Optional[int], sub_job_id: Optional[int],
                           event_type: str) -> Optional[Dict[str, Any]]:
        """
        ดึงไฟล์เสียงสำหรับ event

        ลำดับการค้นหา (Priority):
        1. Sub job specific sound (ถ้ามี sub_job_id)
        2. Main job specific sound (ถ้ามี job_id)
        3. Default sound จาก database
        4. Default sound จาก config file

        Args:
            job_id: ID ของ job type (None = ใช้ default)
            sub_job_id: ID ของ sub job type (None = ใช้เสียงของ main job)
            event_type: ประเภทของ event (success, error, duplicate, warning)

        Returns:
            Dict containing sound_file, volume, is_enabled, or None
        """
        try:
            # ตรวจสอบว่าเสียงเปิดใช้งานหรือไม่
            if not self.config.get("global_settings", {}).get("enabled", True):
                return None

            # 1. ลองหา Sub job specific sound
            if sub_job_id is not None:
                query = """
                    SELECT sound_file, volume, is_enabled
                    FROM sound_settings
                    WHERE sub_job_id = ? AND event_type = ? AND is_enabled = 1
                """
                result = self.db.execute_query(query, (sub_job_id, event_type))
                if result and len(result) > 0:
                    return {
                        'sound_file': result[0]['sound_file'],
                        'volume': float(result[0]['volume']),
                        'is_enabled': bool(result[0]['is_enabled'])
                    }

            # 2. ลองหา Main job specific sound
            if job_id is not None:
                query = """
                    SELECT sound_file, volume, is_enabled
                    FROM sound_settings
                    WHERE job_id = ? AND sub_job_id IS NULL AND event_type = ? AND is_enabled = 1
                """
                result = self.db.execute_query(query, (job_id, event_type))
                if result and len(result) > 0:
                    return {
                        'sound_file': result[0]['sound_file'],
                        'volume': float(result[0]['volume']),
                        'is_enabled': bool(result[0]['is_enabled'])
                    }

            # 3. ลองหา Default sound จาก database
            query = """
                SELECT sound_file, volume, is_enabled
                FROM sound_settings
                WHERE job_id IS NULL AND sub_job_id IS NULL AND event_type = ? AND is_enabled = 1
            """
            result = self.db.execute_query(query, (event_type,))
            if result and len(result) > 0:
                return {
                    'sound_file': result[0]['sound_file'],
                    'volume': float(result[0]['volume']),
                    'is_enabled': bool(result[0]['is_enabled'])
                }

            # 4. ใช้ Default sound จาก config file
            default_sounds = self.config.get("default_sounds", {})
            if event_type in default_sounds:
                sound_config = default_sounds[event_type]
                if sound_config.get("enabled", True):
                    return {
                        'sound_file': sound_config.get("file", ""),
                        'volume': sound_config.get("volume", 0.8),
                        'is_enabled': True
                    }

            return None

        except Exception as e:
            print(f"Error getting sound for event: {str(e)}")
            return None

    def save_sound_setting(self, job_id: Optional[int], sub_job_id: Optional[int],
                          event_type: str, sound_file: str, volume: float = 1.0,
                          is_enabled: bool = True) -> Dict[str, Any]:
        """
        บันทึกการตั้งค่าเสียง

        Args:
            job_id: ID ของ job type (None = default sound)
            sub_job_id: ID ของ sub job type (None = ใช้เสียงของ main job)
            event_type: ประเภทของ event
            sound_file: path ของไฟล์เสียง
            volume: ระดับเสียง (0.0-1.0)
            is_enabled: เปิด/ปิดการใช้งาน

        Returns:
            Dict with success status and message
        """
        try:
            # Validate event_type
            valid_events = ['success', 'error', 'duplicate', 'warning']
            if event_type not in valid_events:
                return {
                    'success': False,
                    'message': f'ประเภท event ไม่ถูกต้อง (ต้องเป็น: {", ".join(valid_events)})'
                }

            # Validate volume
            if not 0.0 <= volume <= 1.0:
                return {'success': False, 'message': 'ระดับเสียงต้องอยู่ระหว่าง 0.0 - 1.0'}

            # Check if setting already exists
            check_query = """
                SELECT id FROM sound_settings
                WHERE (job_id = ? OR (job_id IS NULL AND ? IS NULL))
                AND (sub_job_id = ? OR (sub_job_id IS NULL AND ? IS NULL))
                AND event_type = ?
            """
            result = self.db.execute_query(check_query,
                                          (job_id, job_id, sub_job_id, sub_job_id, event_type))

            if result and len(result) > 0:
                # Update existing setting
                update_query = """
                    UPDATE sound_settings
                    SET sound_file = ?, volume = ?, is_enabled = ?, modified_date = GETDATE()
                    WHERE id = ?
                """
                self.db.execute_non_query(update_query,
                                         (sound_file, volume, is_enabled, result[0]['id']))
                message = 'อัปเดตการตั้งค่าเสียงเรียบร้อย'
            else:
                # Insert new setting
                insert_query = """
                    INSERT INTO sound_settings
                    (job_id, sub_job_id, event_type, sound_file, volume, is_enabled,
                     created_date, modified_date)
                    VALUES (?, ?, ?, ?, ?, ?, GETDATE(), GETDATE())
                """
                self.db.execute_non_query(insert_query,
                                         (job_id, sub_job_id, event_type, sound_file,
                                          volume, is_enabled))
                message = 'บันทึกการตั้งค่าเสียงเรียบร้อย'

            return {'success': True, 'message': message}

        except Exception as e:
            return {'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}

    def get_all_sound_settings(self) -> List[Dict[str, Any]]:
        """ดึงการตั้งค่าเสียงทั้งหมด"""
        try:
            query = """
                SELECT
                    ss.id,
                    ss.job_id,
                    jt.job_name,
                    ss.sub_job_id,
                    sjt.sub_job_name,
                    ss.event_type,
                    ss.sound_file,
                    ss.is_enabled,
                    ss.volume,
                    ss.created_date,
                    ss.modified_date
                FROM sound_settings ss
                LEFT JOIN job_types jt ON ss.job_id = jt.id
                LEFT JOIN sub_job_types sjt ON ss.sub_job_id = sjt.id
                ORDER BY
                    CASE WHEN ss.job_id IS NULL THEN 0 ELSE 1 END,
                    jt.job_name,
                    CASE WHEN ss.sub_job_id IS NULL THEN 0 ELSE 1 END,
                    sjt.sub_job_name,
                    ss.event_type
            """
            results = self.db.execute_query(query)

            settings = []
            for row in results:
                settings.append({
                    'id': row['id'],
                    'job_id': row['job_id'],
                    'job_name': row['job_name'] if row['job_name'] else 'Default',
                    'sub_job_id': row['sub_job_id'],
                    'sub_job_name': row['sub_job_name'] if row['sub_job_name'] else '-',
                    'event_type': row['event_type'],
                    'sound_file': row['sound_file'],
                    'is_enabled': bool(row['is_enabled']),
                    'volume': float(row['volume']),
                    'created_date': row['created_date'],
                    'modified_date': row['modified_date']
                })

            return settings

        except Exception as e:
            print(f"Error getting all sound settings: {str(e)}")
            return []

    def get_sound_settings_by_job(self, job_id: Optional[int] = None,
                                  sub_job_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """ดึงการตั้งค่าเสียงตาม job_id หรือ sub_job_id"""
        try:
            if sub_job_id is not None:
                query = """
                    SELECT * FROM sound_settings
                    WHERE sub_job_id = ?
                    ORDER BY event_type
                """
                results = self.db.execute_query(query, (sub_job_id,))
            elif job_id is not None:
                query = """
                    SELECT * FROM sound_settings
                    WHERE job_id = ? AND sub_job_id IS NULL
                    ORDER BY event_type
                """
                results = self.db.execute_query(query, (job_id,))
            else:
                query = """
                    SELECT * FROM sound_settings
                    WHERE job_id IS NULL AND sub_job_id IS NULL
                    ORDER BY event_type
                """
                results = self.db.execute_query(query)

            return [dict(row) for row in results]

        except Exception as e:
            print(f"Error getting sound settings by job: {str(e)}")
            return []

    def delete_sound_setting(self, setting_id: int) -> Dict[str, Any]:
        """ลบการตั้งค่าเสียง"""
        try:
            delete_query = "DELETE FROM sound_settings WHERE id = ?"
            self.db.execute_non_query(delete_query, (setting_id,))

            return {'success': True, 'message': 'ลบการตั้งค่าเสียงเรียบร้อย'}

        except Exception as e:
            return {'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}

    def toggle_sound_setting(self, setting_id: int, is_enabled: bool) -> Dict[str, Any]:
        """เปิด/ปิดการใช้งานการตั้งค่าเสียง"""
        try:
            update_query = """
                UPDATE sound_settings
                SET is_enabled = ?, modified_date = GETDATE()
                WHERE id = ?
            """
            self.db.execute_non_query(update_query, (is_enabled, setting_id))

            status = 'เปิด' if is_enabled else 'ปิด'
            return {'success': True, 'message': f'{status}การใช้งานเรียบร้อย'}

        except Exception as e:
            return {'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}

    def get_available_sounds(self) -> List[str]:
        """ดึงรายการไฟล์เสียงที่มีในระบบ"""
        available = self.config.get("available_sounds", {}).get("files", [])

        # เพิ่มไฟล์เสียงจาก static folder
        static_dir = "static/sounds"
        if os.path.exists(static_dir):
            for file in os.listdir(static_dir):
                if file.endswith(('.mp3', '.wav', '.ogg')):
                    file_path = f"/static/sounds/{file}"
                    if file_path not in available:
                        available.append(file_path)

        # เพิ่มไฟล์เสียงจาก static root
        static_root = "static"
        if os.path.exists(static_root):
            for file in os.listdir(static_root):
                if file.endswith(('.mp3', '.wav', '.ogg')):
                    file_path = f"/static/{file}"
                    if file_path not in available:
                        available.append(file_path)

        return sorted(available)

    def is_sound_enabled(self) -> bool:
        """ตรวจสอบว่าเสียงเปิดใช้งานทั่วไปหรือไม่"""
        return self.config.get("global_settings", {}).get("enabled", True)

    def set_global_sound_enabled(self, enabled: bool) -> bool:
        """เปิด/ปิดเสียงทั่วไป"""
        try:
            self.config["global_settings"]["enabled"] = enabled
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error setting global sound enabled: {str(e)}")
            return False
