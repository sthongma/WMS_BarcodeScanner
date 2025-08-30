#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scan Controller
Handles scanning functionality and barcode processing
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Dict, Any, Optional, List
from database.database_manager import DatabaseManager


class ScanController:
    """ควบคุมการทำงานของการสแกนบาร์โค้ด"""
    
    def __init__(self, main_app):
        self.main_app = main_app
        self.db = DatabaseManager.get_instance()
        
        # UI Variables
        self.current_job_type = main_app.current_job_type
        self.current_sub_job_type = main_app.current_sub_job_type
        self.notes_var = main_app.notes_var
        self.barcode_entry_var = main_app.barcode_entry_var
        
        # Data storage
        self.job_types_data = main_app.job_types_data
        self.sub_job_types_data = main_app.sub_job_types_data
        
        # UI References
        self.job_combo = None
        self.sub_job_combo = None
        self.notes_entry = None
        self.barcode_entry = None
        self.summary_labels = {}
        
    def create_scanning_ui(self, parent_frame):
        """สร้าง UI สำหรับการสแกน"""
        # Main scanning area
        main_frame = ttk.LabelFrame(parent_frame, text="สแกนบาร์โค้ด", padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Job type selection
        job_frame = ttk.Frame(main_frame)
        job_frame.pack(fill=tk.X, pady=10)
        
        # Main job type
        main_job_frame = ttk.Frame(job_frame)
        main_job_frame.pack(fill=tk.X, pady=5)
        ttk.Label(main_job_frame, text="ประเภทงานหลัก:", font=("Arial", 12), width=15).pack(side=tk.LEFT)
        self.job_combo = ttk.Combobox(main_job_frame, textvariable=self.current_job_type,
                                     state="readonly", font=("Arial", 12), width=25)
        self.job_combo.pack(side=tk.LEFT, padx=10)
        self.job_combo.bind('<<ComboboxSelected>>', self.on_main_job_change)
        
        # Sub job type
        sub_job_frame = ttk.Frame(job_frame)
        sub_job_frame.pack(fill=tk.X, pady=5)
        ttk.Label(sub_job_frame, text="ประเภทงานย่อย:", font=("Arial", 12), width=15).pack(side=tk.LEFT)
        self.sub_job_combo = ttk.Combobox(sub_job_frame, textvariable=self.current_sub_job_type,
                                         state="readonly", font=("Arial", 12), width=25)
        self.sub_job_combo.pack(side=tk.LEFT, padx=10)
        self.sub_job_combo.bind('<<ComboboxSelected>>', self.on_sub_job_change)
        
        # Notes
        notes_frame = ttk.Frame(job_frame)
        notes_frame.pack(fill=tk.X, pady=5)
        ttk.Label(notes_frame, text="หมายเหตุ:", font=("Arial", 12), width=15).pack(side=tk.LEFT)
        self.notes_entry = ttk.Entry(notes_frame, textvariable=self.notes_var,
                                    font=("Arial", 12), width=40)
        self.notes_entry.pack(side=tk.LEFT, padx=10)
        
        # Bind notes entry events
        self.notes_entry.bind('<KeyRelease>', self.on_notes_change)
        self.notes_var.trace('w', self.on_notes_var_change)
        
        # Barcode input
        barcode_frame = ttk.Frame(main_frame)
        barcode_frame.pack(fill=tk.X, pady=20)
        
        ttk.Label(barcode_frame, text="บาร์โค้ด:", font=("Arial", 12)).pack(side=tk.LEFT)
        self.barcode_entry = ttk.Entry(barcode_frame, textvariable=self.barcode_entry_var,
                                      font=("Arial", 14), width=40)
        self.barcode_entry.pack(side=tk.LEFT, padx=10)
        self.barcode_entry.bind('<Return>', self.process_barcode)
        
        # Today Summary section
        self.create_today_summary_ui(main_frame)
        
        return main_frame
    
    def create_today_summary_ui(self, parent):
        """สร้าง UI สำหรับสรุปงานวันนี้"""
        today_summary_frame = ttk.LabelFrame(parent, text="📊 สรุปงานวันนี้", padding=15)
        today_summary_frame.pack(fill=tk.X, pady=10)
        
        # Summary content frame
        summary_content_frame = ttk.Frame(today_summary_frame)
        summary_content_frame.pack(fill=tk.X)
        
        # Job Type row
        job_row = ttk.Frame(summary_content_frame)
        job_row.pack(fill=tk.X, pady=2)
        ttk.Label(job_row, text="งานหลัก:", font=("Arial", 10, "bold"), foreground="#0c5184").pack(side=tk.LEFT)
        self.summary_labels['job_type'] = ttk.Label(job_row, text="ไม่ได้เลือก", font=("Arial", 10))
        self.summary_labels['job_type'].pack(side=tk.LEFT, padx=(10, 0))
        
        # Sub Job Type row
        sub_job_row = ttk.Frame(summary_content_frame)
        sub_job_row.pack(fill=tk.X, pady=2)
        ttk.Label(sub_job_row, text="งานรอง:", font=("Arial", 10, "bold"), foreground="#0c5184").pack(side=tk.LEFT)
        self.summary_labels['sub_job_type'] = ttk.Label(sub_job_row, text="ไม่ได้เลือก", font=("Arial", 10))
        self.summary_labels['sub_job_type'].pack(side=tk.LEFT, padx=(10, 0))
        
        # Notes Filter row
        notes_filter_row = ttk.Frame(summary_content_frame)
        notes_filter_row.pack(fill=tk.X, pady=2)
        ttk.Label(notes_filter_row, text="กรองหมายเหตุ:", font=("Arial", 10, "bold"), foreground="#0c5184").pack(side=tk.LEFT)
        self.summary_labels['notes_filter'] = ttk.Label(notes_filter_row, text="ไม่มี", font=("Arial", 10))
        self.summary_labels['notes_filter'].pack(side=tk.LEFT, padx=(10, 0))
        
        # Count row
        count_row = ttk.Frame(summary_content_frame)
        count_row.pack(fill=tk.X, pady=(10, 5))
        ttk.Label(count_row, text="จำนวนที่สแกนวันนี้:", font=("Arial", 12, "bold"), foreground="#0c5184").pack(side=tk.LEFT)
        
        count_frame = ttk.Frame(count_row)
        count_frame.pack(side=tk.LEFT, padx=(10, 0))
        self.summary_labels['count'] = ttk.Label(count_frame, text="0", 
                                                font=("Arial", 18, "bold"), 
                                                padding=10)
        self.summary_labels['count'].pack()
        
        # Last update row
        update_row = ttk.Frame(summary_content_frame)
        update_row.pack(fill=tk.X, pady=2)
        ttk.Label(update_row, text="อัปเดทล่าสุด:", font=("Arial", 9), foreground="gray").pack(side=tk.LEFT)
        self.summary_labels['last_update'] = ttk.Label(update_row, text="ยังไม่มีข้อมูล", font=("Arial", 9), foreground="gray")
        self.summary_labels['last_update'].pack(side=tk.LEFT, padx=(5, 0))
    
    def on_main_job_change(self, event=None):
        """เมื่อเปลี่ยนงานหลัก"""
        try:
            selected_job = self.current_job_type.get()
            if not selected_job:
                return
            
            # Clear sub job
            self.current_sub_job_type.set("")
            self.sub_job_combo['values'] = []
            
            # Get job ID
            job_id = None
            for job_data in self.job_types_data:
                if job_data['name'] == selected_job:
                    job_id = job_data['id']
                    break
            
            if job_id is None:
                return
            
            # Load sub job types
            try:
                query = """
                    SELECT id, sub_job_name 
                    FROM sub_job_types 
                    WHERE main_job_id = ? AND is_active = 1 
                    ORDER BY sub_job_name
                """
                results = self.db.execute_query(query, (job_id,))
                
                self.sub_job_types_data.clear()
                sub_job_names = []
                
                for row in results:
                    sub_job_data = {'id': row['id'], 'name': row['sub_job_name']}
                    self.sub_job_types_data.append(sub_job_data)
                    sub_job_names.append(row['sub_job_name'])
                
                self.sub_job_combo['values'] = sub_job_names
                
                # Update today summary
                self.update_today_summary()
                
            except Exception as e:
                print(f"Error loading sub job types: {str(e)}")
                
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการเปลี่ยนงานหลัก: {str(e)}")
    
    def on_sub_job_change(self, event=None):
        """เมื่อเปลี่ยนงานรอง"""
        self.update_today_summary()
    
    def on_notes_change(self, event=None):
        """เมื่อเปลี่ยนหมายเหตุ"""
        self.update_today_summary()
    
    def on_notes_var_change(self, *args):
        """เมื่อตัวแปรหมายเหตุเปลี่ยน"""
        self.update_today_summary()
    
    def process_barcode(self, event=None):
        """ประมวลผลบาร์โค้ด"""
        barcode = self.barcode_entry_var.get().strip()
        if not barcode:
            messagebox.showwarning("คำเตือน", "กรุณากรอกบาร์โค้ด")
            return
        
        # Validate job type selection
        if not self.current_job_type.get():
            messagebox.showwarning("คำเตือน", "กรุณาเลือกประเภทงานหลัก")
            return
        
        try:
            # Get job IDs
            job_id = self._get_job_id(self.current_job_type.get())
            sub_job_id = self._get_sub_job_id(self.current_sub_job_type.get()) if self.current_sub_job_type.get() else None
            
            if job_id is None:
                messagebox.showerror("ข้อผิดพลาด", "ไม่พบข้อมูลประเภทงานหลัก")
                return
            
            # Check dependencies
            if not self._check_dependencies(barcode, job_id):
                return
            
            # Check duplicates
            if self._check_duplicate_scan(barcode, job_id, sub_job_id):
                return
            
            # Save scan record
            self._save_scan_record(barcode, job_id, sub_job_id)
            
            # Clear barcode entry and focus
            self.barcode_entry_var.set("")
            self.barcode_entry.focus()
            
            # Update summary and history
            self.update_today_summary()
            if hasattr(self.main_app, 'refresh_scanning_history'):
                self.main_app.refresh_scanning_history()
            
            # Show success message
            messagebox.showinfo("สำเร็จ", f"บันทึกการสแกนบาร์โค้ด: {barcode}")
            
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการประมวลผลบาร์โค้ด: {str(e)}")
    
    def update_today_summary(self):
        """อัปเดตสรุปงานวันนี้"""
        try:
            # Get current selections
            job_type = self.current_job_type.get()
            sub_job_type = self.current_sub_job_type.get()
            notes_filter = self.notes_var.get().strip()
            
            # Update labels
            self.summary_labels['job_type'].config(text=job_type if job_type else "ไม่ได้เลือก")
            self.summary_labels['sub_job_type'].config(text=sub_job_type if sub_job_type else "ไม่ได้เลือก")
            self.summary_labels['notes_filter'].config(text=notes_filter if notes_filter else "ไม่มี")
            
            # Get count from database
            if job_type:
                job_id = self._get_job_id(job_type)
                if job_id:
                    count = self._get_today_scan_count(job_id, sub_job_type, notes_filter)
                    self.summary_labels['count'].config(text=str(count))
                else:
                    self.summary_labels['count'].config(text="0")
            else:
                self.summary_labels['count'].config(text="0")
            
            # Update timestamp
            current_time = datetime.now().strftime("%H:%M:%S")
            self.summary_labels['last_update'].config(text=current_time)
            
        except Exception as e:
            print(f"Error updating today summary: {str(e)}")
    
    def _get_job_id(self, job_name: str) -> Optional[int]:
        """ดึง job ID จากชื่องาน"""
        for job_data in self.job_types_data:
            if job_data['name'] == job_name:
                return job_data['id']
        return None
    
    def _get_sub_job_id(self, sub_job_name: str) -> Optional[int]:
        """ดึง sub job ID จากชื่องานรอง"""
        for sub_job_data in self.sub_job_types_data:
            if sub_job_data['name'] == sub_job_name:
                return sub_job_data['id']
        return None
    
    def _check_dependencies(self, barcode: str, job_id: int) -> bool:
        """ตรวจสอบ dependencies"""
        try:
            # Check if job_dependencies table exists
            check_query = "SELECT COUNT(*) as count FROM job_dependencies WHERE job_id = ?"
            results = self.db.execute_query(check_query, (job_id,))
            
            if not results or results[0]['count'] == 0:
                return True  # No dependencies
            
            # Check required jobs
            required_query = """
                SELECT jd.required_job_id, jt.job_name 
                FROM job_dependencies jd
                JOIN job_types jt ON jd.required_job_id = jt.id
                WHERE jd.job_id = ?
            """
            required_jobs = self.db.execute_query(required_query, (job_id,))
            
            for required_job in required_jobs:
                check_scan_query = """
                    SELECT COUNT(*) as count 
                    FROM scan_logs 
                    WHERE barcode = ? AND job_id = ?
                """
                scan_result = self.db.execute_query(check_scan_query, (barcode, required_job['required_job_id']))
                
                if scan_result[0]['count'] == 0:
                    messagebox.showerror("ไม่สามารถสแกนได้", 
                                       f'ต้องสแกนงาน "{required_job["job_name"]}" ก่อน')
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error checking dependencies: {str(e)}")
            return True  # Allow scan if error occurs
    
    def _check_duplicate_scan(self, barcode: str, job_id: int, sub_job_id: Optional[int]) -> bool:
        """ตรวจสอบการสแกนซ้ำ"""
        try:
            if sub_job_id:
                query = """
                    SELECT COUNT(*) as count 
                    FROM scan_logs 
                    WHERE barcode = ? AND job_id = ? AND sub_job_id = ?
                """
                results = self.db.execute_query(query, (barcode, job_id, sub_job_id))
            else:
                query = """
                    SELECT COUNT(*) as count 
                    FROM scan_logs 
                    WHERE barcode = ? AND job_id = ? AND sub_job_id IS NULL
                """
                results = self.db.execute_query(query, (barcode, job_id))
            
            if results[0]['count'] > 0:
                messagebox.showwarning("ข้อมูลซ้ำ", f"บาร์โค้ด {barcode} ถูกสแกนในงานนี้แล้ว")
                return True
            
            return False
            
        except Exception as e:
            print(f"Error checking duplicates: {str(e)}")
            return False
    
    def _save_scan_record(self, barcode: str, job_id: int, sub_job_id: Optional[int]):
        """บันทึกข้อมูลการสแกน"""
        job_type_name = self.current_job_type.get()
        notes = self.notes_var.get().strip()
        
        query = """
            INSERT INTO scan_logs (barcode, scan_date, job_type, user_id, job_id, sub_job_id, notes)
            VALUES (?, GETDATE(), ?, ?, ?, ?, ?)
        """
        
        self.db.execute_non_query(query, (
            barcode, job_type_name, self.db.current_user, 
            job_id, sub_job_id, notes if notes else None
        ))
    
    def _get_today_scan_count(self, job_id: int, sub_job_type: str, notes_filter: str) -> int:
        """ดึงจำนวนการสแกนวันนี้"""
        try:
            if sub_job_type:
                sub_job_id = self._get_sub_job_id(sub_job_type)
                query = """
                    SELECT COUNT(*) as count 
                    FROM scan_logs 
                    WHERE job_id = ? AND sub_job_id = ? AND CAST(scan_date AS DATE) = CAST(GETDATE() AS DATE)
                """
                params = [job_id, sub_job_id]
            else:
                query = """
                    SELECT COUNT(*) as count 
                    FROM scan_logs 
                    WHERE job_id = ? AND CAST(scan_date AS DATE) = CAST(GETDATE() AS DATE)
                """
                params = [job_id]
            
            # Add notes filter if provided
            if notes_filter:
                query += " AND notes LIKE ?"
                params.append(f"%{notes_filter}%")
            
            results = self.db.execute_query(query, tuple(params))
            return results[0]['count'] if results else 0
            
        except Exception as e:
            print(f"Error getting today scan count: {str(e)}")
            return 0