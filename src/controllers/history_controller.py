#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
History Controller
Handles history viewing and searching functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from typing import Dict, Any, Optional, List
from database.database_manager import DatabaseManager


class HistoryController:
    """ควบคุมการทำงานของการดูประวัติ"""
    
    def __init__(self, main_app):
        self.main_app = main_app
        self.db = DatabaseManager.get_instance()
        
        # UI References
        self.history_tree = None
        self.date_entry = None
        self.search_barcode_entry = None
        self.search_job_combo = None
        
        # Data
        self.job_types_data = main_app.job_types_data
        
    def create_history_ui(self, parent_frame):
        """สร้าง UI สำหรับดูประวัติ"""
        # Search controls
        search_frame = ttk.LabelFrame(parent_frame, text="ค้นหา", padding=10)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Date search
        date_frame = ttk.Frame(search_frame)
        date_frame.pack(fill=tk.X, pady=2)
        ttk.Label(date_frame, text="วันที่:").pack(side=tk.LEFT)
        self.date_entry = ttk.Entry(date_frame, width=12)
        self.date_entry.pack(side=tk.LEFT, padx=5)
        self.date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.date_entry.bind('<Return>', self.search_history)
        
        # Barcode search
        barcode_search_frame = ttk.Frame(search_frame)
        barcode_search_frame.pack(fill=tk.X, pady=2)
        ttk.Label(barcode_search_frame, text="บาร์โค้ด:").pack(side=tk.LEFT)
        self.search_barcode_entry = ttk.Entry(barcode_search_frame, width=30)
        self.search_barcode_entry.pack(side=tk.LEFT, padx=5)
        self.search_barcode_entry.bind('<Return>', self.search_history)
        
        # Job type search
        job_search_frame = ttk.Frame(search_frame)
        job_search_frame.pack(fill=tk.X, pady=2)
        ttk.Label(job_search_frame, text="ประเภทงาน:").pack(side=tk.LEFT)
        self.search_job_combo = ttk.Combobox(job_search_frame, state="readonly", width=25)
        self.search_job_combo.pack(side=tk.LEFT, padx=5)
        self.search_job_combo.bind('<<ComboboxSelected>>', self.search_history)
        
        # Search button
        search_btn_frame = ttk.Frame(search_frame)
        search_btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(search_btn_frame, text="ค้นหา", command=self.search_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_btn_frame, text="รีเซ็ต", command=self.reset_search).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_btn_frame, text="รีเฟรช", command=self.refresh_history).pack(side=tk.LEFT, padx=5)
        
        # Results table
        self.create_history_table(parent_frame)
        
        # Load initial data
        self.load_job_types_for_search()
        self.refresh_history()
        
        return parent_frame
    
    def create_history_table(self, parent):
        """สร้างตารางสำหรับแสดงประวัติ"""
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create frame for table and scrollbars
        tree_frame = ttk.Frame(table_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for table display
        columns = ('ID', 'บาร์โค้ด', 'วันที่/เวลา', 'ประเภทงานหลัก', 'ประเภทงานย่อย', 'หมายเหตุ', 'ผู้ใช้')
        self.history_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        # Define headings and column widths
        column_widths = {
            'ID': 80,
            'บาร์โค้ด': 200,
            'วันที่/เวลา': 150,
            'ประเภทงานหลัก': 200,
            'ประเภทงานย่อย': 200,
            'หมายเหตุ': 300,
            'ผู้ใช้': 150
        }
        
        for col in columns:
            self.history_tree.heading(col, text=col, command=lambda c=col: self.sort_column(c))
            self.history_tree.column(col, width=column_widths.get(col, 150))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.history_tree.xview)
        self.history_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout for proper scrollbar positioning
        self.history_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Context menu for history records
        self.create_context_menu()
        
        # Info label
        info_frame = ttk.Frame(table_frame)
        info_frame.pack(fill=tk.X, pady=5)
        self.info_label = ttk.Label(info_frame, text="พร้อมค้นหา", font=("Arial", 9), foreground="gray")
        self.info_label.pack(side=tk.LEFT)
    
    def create_context_menu(self):
        """สร้าง context menu สำหรับ history record"""
        self.context_menu = tk.Menu(self.history_tree, tearoff=0)
        # Original simple labels
        self.context_menu.add_command(label="แก้ไข", command=self.edit_history_record)
        self.context_menu.add_command(label="ลบ", command=self.delete_history_record)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="คัดลอกบาร์โค้ด", command=self.copy_barcode)
        # Single bind (controller not used in unified UI but kept minimal)
        self.history_tree.bind("<Button-3>", self.show_context_menu)
    
    def show_context_menu(self, event):
        """แสดง context menu (simple)"""
        try:
            item = self.history_tree.selection()[0]
            self.context_menu.post(event.x_root, event.y_root)
        except IndexError:
            pass
    
    def search_history(self, event=None):
        """ค้นหาประวัติ"""
        try:
            # Get search parameters
            search_date = self.date_entry.get().strip()
            search_barcode = self.search_barcode_entry.get().strip()
            search_job = self.search_job_combo.get().strip()
            
            # Build query
            query = """
                SELECT 
                    sl.id,
                    sl.barcode,
                    sl.scan_date,
                    jt.job_name as job_type_name,
                    ISNULL(sjt.sub_job_name, '-') as sub_job_type_name,
                    ISNULL(sl.notes, '') as notes,
                    sl.user_id
                FROM scan_logs sl
                LEFT JOIN job_types jt ON sl.job_id = jt.id
                LEFT JOIN sub_job_types sjt ON sl.sub_job_id = sjt.id
                WHERE 1=1
            """
            
            params = []
            
            # Add date filter
            if search_date:
                query += " AND CAST(sl.scan_date AS DATE) = ?"
                params.append(search_date)
            
            # Add barcode filter
            if search_barcode:
                query += " AND sl.barcode LIKE ?"
                params.append(f"%{search_barcode}%")
            
            # Add job type filter
            if search_job:
                query += " AND jt.job_name = ?"
                params.append(search_job)
            
            query += " ORDER BY sl.scan_date DESC"
            
            # Execute query
            results = self.db.execute_query(query, tuple(params))
            
            # Clear existing data
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            
            # Add new data
            for row in results:
                formatted_date = row['scan_date'].strftime("%Y-%m-%d %H:%M:%S")
                self.history_tree.insert('', tk.END, values=(
                    row['id'],
                    row['barcode'],
                    formatted_date,
                    row['job_type_name'] or '',
                    row['sub_job_type_name'],
                    row['notes'],
                    row['user_id']
                ))
            
            # Update info label
            count = len(results)
            self.info_label.config(text=f"พบ {count} รายการ")
            
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการค้นหา: {str(e)}")
    
    def refresh_history(self):
        """รีเฟรชข้อมูลประวัติ"""
        # Clear search fields and search again
        self.reset_search()
        self.search_history()
    
    def reset_search(self):
        """รีเซ็ตการค้นหา"""
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.search_barcode_entry.delete(0, tk.END)
        self.search_job_combo.set("")
    
    def load_job_types_for_search(self):
        """โหลดประเภทงานสำหรับการค้นหา"""
        try:
            job_names = [""] + [job['name'] for job in self.job_types_data]
            self.search_job_combo['values'] = job_names
        except Exception as e:
            print(f"Error loading job types for search: {str(e)}")
    
    def sort_column(self, col):
        """เรียงข้อมูลในคอลัมน์"""
        try:
            # Get all data
            data = [(self.history_tree.set(child, col), child) for child in self.history_tree.get_children('')]
            
            # Sort data
            data.sort(key=lambda x: x[0])
            
            # Reorder items
            for index, (val, child) in enumerate(data):
                self.history_tree.move(child, '', index)
                
        except Exception as e:
            print(f"Error sorting column {col}: {str(e)}")
    
    def edit_history_record(self):
        """แก้ไขข้อมูลประวัติ"""
        try:
            selected_item = self.history_tree.selection()[0]
            values = self.history_tree.item(selected_item, 'values')
            
            # Create edit dialog
            self.show_edit_dialog(values)
            
        except IndexError:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกรายการที่ต้องการแก้ไข")
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการแก้ไข: {str(e)}")
    
    def delete_history_record(self):
        """ลบข้อมูลประวัติ"""
        try:
            selected_item = self.history_tree.selection()[0]
            values = self.history_tree.item(selected_item, 'values')
            record_id = values[0]
            barcode = values[1]
            job_type_name = values[3]  # ชื่อประเภทงานหลัก
            sub_job_type_name = values[4]  # เผื่อใช้ในอนาคต
            
            # Confirm deletion
            if messagebox.askyesno("ยืนยันการลบ", f"ต้องการลบข้อมูลบาร์โค้ด {barcode} หรือไม่?"):
                try:
                    # ดึง job_id ของเรคอร์ดที่จะลบ
                    job_query = "SELECT job_id FROM scan_logs WHERE id = ?"
                    job_results = self.db.execute_query(job_query, (record_id,))
                    if not job_results:
                        messagebox.showerror("ข้อผิดพลาด", "ไม่พบข้อมูลที่ต้องการลบ")
                        return
                    current_job_id = job_results[0]['job_id']

                    # ตรวจสอบว่ามีงานที่ตามหลัง (dependent jobs) ถูกสแกนแล้วสำหรับบาร์โค้ดนี้หรือไม่
                    # โครงสร้าง: job_dependencies(job_id, required_job_id) => งาน job_id ต้องมี required_job_id มาก่อน
                    # ดังนั้นงานที่ 'ตามหลัง' งานนี้ คือแถวที่ required_job_id = current_job_id
                    depend_query = """
                        SELECT COUNT(*) AS count
                        FROM scan_logs sl
                        WHERE sl.barcode = ? AND sl.job_id IN (
                            SELECT jd.job_id FROM job_dependencies jd WHERE jd.required_job_id = ?
                        )
                    """
                    depend_results = self.db.execute_query(depend_query, (barcode, current_job_id))
                    if depend_results and depend_results[0]['count'] > 0:
                        messagebox.showwarning(
                            "ไม่สามารถลบได้",
                            "มีงานถัดไปที่สแกนหลังจากงานนี้แล้ว จึงไม่สามารถลบได้ (มีการพึ่งพาข้อมูล)"
                        )
                        return

                    # หากไม่มีงานถัดไป ให้ลบได้ ผ่าน Service (เพื่อให้มี audit log)
                    from services.scan_service import ScanService
                    scan_service = ScanService()
                    result = scan_service.delete_scan_record(int(record_id), user_id=self.db.current_user)
                    if not result.get('success'):
                        messagebox.showerror("ข้อผิดพลาด", result.get('message', 'ไม่สามารถลบข้อมูลได้'))
                        return
                
                    # Remove from tree
                    self.history_tree.delete(selected_item)
                    messagebox.showinfo("สำเร็จ", result.get('message', 'ลบข้อมูลเรียบร้อยแล้ว'))
                except Exception as inner_e:
                    messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการลบ: {str(inner_e)}")
                
        except IndexError:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกรายการที่ต้องการลบ")
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการลบ: {str(e)}")
    
    def copy_barcode(self):
        """คัดลอกบาร์โค้ด"""
        try:
            selected_item = self.history_tree.selection()[0]
            values = self.history_tree.item(selected_item, 'values')
            barcode = values[1]
            
            # Copy to clipboard
            self.history_tree.clipboard_clear()
            self.history_tree.clipboard_append(barcode)
            
            messagebox.showinfo("สำเร็จ", f"คัดลอกบาร์โค้ด {barcode} แล้ว")
            
        except IndexError:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกรายการที่ต้องการคัดลอก")
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการคัดลอก: {str(e)}")
    
    def show_edit_dialog(self, values):
        """แสดง dialog สำหรับแก้ไขข้อมูล"""
        record_id = values[0]
        barcode = values[1]
        notes = values[5]
        
        # Create dialog window
        dialog = tk.Toplevel(self.main_app.root)
        dialog.title(f"แก้ไขข้อมูล - {barcode}")
        dialog.geometry("400x200")
        dialog.transient(self.main_app.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Content frame
        content_frame = ttk.Frame(dialog, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Barcode (readonly)
        ttk.Label(content_frame, text="บาร์โค้ด:").pack(anchor='w')
        barcode_entry = ttk.Entry(content_frame, width=50, state='readonly')
        barcode_entry.pack(fill=tk.X, pady=(0, 10))
        barcode_entry.config(state='normal')
        barcode_entry.insert(0, barcode)
        barcode_entry.config(state='readonly')
        
        # Notes
        ttk.Label(content_frame, text="หมายเหตุ:").pack(anchor='w')
        notes_var = tk.StringVar(value=notes)
        notes_entry = ttk.Entry(content_frame, textvariable=notes_var, width=50)
        notes_entry.pack(fill=tk.X, pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X)
        
        def save_changes():
            try:
                new_notes = notes_var.get().strip()
                
                # Use ScanService to update and create audit log
                from services.scan_service import ScanService
                scan_service = ScanService()
                result = scan_service.update_scan_record(
                    record_id=int(record_id),
                    notes=new_notes if new_notes else None,
                    user_id=self.db.current_user
                )
                
                if result.get('success'):
                    messagebox.showinfo("สำเร็จ", result.get('message', "บันทึกการเปลี่ยนแปลงเรียบร้อยแล้ว"))
                    dialog.destroy()
                    
                    # Refresh history
                    self.search_history()
                else:
                    messagebox.showerror("ข้อผิดพลาด", result.get('message', 'ไม่สามารถบันทึกการเปลี่ยนแปลงได้'))
                
            except Exception as e:
                messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการบันทึก: {str(e)}")
        
        def cancel_edit():
            dialog.destroy()
        
        ttk.Button(button_frame, text="บันทึกการเปลี่ยนแปลง", command=save_changes).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="ยกเลิก", command=cancel_edit).pack(side=tk.RIGHT)
        
        # Focus on notes entry
        notes_entry.focus_set()
        notes_entry.select_range(0, tk.END)