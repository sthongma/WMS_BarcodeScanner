#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Log Manager Utility
จัดการไฟล์ log โดยแยกตามวันที่และลบไฟล์เก่า
"""

import os
import shutil
import logging
from datetime import datetime, timedelta
from typing import Optional
import threading
import time


class LogManager:
    """จัดการไฟล์ log ด้วยการหมุนเวียนแบบรายวันและการลบไฟล์เก่า"""
    
    def __init__(self, log_dir: str = "logs", retention_days: int = 30):
        self.log_dir = log_dir
        self.retention_days = retention_days
        self.current_date = None
        self.current_log_file = None
        self._lock = threading.Lock()
        
        # สร้างโฟลเดอร์ logs ถ้ายังไม่มี
        os.makedirs(self.log_dir, exist_ok=True)
        
        # เริ่มต้นการหมุนเวียน log
        self._rotate_if_needed()
        
        # เริ่มต้น cleanup thread
        self._start_cleanup_thread()
    
    def get_current_log_file(self) -> str:
        """ดึงชื่อไฟล์ log ปัจจุบัน"""
        with self._lock:
            self._rotate_if_needed()
            return self.current_log_file
    
    def _rotate_if_needed(self):
        """หมุนเวียนไฟล์ log หากเปลี่ยนวันที่"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        if self.current_date != today:
            self.current_date = today
            self.current_log_file = os.path.join(self.log_dir, f"web_app_{today}.log")
            
            # ย้าย log ปัจจุบันไปเป็นไฟล์ของเมื่อวาน (หากมี)
            self._move_current_log_to_dated()
    
    def _move_current_log_to_dated(self):
        """ย้าย web_app.log ปัจจุบันไปเป็นไฟล์ที่มีวันที่"""
        current_log = os.path.join(self.log_dir, "web_app.log")
        
        if os.path.exists(current_log) and os.path.getsize(current_log) > 0:
            try:
                # หาวันที่ของไฟล์ปัจจุบัน
                file_time = datetime.fromtimestamp(os.path.getmtime(current_log))
                dated_filename = f"web_app_{file_time.strftime('%Y-%m-%d')}.log"
                dated_path = os.path.join(self.log_dir, dated_filename)
                
                # ถ้ามีไฟล์วันที่นั้นอยู่แล้ว ให้ append เข้าไป
                if os.path.exists(dated_path):
                    with open(current_log, 'r', encoding='utf-8') as src:
                        with open(dated_path, 'a', encoding='utf-8') as dst:
                            dst.write('\n')  # เพิ่มบรรทัดว่างคั่น
                            dst.write(src.read())
                    os.remove(current_log)
                else:
                    # ย้ายไฟล์
                    shutil.move(current_log, dated_path)
                
                print(f"Log rotated: {current_log} -> {dated_path}")
                
            except Exception as e:
                print(f"Error rotating log file: {e}")
    
    def cleanup_old_logs(self):
        """ลบไฟล์ log ที่เก่ากว่า retention_days วัน"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            deleted_files = []
            
            for filename in os.listdir(self.log_dir):
                if filename.startswith("web_app_") and filename.endswith(".log"):
                    file_path = os.path.join(self.log_dir, filename)
                    
                    # ดึงวันที่จากชื่อไฟล์
                    try:
                        date_part = filename.replace("web_app_", "").replace(".log", "")
                        file_date = datetime.strptime(date_part, "%Y-%m-%d")
                        
                        if file_date < cutoff_date:
                            os.remove(file_path)
                            deleted_files.append(filename)
                            
                    except ValueError:
                        # ถ้าชื่อไฟล์ไม่ตรงรูปแบบ ให้ดูจากวันที่แก้ไขไฟล์
                        if os.path.getmtime(file_path) < cutoff_date.timestamp():
                            os.remove(file_path)
                            deleted_files.append(filename)
            
            if deleted_files:
                print(f"Cleaned up {len(deleted_files)} old log files: {deleted_files}")
            
        except Exception as e:
            print(f"Error during log cleanup: {e}")
    
    def _start_cleanup_thread(self):
        """เริ่มต้น thread สำหรับการลบไฟล์ log เก่าแบบอัตโนมัติ"""
        def cleanup_worker():
            while True:
                try:
                    # รอ 24 ชั่วโมง (86400 วินาที)
                    time.sleep(86400)
                    self.cleanup_old_logs()
                except Exception as e:
                    print(f"Error in cleanup thread: {e}")
                    time.sleep(3600)  # รอ 1 ชั่วโมงแล้วลองใหม่
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        print(f"Log cleanup thread started (retention: {self.retention_days} days)")
    
    def get_log_files_info(self) -> list:
        """ดึงข้อมูลไฟล์ log ทั้งหมด"""
        log_files = []
        
        try:
            for filename in os.listdir(self.log_dir):
                if filename.endswith(".log"):
                    file_path = os.path.join(self.log_dir, filename)
                    file_stat = os.stat(file_path)
                    
                    log_files.append({
                        'filename': filename,
                        'size': file_stat.st_size,
                        'size_mb': round(file_stat.st_size / (1024 * 1024), 2),
                        'modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                        'path': file_path
                    })
            
            # เรียงตามวันที่แก้ไขล่าสุด
            log_files.sort(key=lambda x: x['modified'], reverse=True)
            
        except Exception as e:
            print(f"Error getting log files info: {e}")
        
        return log_files


# Global log manager instance
log_manager = LogManager()


class DailyRotatingFileHandler(logging.FileHandler):
    """Custom file handler ที่หมุนเวียนไฟล์ log รายวัน"""
    
    def __init__(self, filename, mode='a', encoding='utf-8', delay=False):
        # ใช้ชื่อไฟล์พื้นฐาน แล้วให้ log_manager จัดการ
        super().__init__(filename, mode, encoding, delay)
        self.base_filename = filename
    
    def emit(self, record):
        """Override emit เพื่อตรวจสอบการหมุนเวียนไฟล์"""
        try:
            # ตรวจสอบว่าต้องหมุนเวียนไฟล์หรือไม่
            current_log = log_manager.get_current_log_file()
            
            # ถ้าชื่อไฟล์เปลี่ยน ให้ปิดไฟล์เก่าและเปิดไฟล์ใหม่
            if self.stream and current_log != self.baseFilename:
                self.stream.close()
                self.stream = None
                self.baseFilename = current_log
            
            # เรียก emit ของ parent class
            super().emit(record)
            
        except Exception:
            self.handleError(record)


def setup_daily_rotating_logging(debug_mode: bool = False, log_dir: str = "logs"):
    """ตั้งค่า logging ด้วยการหมุนเวียนรายวัน"""
    log_level = logging.DEBUG if debug_mode else logging.INFO
    
    # สร้างโฟลเดอร์ logs
    os.makedirs(log_dir, exist_ok=True)
    
    # ลบ handlers เดิมทั้งหมด
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # สร้าง custom handler
    log_file = os.path.join(log_dir, "web_app.log")
    file_handler = DailyRotatingFileHandler(log_file, encoding='utf-8')
    console_handler = logging.StreamHandler()
    
    # ตั้งค่า format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # เพิ่ม handlers
    logging.root.setLevel(log_level)
    logging.root.addHandler(file_handler)
    logging.root.addHandler(console_handler)
    
    # จัดการ encoding สำหรับ Windows
    import sys
    if sys.platform == 'win32':
        try:
            console_handler.stream.reconfigure(encoding='utf-8')
        except:
            pass
    
    # ตั้งค่า level สำหรับ logger เฉพาะ
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    # ทำ cleanup ครั้งแรก
    log_manager.cleanup_old_logs()
    
    logger = logging.getLogger(__name__)
    logger.info(f"Daily rotating logging initialized (retention: {log_manager.retention_days} days)")


def force_log_rotation():
    """บังคับหมุนเวียน log ทันที (สำหรับทดสอบ)"""
    with log_manager._lock:
        log_manager.current_date = None
        log_manager._rotate_if_needed()


def get_log_status():
    """ดึงสถานะของระบบ log"""
    return {
        'current_date': log_manager.current_date,
        'current_log_file': log_manager.current_log_file,
        'retention_days': log_manager.retention_days,
        'log_files': log_manager.get_log_files_info()
    }