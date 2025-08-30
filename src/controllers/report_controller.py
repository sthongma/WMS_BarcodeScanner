#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Report Controller
Handles report generation and export functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import pandas as pd
import os
from typing import Dict, Any, Optional, List
from database.database_manager import DatabaseManager


class ReportController:
    """ควบคุมการทำงานของรายงาน"""
    
    def __init__(self, main_app):
        self.main_app = main_app
        self.db = DatabaseManager.get_instance()
        
        # UI Variables
        self.report_date_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        self.report_job_type_var = tk.StringVar()
        self.report_sub_job_type_var = tk.StringVar()
        self.report_note_filter_var = tk.StringVar()
        
        # UI References
        self.report_job_type_combo = None
        self.report_sub_job_type_combo = None
        self.report_tree = None
        self.report_info_label = None
        
        # Data storage
        self.job_types_data = main_app.job_types_data
        self.report_job_types_data = {}
        self.report_sub_job_types_data = {}
        self.current_report_data = []
        self.current_report_summary = {}
        
    def create_reports_ui(self, parent_frame):
        """สร้าง UI สำหรับรายงาน"""
        # Filter selection frame
        filter_frame = ttk.LabelFrame(parent_frame, text="เลือกเงื่อนไขรายงาน", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Date selection
        date_frame = ttk.Frame(filter_frame)
        date_frame.pack(fill=tk.X, pady=5)
        ttk.Label(date_frame, text="วันที่:").pack(side=tk.LEFT)
        report_date_entry = ttk.Entry(date_frame, textvariable=self.report_date_var, width=15)
        report_date_entry.pack(side=tk.LEFT, padx=10)
        
        # Job Type selection
        job_type_frame = ttk.Frame(filter_frame)
        job_type_frame.pack(fill=tk.X, pady=5)
        ttk.Label(job_type_frame, text="งานหลัก:").pack(side=tk.LEFT)
        self.report_job_type_combo = ttk.Combobox(job_type_frame, textvariable=self.report_job_type_var, 
                                                  state="readonly", width=30)
        self.report_job_type_combo.pack(side=tk.LEFT, padx=10)
        self.report_job_type_combo.bind("<<ComboboxSelected>>", self.on_report_job_type_change)
        
        # Sub Job Type selection
        sub_job_type_frame = ttk.Frame(filter_frame)
        sub_job_type_frame.pack(fill=tk.X, pady=5)
        ttk.Label(sub_job_type_frame, text="งานรอง:").pack(side=tk.LEFT)
        self.report_sub_job_type_combo = ttk.Combobox(sub_job_type_frame, textvariable=self.report_sub_job_type_var, 
                                                      state="readonly", width=30)
        self.report_sub_job_type_combo.pack(side=tk.LEFT, padx=10)
        
        # Note filter
        note_frame = ttk.Frame(filter_frame)
        note_frame.pack(fill=tk.X, pady=5)
        ttk.Label(note_frame, text="กรองหมายเหตุ:").pack(side=tk.LEFT)
        note_entry = ttk.Entry(note_frame, textvariable=self.report_note_filter_var, width=30)
        note_entry.pack(side=tk.LEFT, padx=10)
        
        # Action buttons
        button_frame = ttk.Frame(filter_frame)
        button_frame.pack(fill=tk.X, pady=10)
        ttk.Button(button_frame, text="สร้างรายงาน", command=self.run_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="ส่งออก Excel", command=self.export_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="ล้างข้อมูล", command=self.clear_report).pack(side=tk.LEFT, padx=5)
        
        # Results table
        self.create_report_table(parent_frame)
        
        # Load initial data
        self.refresh_report_job_types()
        
        return parent_frame
    
    def create_report_table(self, parent):
        """สร้างตารางสำหรับแสดงรายงาน"""
        table_frame = ttk.LabelFrame(parent, text="ผลลัพธ์รายงาน", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create frame for table and scrollbars
        tree_frame = ttk.Frame(table_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for table display
        columns = ('บาร์โค้ด', 'วันที่/เวลา', 'ประเภทงานหลัก', 'ประเภทงานย่อย', 'หมายเหตุ', 'ผู้ใช้')
        self.report_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Define headings and column widths
        column_widths = {
            'บาร์โค้ด': 150,
            'วันที่/เวลา': 150,
            'ประเภทงานหลัก': 150,
            'ประเภทงานย่อย': 150,
            'หมายเหตุ': 200,
            'ผู้ใช้': 120
        }
        
        for col in columns:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=column_widths.get(col, 150))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.report_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.report_tree.xview)
        self.report_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout for proper scrollbar positioning
        self.report_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Info label
        info_frame = ttk.Frame(table_frame)
        info_frame.pack(fill=tk.X, pady=5)
        self.report_info_label = ttk.Label(info_frame, text="พร้อมสร้างรายงาน", font=("Arial", 9), foreground="gray")
        self.report_info_label.pack(side=tk.LEFT)
    
    def refresh_report_job_types(self):
        """รีเฟรชประเภทงานสำหรับรายงาน"""
        try:
            # Clear existing data
            self.report_job_types_data.clear()
            
            # Get job types from database
            query = "SELECT id, job_name FROM job_types ORDER BY job_name"
            results = self.db.execute_query(query)
            
            job_names = []
            for row in results:
                job_name = row['job_name']
                job_id = row['id']
                self.report_job_types_data[job_name] = job_id
                job_names.append(job_name)
            
            # Update combo box
            self.report_job_type_combo['values'] = job_names
            
            # Auto-select first job if available
            if job_names:
                self.report_job_type_var.set(job_names[0])
                self.on_report_job_type_change()
            
        except Exception as e:
            print(f"Error refreshing report job types: {str(e)}")
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการโหลดประเภทงาน: {str(e)}")
    
    def on_report_job_type_change(self, event=None):
        """เมื่อเปลี่ยนประเภทงานหลักในรายงาน"""
        try:
            selected_job = self.report_job_type_var.get()
            if not selected_job:
                return
            
            # Clear sub job types
            self.report_sub_job_type_var.set("")
            self.report_sub_job_types_data.clear()
            
            # Get job ID
            job_id = self.report_job_types_data.get(selected_job)
            if job_id is None:
                return
            
            # Load sub job types
            query = """
                SELECT id, sub_job_name 
                FROM sub_job_types 
                WHERE main_job_id = ? AND is_active = 1 
                ORDER BY sub_job_name
            """
            results = self.db.execute_query(query, (job_id,))
            
            sub_job_names = [""]  # Add empty option for "all sub jobs"
            for row in results:
                sub_job_name = row['sub_job_name']
                sub_job_id = row['id']
                self.report_sub_job_types_data[sub_job_name] = sub_job_id
                sub_job_names.append(sub_job_name)
            
            # Update combo box
            self.report_sub_job_type_combo['values'] = sub_job_names
            
        except Exception as e:
            print(f"Error loading sub job types for report: {str(e)}")
    
    def run_report(self):
        """สร้างรายงาน"""
        # Get filter values
        report_date = self.report_date_var.get()
        selected_job_type = self.report_job_type_var.get()
        selected_sub_job_type = self.report_sub_job_type_var.get()
        note_filter = self.report_note_filter_var.get().strip()
        
        # Validate inputs
        if not report_date:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกวันที่")
            return
        
        if not selected_job_type:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกงานหลัก")
            return
        
        try:
            # Get actual IDs
            job_type_id = self.report_job_types_data.get(selected_job_type)
            sub_job_type_id = None
            if selected_sub_job_type:
                sub_job_type_id = self.report_sub_job_types_data.get(selected_sub_job_type)
            
            # Build query
            if job_type_id and sub_job_type_id:
                # Specific job type and sub job type
                report_query = """
                    SELECT 
                        sl.barcode,
                        sl.scan_date,
                        sl.notes,
                        sl.user_id,
                        jt.job_name as job_type_name,
                        sjt.sub_job_name as sub_job_type_name
                    FROM scan_logs sl
                    LEFT JOIN job_types jt ON sl.job_id = jt.id
                    LEFT JOIN sub_job_types sjt ON sl.sub_job_id = sjt.id
                    WHERE sl.job_id = ? 
                    AND sl.sub_job_id = ?
                    AND CAST(sl.scan_date AS DATE) = ?
                """
                params = [job_type_id, sub_job_type_id, report_date]
            elif job_type_id:
                # Specific job type, all sub job types
                report_query = """
                    SELECT 
                        sl.barcode,
                        sl.scan_date,
                        sl.notes,
                        sl.user_id,
                        jt.job_name as job_type_name,
                        ISNULL(sjt.sub_job_name, 'ไม่มี') as sub_job_type_name
                    FROM scan_logs sl
                    LEFT JOIN job_types jt ON sl.job_id = jt.id
                    LEFT JOIN sub_job_types sjt ON sl.sub_job_id = sjt.id
                    WHERE sl.job_id = ? 
                    AND CAST(sl.scan_date AS DATE) = ?
                """
                params = [job_type_id, report_date]
            else:
                messagebox.showwarning("คำเตือน", "กรุณาเลือกงานหลัก")
                return
            
            # Add note filter if specified
            if note_filter:
                report_query += " AND sl.notes LIKE ?"
                params.append(f"%{note_filter}%")
            
            report_query += " ORDER BY sl.scan_date DESC"
            
            # Execute query
            results = self.db.execute_query(report_query, tuple(params))
            
            # Store data for export
            self.current_report_data = results
            self.current_report_summary = {
                'report_date': report_date,
                'job_type_name': selected_job_type,
                'sub_job_type_name': selected_sub_job_type or 'ทั้งหมด',
                'note_filter': note_filter if note_filter else None,
                'total_count': len(results),
                'generated_at': datetime.datetime.now().isoformat()
            }
            
            if not results:
                messagebox.showinfo("ผลลัพธ์", "ไม่พบข้อมูลในวันที่ที่เลือก")
                self.clear_report_display()
                return
            
            # Clear existing data in tree
            for item in self.report_tree.get_children():
                self.report_tree.delete(item)
            
            # Add new data to tree
            for row in results:
                formatted_date = row['scan_date'].strftime("%Y-%m-%d %H:%M:%S")
                self.report_tree.insert('', tk.END, values=(
                    row['barcode'],
                    formatted_date,
                    row['job_type_name'] or '',
                    row['sub_job_type_name'] or '',
                    row['notes'] or '',
                    row['user_id']
                ))
            
            # Update info label
            count = len(results)
            filter_text = f" (กรองด้วย: {note_filter})" if note_filter else ""
            self.report_info_label.config(
                text=f"พบ {count} รายการ - {selected_job_type} > {selected_sub_job_type or 'ทั้งหมด'} วันที่ {report_date}{filter_text}"
            )
            
            messagebox.showinfo("สำเร็จ", f"สร้างรายงานเรียบร้อย พบ {count} รายการ")
            
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการสร้างรายงาน: {str(e)}")
    
    def export_report(self):
        """ส่งออกรายงานเป็น Excel"""
        if not self.current_report_data:
            messagebox.showwarning("คำเตือน", "ไม่มีข้อมูลสำหรับส่งออก กรุณาสร้างรายงานก่อน")
            return
        
        try:
            # Select file location
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="บันทึกรายงานเป็น"
            )
            
            if not filename:
                return
            
            # Prepare data for DataFrame
            export_data = []
            for row in self.current_report_data:
                export_data.append({
                    'บาร์โค้ด': row['barcode'],
                    'วันที่/เวลา': row['scan_date'].strftime("%Y-%m-%d %H:%M:%S"),
                    'ประเภทงานหลัก': row['job_type_name'] or '',
                    'ประเภทงานย่อย': row['sub_job_type_name'] or '',
                    'หมายเหตุ': row['notes'] or '',
                    'ผู้ใช้': row['user_id']
                })
            
            # Create DataFrame
            df = pd.DataFrame(export_data)
            
            # Create Excel writer object
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Write summary sheet
                summary_data = {
                    'รายการ': [
                        'วันที่รายงาน',
                        'งานหลัก',
                        'งานรอง',
                        'กรองหมายเหตุ',
                        'จำนวนรวม',
                        'วันที่สร้าง'
                    ],
                    'ค่า': [
                        self.current_report_summary['report_date'],
                        self.current_report_summary['job_type_name'],
                        self.current_report_summary['sub_job_type_name'],
                        self.current_report_summary['note_filter'] or 'ไม่มี',
                        self.current_report_summary['total_count'],
                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ]
                }
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='สรุป', index=False)
                
                # Write data sheet
                if not df.empty:
                    df.to_excel(writer, sheet_name='ข้อมูล', index=False)
                
                # Auto-adjust column widths
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
            
            messagebox.showinfo("สำเร็จ", f"ส่งออกรายงานเรียบร้อยแล้ว\nไฟล์: {filename}")
            
            # Ask if want to open file
            if messagebox.askyesno("เปิดไฟล์", "ต้องการเปิดไฟล์ที่ส่งออกหรือไม่?"):
                os.startfile(filename)
            
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการส่งออก: {str(e)}")
    
    def clear_report(self):
        """ล้างข้อมูลรายงาน"""
        # Clear tree
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)
        
        # Clear data
        self.current_report_data = []
        self.current_report_summary = {}
        
        # Reset info label
        self.report_info_label.config(text="พร้อมสร้างรายงาน")
    
    def clear_report_display(self):
        """ล้างการแสดงผลรายงานเท่านั้น"""
        # Clear tree
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)
        
        # Reset info label
        self.report_info_label.config(text="ไม่พบข้อมูล")