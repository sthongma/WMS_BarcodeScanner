#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
History Tab Component
UI component for scan history
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, Callable
from datetime import datetime, timedelta


class HistoryTab:
    """แท็บประวัติการสแกน"""
    
    def __init__(self, parent: ttk.Frame, db_manager, on_history_updated: Callable = None):
        self.parent = parent
        self.db_manager = db_manager
        self.on_history_updated = on_history_updated
        
        self.setup_ui()
        self.refresh_history()
    
    def setup_ui(self):
        """สร้าง UI"""
        # สร้าง frame หลัก
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # หัวข้อ
        title_label = ttk.Label(main_frame, text="ประวัติการสแกน", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Frame สำหรับตัวกรอง
        filter_frame = ttk.LabelFrame(main_frame, text="ตัวกรอง")
        filter_frame.pack(fill=tk.X, pady=(0, 20))
        
        # วันที่เริ่มต้น
        ttk.Label(filter_frame, text="วันที่เริ่มต้น:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.start_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"))
        start_date_entry = ttk.Entry(filter_frame, textvariable=self.start_date_var, width=15)
        start_date_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # วันที่สิ้นสุด
        ttk.Label(filter_frame, text="วันที่สิ้นสุด:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.end_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        end_date_entry = ttk.Entry(filter_frame, textvariable=self.end_date_var, width=15)
        end_date_entry.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Job Type
        ttk.Label(filter_frame, text="Job Type:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.job_type_var = tk.StringVar()
        self.job_type_combo = ttk.Combobox(filter_frame, textvariable=self.job_type_var, 
                                          state="readonly", width=20)
        self.job_type_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Barcode
        ttk.Label(filter_frame, text="Barcode:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.barcode_var = tk.StringVar()
        barcode_entry = ttk.Entry(filter_frame, textvariable=self.barcode_var, width=20)
        barcode_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        
        # ปุ่มค้นหา
        ttk.Button(filter_frame, text="ค้นหา", command=self.search_history).grid(row=1, column=4, padx=5, pady=5)
        ttk.Button(filter_frame, text="ล้างตัวกรอง", command=self.clear_filters).grid(row=1, column=5, padx=5, pady=5)
        
        # Frame สำหรับตารางประวัติ
        history_frame = ttk.LabelFrame(main_frame, text="ประวัติการสแกน")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Treeview สำหรับประวัติ
        columns = ("ID", "วันที่สแกน", "Barcode", "Job Type", "Sub Job Type", "ผู้สแกน", "สถานะ", "หมายเหตุ")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=120)
        
        self.history_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar สำหรับ Treeview
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Context menu สำหรับตาราง
        self.context_menu = tk.Menu(self.parent, tearoff=0)
        self.context_menu.add_command(label="แก้ไข", command=self.edit_record)
        self.context_menu.add_command(label="ลบ", command=self.delete_record)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="ส่งออก", command=self.export_history)
        
        self.history_tree.bind("<Button-3>", self.show_context_menu)
        
        # Frame สำหรับปุ่ม
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="รีเฟรช", command=self.refresh_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="ส่งออก Excel", command=self.export_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="สถิติ", command=self.show_statistics).pack(side=tk.LEFT, padx=5)
        
        # โหลด Job Types
        self.load_job_types()
    
    def load_job_types(self):
        """โหลดรายการ Job Types"""
        try:
            query = "SELECT id, name FROM job_types WHERE is_active = 1 ORDER BY name"
            results = self.db_manager.execute_query(query)
            
            job_types = ["ทั้งหมด"] + [row['name'] for row in results]
            self.job_type_combo['values'] = job_types
            self.job_type_combo.set("ทั้งหมด")
            
        except Exception as e:
            messagebox.showerror("ผิดพลาด", f"ไม่สามารถโหลด Job Types: {str(e)}")
    
    def search_history(self):
        """ค้นหาประวัติ"""
        try:
            # สร้างเงื่อนไขการค้นหา
            conditions = []
            params = []
            
            # วันที่
            start_date = self.start_date_var.get()
            end_date = self.end_date_var.get()
            
            if start_date and end_date:
                conditions.append("CAST(s.scan_date AS DATE) BETWEEN ? AND ?")
                params.extend([start_date, end_date])
            
            # Job Type
            job_type = self.job_type_var.get()
            if job_type and job_type != "ทั้งหมด":
                conditions.append("j.name = ?")
                params.append(job_type)
            
            # Barcode
            barcode = self.barcode_var.get().strip()
            if barcode:
                conditions.append("s.barcode LIKE ?")
                params.append(f"%{barcode}%")
            
            # สร้าง query
            query = """
                SELECT s.*, j.name as job_type_name, sj.name as sub_job_type_name
                FROM scan_logs s
                JOIN job_types j ON s.job_type_id = j.id
                LEFT JOIN sub_job_types sj ON s.sub_job_type_id = sj.id
            """
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY s.scan_date DESC"
            
            # ดึงข้อมูล
            results = self.db_manager.execute_query(query, tuple(params))
            self.display_history(results)
            
        except Exception as e:
            messagebox.showerror("ผิดพลาด", f"เกิดข้อผิดพลาดในการค้นหา: {str(e)}")
    
    def refresh_history(self):
        """รีเฟรชประวัติ"""
        self.search_history()
    
    def clear_filters(self):
        """ล้างตัวกรอง"""
        self.start_date_var.set((datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"))
        self.end_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.job_type_var.set("ทั้งหมด")
        self.barcode_var.set("")
        self.refresh_history()
    
    def display_history(self, results: list):
        """แสดงประวัติในตาราง"""
        # ล้างข้อมูลเก่า
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        for row in results:
            scan_date = row['scan_date'].strftime("%Y-%m-%d %H:%M:%S") if row['scan_date'] else ""
            sub_job_type = row['sub_job_type_name'] or ""
            status = "สำเร็จ" if row['status'] == 'Active' else row['status']
            notes = row['notes'] or ""
            
            self.history_tree.insert("", tk.END, values=(
                row['id'], scan_date, row['barcode'], row['job_type_name'], 
                sub_job_type, row['scanned_by'], status, notes
            ))
    
    def show_context_menu(self, event):
        """แสดง context menu"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def edit_record(self):
        """แก้ไขรายการ"""
        selected = self.history_tree.selection()
        if not selected:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกรายการที่ต้องการแก้ไข")
            return
        
        # ดึงข้อมูลที่เลือก
        item = self.history_tree.item(selected[0])
        record_id = item['values'][0]
        
        # สร้าง dialog สำหรับแก้ไข
        self.show_edit_dialog(record_id, item['values'])
    
    def show_edit_dialog(self, record_id: int, current_values: tuple):
        """แสดง dialog สำหรับแก้ไข"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("แก้ไขรายการสแกน")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # สร้าง UI สำหรับ dialog
        ttk.Label(dialog, text="Barcode:").pack(pady=5)
        barcode_entry = ttk.Entry(dialog, width=40)
        barcode_entry.insert(0, current_values[2])
        barcode_entry.pack(pady=5)
        
        ttk.Label(dialog, text="หมายเหตุ:").pack(pady=5)
        notes_entry = ttk.Entry(dialog, width=40)
        notes_entry.insert(0, current_values[7])
        notes_entry.pack(pady=5)
        
        def save_changes():
            barcode = barcode_entry.get().strip()
            notes = notes_entry.get().strip()
            
            if not barcode:
                messagebox.showerror("ผิดพลาด", "กรุณากรอก Barcode")
                return
            
            try:
                query = "UPDATE scan_logs SET barcode = ?, notes = ? WHERE id = ?"
                self.db_manager.execute_non_query(query, (barcode, notes, record_id))
                
                messagebox.showinfo("สำเร็จ", "แก้ไขรายการเรียบร้อยแล้ว")
                dialog.destroy()
                self.refresh_history()
                
            except Exception as e:
                messagebox.showerror("ผิดพลาด", f"ไม่สามารถแก้ไขรายการ: {str(e)}")
        
        ttk.Button(dialog, text="บันทึก", command=save_changes).pack(pady=10)
        ttk.Button(dialog, text="ยกเลิก", command=dialog.destroy).pack(pady=5)
    
    def delete_record(self):
        """ลบรายการ"""
        selected = self.history_tree.selection()
        if not selected:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกรายการที่ต้องการลบ")
            return
        
        item = self.history_tree.item(selected[0])
        record_id = item['values'][0]
        barcode = item['values'][2]
        
        if messagebox.askyesno("ยืนยัน", f"คุณต้องการลบรายการ Barcode: {barcode} หรือไม่?"):
            try:
                query = "DELETE FROM scan_logs WHERE id = ?"
                self.db_manager.execute_non_query(query, (record_id,))
                
                messagebox.showinfo("สำเร็จ", "ลบรายการเรียบร้อยแล้ว")
                self.refresh_history()
                
            except Exception as e:
                messagebox.showerror("ผิดพลาด", f"ไม่สามารถลบรายการ: {str(e)}")
    
    def export_history(self):
        """ส่งออกประวัติ"""
        try:
            # ดึงข้อมูลทั้งหมดที่แสดงอยู่
            data = []
            for item in self.history_tree.get_children():
                values = self.history_tree.item(item)['values']
                data.append({
                    'ID': values[0],
                    'วันที่สแกน': values[1],
                    'Barcode': values[2],
                    'Job Type': values[3],
                    'Sub Job Type': values[4],
                    'ผู้สแกน': values[5],
                    'สถานะ': values[6],
                    'หมายเหตุ': values[7]
                })
            
            if not data:
                messagebox.showwarning("คำเตือน", "ไม่มีข้อมูลให้ส่งออก")
                return
            
            # เลือกตำแหน่งบันทึกไฟล์
            file_path = filedialog.asksaveasfilename(
                title="บันทึกไฟล์ Excel",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")]
            )
            
            if file_path:
                from utils.file_utils import export_to_excel
                if export_to_excel(data, file_path, "ประวัติการสแกน"):
                    messagebox.showinfo("สำเร็จ", f"ส่งออกไฟล์เรียบร้อยแล้วที่: {file_path}")
                else:
                    messagebox.showerror("ผิดพลาด", "ไม่สามารถส่งออกไฟล์ได้")
                    
        except Exception as e:
            messagebox.showerror("ผิดพลาด", f"เกิดข้อผิดพลาดในการส่งออก: {str(e)}")
    
    def show_statistics(self):
        """แสดงสถิติ"""
        try:
            # ดึงสถิติจากฐานข้อมูล
            query = """
                SELECT 
                    COUNT(*) as total_scans,
                    COUNT(DISTINCT s.barcode) as unique_barcodes,
                    COUNT(DISTINCT s.scanned_by) as unique_users,
                    j.name as job_type,
                    COUNT(*) as job_count
                FROM scan_logs s
                JOIN job_types j ON s.job_type_id = j.id
                WHERE s.status = 'Active'
                GROUP BY j.name
                ORDER BY job_count DESC
            """
            results = self.db_manager.execute_query(query)
            
            # สร้าง dialog แสดงสถิติ
            dialog = tk.Toplevel(self.parent)
            dialog.title("สถิติการสแกน")
            dialog.geometry("500x400")
            dialog.transient(self.parent)
            dialog.grab_set()
            
            # สร้าง UI สำหรับ dialog
            ttk.Label(dialog, text="สถิติการสแกน", font=("Arial", 12, "bold")).pack(pady=10)
            
            # สร้าง Treeview สำหรับแสดงสถิติ
            columns = ("Job Type", "จำนวนการสแกน")
            stats_tree = ttk.Treeview(dialog, columns=columns, show="headings", height=10)
            
            for col in columns:
                stats_tree.heading(col, text=col)
                stats_tree.column(col, width=200)
            
            stats_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # เพิ่มข้อมูลสถิติ
            for row in results:
                stats_tree.insert("", tk.END, values=(
                    row['job_type'], row['job_count']
                ))
            
            ttk.Button(dialog, text="ปิด", command=dialog.destroy).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("ผิดพลาด", f"เกิดข้อผิดพลาดในการดึงสถิติ: {str(e)}") 