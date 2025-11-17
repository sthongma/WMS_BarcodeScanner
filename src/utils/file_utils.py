#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Utilities Module
Handles file operations and utilities
"""

import os
import pandas as pd
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
from typing import Optional, List, Dict, Any


def select_file(title: str = "เลือกไฟล์", file_types: List[tuple] = None) -> Optional[str]:
    """เลือกไฟล์และส่งคืน path"""
    if file_types is None:
        file_types = [
            ("Excel files", "*.xlsx *.xls"),
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ]
    
    file_path = filedialog.askopenfilename(
        title=title,
        filetypes=file_types
    )
    
    return file_path if file_path else None


def save_file(title: str = "บันทึกไฟล์", file_types: List[tuple] = None) -> Optional[str]:
    """เลือกตำแหน่งบันทึกไฟล์และส่งคืน path"""
    if file_types is None:
        file_types = [
            ("Excel files", "*.xlsx"),
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ]
    
    file_path = filedialog.asksaveasfilename(
        title=title,
        filetypes=file_types,
        defaultextension=file_types[0][1].split('*')[1] if file_types else ""
    )
    
    return file_path if file_path else None


def read_excel_file(file_path: str) -> Optional[pd.DataFrame]:
    """อ่านไฟล์ Excel และส่งคืน DataFrame (ข้อมูลทั้งหมดเป็น text)"""
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, encoding='utf-8', dtype=str, keep_default_na=False)
        else:
            df = pd.read_excel(file_path, dtype=str, keep_default_na=False)
        return df
    except Exception as e:
        messagebox.showerror("Error", f"ไม่สามารถอ่านไฟล์ได้: {str(e)}")
        return None


def export_to_excel(data: List[Dict[str, Any]], file_path: str, sheet_name: str = "Sheet1") -> bool:
    """ส่งออกข้อมูลเป็นไฟล์ Excel"""
    try:
        df = pd.DataFrame(data)
        df.to_excel(file_path, sheet_name=sheet_name, index=False)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"ไม่สามารถส่งออกไฟล์ได้: {str(e)}")
        return False


def export_to_csv(data: List[Dict[str, Any]], file_path: str) -> bool:
    """ส่งออกข้อมูลเป็นไฟล์ CSV"""
    try:
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        return True
    except Exception as e:
        messagebox.showerror("Error", f"ไม่สามารถส่งออกไฟล์ได้: {str(e)}")
        return False


def create_template_excel(file_path: str, columns: List[str], sample_data: List[List] = None) -> bool:
    """สร้างไฟล์ Excel template"""
    try:
        df = pd.DataFrame(columns=columns)
        
        if sample_data:
            sample_df = pd.DataFrame(sample_data, columns=columns)
            df = pd.concat([df, sample_df], ignore_index=True)
        
        df.to_excel(file_path, index=False)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"ไม่สามารถสร้างไฟล์ template ได้: {str(e)}")
        return False


def ensure_directory_exists(directory_path: str) -> bool:
    """ตรวจสอบและสร้างโฟลเดอร์ถ้ายังไม่มี"""
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"ไม่สามารถสร้างโฟลเดอร์ได้: {str(e)}")
        return False


def get_file_extension(file_path: str) -> str:
    """รับนามสกุลไฟล์"""
    return os.path.splitext(file_path)[1].lower()


def is_valid_file_path(file_path: str) -> bool:
    """ตรวจสอบว่า path ไฟล์ถูกต้องหรือไม่"""
    return os.path.exists(file_path) and os.path.isfile(file_path) 