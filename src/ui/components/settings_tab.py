#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Settings Tab Component
UI component for general settings
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Callable


class SettingsTab:
    """แท็บการตั้งค่าทั่วไป"""
    
    def __init__(self, parent: ttk.Frame, db_manager, on_settings_changed: Callable = None):
        self.parent = parent
        self.db_manager = db_manager
        self.on_settings_changed = on_settings_changed
        
        self.setup_ui()
    
    def setup_ui(self):
        """สร้าง UI"""
        # สร้าง frame หลัก
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # หัวข้อ
        title_label = ttk.Label(main_frame, text="การตั้งค่าทั่วไป", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Frame สำหรับการตั้งค่า Job Types
        job_frame = ttk.LabelFrame(main_frame, text="การจัดการ Job Types")
        job_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Job Type List
        ttk.Label(job_frame, text="Job Types:").pack(anchor=tk.W, padx=5, pady=5)
        
        # Treeview สำหรับแสดง Job Types
        columns = ("ID", "Name", "Description", "Status")
        self.job_tree = ttk.Treeview(job_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.job_tree.heading(col, text=col)
            self.job_tree.column(col, width=100)
        
        self.job_tree.pack(fill=tk.X, padx=5, pady=5)
        
        # Scrollbar สำหรับ Treeview
        job_scrollbar = ttk.Scrollbar(job_frame, orient=tk.VERTICAL, command=self.job_tree.yview)
        job_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.job_tree.configure(yscrollcommand=job_scrollbar.set)
        
        # Frame สำหรับปุ่ม Job Types
        job_button_frame = ttk.Frame(job_frame)
        job_button_frame.pack(pady=10)
        
        ttk.Button(job_button_frame, text="เพิ่ม Job Type", command=self.add_job_type).pack(side=tk.LEFT, padx=5)
        ttk.Button(job_button_frame, text="แก้ไข", command=self.edit_job_type).pack(side=tk.LEFT, padx=5)
        ttk.Button(job_button_frame, text="ลบ", command=self.delete_job_type).pack(side=tk.LEFT, padx=5)
        ttk.Button(job_button_frame, text="รีเฟรช", command=self.refresh_job_types).pack(side=tk.LEFT, padx=5)
        
        # Frame สำหรับการตั้งค่า Dependencies
        dep_frame = ttk.LabelFrame(main_frame, text="การจัดการ Dependencies")
        dep_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Dependencies List
        ttk.Label(dep_frame, text="Dependencies:").pack(anchor=tk.W, padx=5, pady=5)
        
        # Treeview สำหรับแสดง Dependencies
        dep_columns = ("Job Type", "Dependent Job", "Order", "Required")
        self.dep_tree = ttk.Treeview(dep_frame, columns=dep_columns, show="headings", height=6)
        
        for col in dep_columns:
            self.dep_tree.heading(col, text=col)
            self.dep_tree.column(col, width=120)
        
        self.dep_tree.pack(fill=tk.X, padx=5, pady=5)
        
        # Scrollbar สำหรับ Dependencies Treeview
        dep_scrollbar = ttk.Scrollbar(dep_frame, orient=tk.VERTICAL, command=self.dep_tree.yview)
        dep_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.dep_tree.configure(yscrollcommand=dep_scrollbar.set)
        
        # Frame สำหรับปุ่ม Dependencies
        dep_button_frame = ttk.Frame(dep_frame)
        dep_button_frame.pack(pady=10)
        
        ttk.Button(dep_button_frame, text="เพิ่ม Dependency", command=self.add_dependency).pack(side=tk.LEFT, padx=5)
        ttk.Button(dep_button_frame, text="แก้ไข", command=self.edit_dependency).pack(side=tk.LEFT, padx=5)
        ttk.Button(dep_button_frame, text="ลบ", command=self.delete_dependency).pack(side=tk.LEFT, padx=5)
        ttk.Button(dep_button_frame, text="รีเฟรช", command=self.refresh_dependencies).pack(side=tk.LEFT, padx=5)
        
        # โหลดข้อมูลเริ่มต้น
        self.refresh_job_types()
        self.refresh_dependencies()
    
    def refresh_job_types(self):
        """รีเฟรชรายการ Job Types"""
        # ล้างข้อมูลเก่า
        for item in self.job_tree.get_children():
            self.job_tree.delete(item)
        
        try:
            # ดึงข้อมูลจากฐานข้อมูล
            query = "SELECT id, name, description, is_active FROM job_types ORDER BY name"
            results = self.db_manager.execute_query(query)
            
            for row in results:
                status = "Active" if row['is_active'] else "Inactive"
                self.job_tree.insert("", tk.END, values=(
                    row['id'], row['name'], row['description'], status
                ))
        except Exception as e:
            messagebox.showerror("ผิดพลาด", f"ไม่สามารถโหลดข้อมูล Job Types: {str(e)}")
    
    def refresh_dependencies(self):
        """รีเฟรชรายการ Dependencies"""
        # ล้างข้อมูลเก่า
        for item in self.dep_tree.get_children():
            self.dep_tree.delete(item)
        
        try:
            # ดึงข้อมูลจากฐานข้อมูล
            query = """
                SELECT j1.name as job_type, j2.name as dependent_job, 
                       d.dependency_order, d.is_required
                FROM scan_dependencies d
                JOIN job_types j1 ON d.job_type_id = j1.id
                JOIN job_types j2 ON d.dependent_job_type_id = j2.id
                ORDER BY j1.name, d.dependency_order
            """
            results = self.db_manager.execute_query(query)
            
            for row in results:
                required = "Yes" if row['is_required'] else "No"
                self.dep_tree.insert("", tk.END, values=(
                    row['job_type'], row['dependent_job'], 
                    row['dependency_order'], required
                ))
        except Exception as e:
            messagebox.showerror("ผิดพลาด", f"ไม่สามารถโหลดข้อมูล Dependencies: {str(e)}")
    
    def add_job_type(self):
        """เพิ่ม Job Type"""
        # สร้าง dialog สำหรับเพิ่ม Job Type
        dialog = tk.Toplevel(self.parent)
        dialog.title("เพิ่ม Job Type")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # สร้าง UI สำหรับ dialog
        ttk.Label(dialog, text="ชื่อ Job Type:").pack(pady=5)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.pack(pady=5)
        
        ttk.Label(dialog, text="คำอธิบาย:").pack(pady=5)
        desc_entry = ttk.Entry(dialog, width=40)
        desc_entry.pack(pady=5)
        
        active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(dialog, text="Active", variable=active_var).pack(pady=5)
        
        def save_job_type():
            name = name_entry.get().strip()
            description = desc_entry.get().strip()
            
            if not name:
                messagebox.showerror("ผิดพลาด", "กรุณากรอกชื่อ Job Type")
                return
            
            try:
                query = """
                    INSERT INTO job_types (name, description, is_active, created_by)
                    VALUES (?, ?, ?, ?)
                """
                self.db_manager.execute_non_query(query, (name, description, active_var.get(), self.db_manager.current_user))
                
                messagebox.showinfo("สำเร็จ", "เพิ่ม Job Type เรียบร้อยแล้ว")
                dialog.destroy()
                self.refresh_job_types()
                
            except Exception as e:
                messagebox.showerror("ผิดพลาด", f"ไม่สามารถเพิ่ม Job Type: {str(e)}")
        
        ttk.Button(dialog, text="บันทึก", command=save_job_type).pack(pady=10)
        ttk.Button(dialog, text="ยกเลิก", command=dialog.destroy).pack(pady=5)
    
    def edit_job_type(self):
        """แก้ไข Job Type"""
        selected = self.job_tree.selection()
        if not selected:
            messagebox.showwarning("คำเตือน", "กรุณาเลือก Job Type ที่ต้องการแก้ไข")
            return
        
        # ดึงข้อมูลที่เลือก
        item = self.job_tree.item(selected[0])
        job_id = item['values'][0]
        
        # สร้าง dialog สำหรับแก้ไข
        dialog = tk.Toplevel(self.parent)
        dialog.title("แก้ไข Job Type")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # สร้าง UI สำหรับ dialog
        ttk.Label(dialog, text="ชื่อ Job Type:").pack(pady=5)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.insert(0, item['values'][1])
        name_entry.pack(pady=5)
        
        ttk.Label(dialog, text="คำอธิบาย:").pack(pady=5)
        desc_entry = ttk.Entry(dialog, width=40)
        desc_entry.insert(0, item['values'][2])
        desc_entry.pack(pady=5)
        
        active_var = tk.BooleanVar(value=item['values'][3] == "Active")
        ttk.Checkbutton(dialog, text="Active", variable=active_var).pack(pady=5)
        
        def save_changes():
            name = name_entry.get().strip()
            description = desc_entry.get().strip()
            
            if not name:
                messagebox.showerror("ผิดพลาด", "กรุณากรอกชื่อ Job Type")
                return
            
            try:
                query = """
                    UPDATE job_types 
                    SET name = ?, description = ?, is_active = ?, modified_by = ?
                    WHERE id = ?
                """
                self.db_manager.execute_non_query(query, (name, description, active_var.get(), self.db_manager.current_user, job_id))
                
                messagebox.showinfo("สำเร็จ", "แก้ไข Job Type เรียบร้อยแล้ว")
                dialog.destroy()
                self.refresh_job_types()
                
            except Exception as e:
                messagebox.showerror("ผิดพลาด", f"ไม่สามารถแก้ไข Job Type: {str(e)}")
        
        ttk.Button(dialog, text="บันทึก", command=save_changes).pack(pady=10)
        ttk.Button(dialog, text="ยกเลิก", command=dialog.destroy).pack(pady=5)
    
    def delete_job_type(self):
        """ลบ Job Type"""
        selected = self.job_tree.selection()
        if not selected:
            messagebox.showwarning("คำเตือน", "กรุณาเลือก Job Type ที่ต้องการลบ")
            return
        
        item = self.job_tree.item(selected[0])
        job_id = item['values'][0]
        job_name = item['values'][1]
        
        if messagebox.askyesno("ยืนยัน", f"คุณต้องการลบ Job Type '{job_name}' หรือไม่?"):
            try:
                query = "DELETE FROM job_types WHERE id = ?"
                self.db_manager.execute_non_query(query, (job_id,))
                
                messagebox.showinfo("สำเร็จ", "ลบ Job Type เรียบร้อยแล้ว")
                self.refresh_job_types()
                
            except Exception as e:
                messagebox.showerror("ผิดพลาด", f"ไม่สามารถลบ Job Type: {str(e)}")
    
    def add_dependency(self):
        """เพิ่ม Dependency"""
        messagebox.showinfo("ข้อมูล", "ฟีเจอร์นี้จะถูกเพิ่มในอนาคต")
    
    def edit_dependency(self):
        """แก้ไข Dependency"""
        messagebox.showinfo("ข้อมูล", "ฟีเจอร์นี้จะถูกเพิ่มในอนาคต")
    
    def delete_dependency(self):
        """ลบ Dependency"""
        messagebox.showinfo("ข้อมูล", "ฟีเจอร์นี้จะถูกเพิ่มในอนาคต") 