#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation Utilities Module
Handles data validation and verification
"""

import re
import pandas as pd
import tkinter.messagebox as messagebox
from typing import List, Dict, Any, Tuple, Optional


def validate_barcode(barcode: str) -> bool:
    """ตรวจสอบความถูกต้องของ barcode"""
    if not barcode or not isinstance(barcode, str):
        return False
    
    # ตรวจสอบว่า barcode ไม่ว่างและมีความยาวที่เหมาะสม
    barcode = barcode.strip()
    if len(barcode) < 3 or len(barcode) > 50:
        return False
    
    # ตรวจสอบว่า barcode มีเฉพาะตัวอักษรและตัวเลข
    if not re.match(r'^[A-Za-z0-9\-_\.]+$', barcode):
        return False
    
    return True


def validate_job_type(job_type: str) -> bool:
    """ตรวจสอบความถูกต้องของ job type"""
    if not job_type or not isinstance(job_type, str):
        return False
    
    job_type = job_type.strip()
    if len(job_type) < 1 or len(job_type) > 100:
        return False
    
    return True


def validate_sub_job_type(sub_job_type: str) -> bool:
    """ตรวจสอบความถูกต้องของ sub job type"""
    if not sub_job_type or not isinstance(sub_job_type, str):
        return False
    
    sub_job_type = sub_job_type.strip()
    if len(sub_job_type) < 1 or len(sub_job_type) > 100:
        return False
    
    return True


def validate_import_data(df: pd.DataFrame, required_columns: List[str]) -> Tuple[bool, List[str]]:
    """ตรวจสอบความถูกต้องของข้อมูลที่นำเข้า"""
    errors = []
    
    # ตรวจสอบว่ามีข้อมูลหรือไม่
    if df.empty:
        errors.append("ไฟล์ไม่มีข้อมูล")
        return False, errors
    
    # ตรวจสอบคอลัมน์ที่จำเป็น
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        errors.append(f"คอลัมน์ที่ขาดหายไป: {', '.join(missing_columns)}")
    
    # ตรวจสอบข้อมูลในแต่ละแถว
    for index, row in df.iterrows():
        row_errors = validate_import_row(row, index + 1, required_columns)
        errors.extend(row_errors)
    
    return len(errors) == 0, errors


def validate_import_row(row: pd.Series, row_number: int, required_columns: List[str]) -> List[str]:
    """ตรวจสอบความถูกต้องของข้อมูลในแต่ละแถว"""
    errors = []
    
    for col in required_columns:
        if col not in row:
            errors.append(f"แถว {row_number}: คอลัมน์ '{col}' ไม่พบ")
            continue
        
        value = row[col]
        
        # ตรวจสอบว่าค่าไม่เป็น NaN
        if pd.isna(value):
            errors.append(f"แถว {row_number}: คอลัมน์ '{col}' ไม่สามารถว่างได้")
            continue
        
        # แปลงเป็น string และตรวจสอบ
        value_str = str(value).strip()
        if not value_str:
            errors.append(f"แถว {row_number}: คอลัมน์ '{col}' ไม่สามารถว่างได้")
            continue
        
        # ตรวจสอบตามประเภทของคอลัมน์
        if col.lower() in ['barcode', 'barcode_id']:
            if not validate_barcode(value_str):
                errors.append(f"แถว {row_number}: คอลัมน์ '{col}' มีรูปแบบ barcode ไม่ถูกต้อง")
        
        elif col.lower() in ['job_type', 'job_type_id']:
            if not validate_job_type(value_str):
                errors.append(f"แถว {row_number}: คอลัมน์ '{col}' มีรูปแบบ job type ไม่ถูกต้อง")
        
        elif col.lower() in ['sub_job_type', 'sub_job_type_id']:
            if not validate_sub_job_type(value_str):
                errors.append(f"แถว {row_number}: คอลัมน์ '{col}' มีรูปแบบ sub job type ไม่ถูกต้อง")
    
    return errors


def validate_database_connection(server: str, database: str, auth_type: str, 
                               username: str = "", password: str = "") -> Tuple[bool, str]:
    """ตรวจสอบการตั้งค่าการเชื่อมต่อฐานข้อมูล"""
    errors = []
    
    if not server or not server.strip():
        errors.append("Server ไม่สามารถว่างได้")
    
    if not database or not database.strip():
        errors.append("Database ไม่สามารถว่างได้")
    
    if auth_type not in ["Windows", "SQL"]:
        errors.append("Authentication Type ต้องเป็น Windows หรือ SQL")
    
    if auth_type == "SQL":
        if not username or not username.strip():
            errors.append("Username ไม่สามารถว่างได้เมื่อใช้ SQL Authentication")
        if not password:
            errors.append("Password ไม่สามารถว่างได้เมื่อใช้ SQL Authentication")
    
    error_message = "; ".join(errors) if errors else ""
    return len(errors) == 0, error_message


def validate_date_format(date_str: str, format_str: str = "%Y-%m-%d") -> bool:
    """ตรวจสอบรูปแบบวันที่"""
    try:
        from datetime import datetime
        datetime.strptime(date_str, format_str)
        return True
    except ValueError:
        return False


def validate_email(email: str) -> bool:
    """ตรวจสอบรูปแบบอีเมล"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone_number(phone: str) -> bool:
    """ตรวจสอบรูปแบบเบอร์โทรศัพท์"""
    # รับเบอร์โทรศัพท์ไทย
    pattern = r'^(\+66|0)[0-9]{8,9}$'
    return bool(re.match(pattern, phone.replace('-', '').replace(' ', '')))


def sanitize_input(input_str: str) -> str:
    """ทำความสะอาดข้อมูลที่รับเข้ามา"""
    if not input_str:
        return ""
    
    # ลบ whitespace ที่ไม่จำเป็น
    cleaned = input_str.strip()
    
    # ลบอักขระพิเศษที่อาจเป็นอันตราย
    cleaned = re.sub(r'[<>"\']', '', cleaned)
    
    return cleaned


def validate_numeric_range(value: Any, min_val: float = None, max_val: float = None) -> bool:
    """ตรวจสอบว่าค่าตัวเลขอยู่ในช่วงที่กำหนดหรือไม่"""
    try:
        num_val = float(value)
        
        if min_val is not None and num_val < min_val:
            return False
        
        if max_val is not None and num_val > max_val:
            return False
        
        return True
    except (ValueError, TypeError):
        return False 