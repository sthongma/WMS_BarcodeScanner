#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import Tab Component
UI component for data import
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, Callable, List, Optional
import pandas as pd
from ..tabs.base_tab import BaseTab


class ImportTab(BaseTab):
    """แท็บการนำเข้าข้อมูล"""

    def __init__(
        self,
        parent: tk.Widget,
        db_manager: Any,
        repositories: Dict[str, Any],
        services: Dict[str, Any],
        on_import_completed: Optional[Callable] = None
    ):
        self.on_import_completed = on_import_completed
        self.import_data = None
        super().__init__(parent, db_manager, repositories, services)

    def build_ui(self):
        """สร้าง UI"""
        # Use the frame provided by BaseTab
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # หัวข้อ
        title_label = ttk.Label(main_frame, text="นำเข้าข้อมูล", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Frame สำหรับการเลือกไฟล์
        file_frame = ttk.LabelFrame(main_frame, text="เลือกไฟล์")
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        # ปุ่มเลือกไฟล์
        ttk.Button(file_frame, text="เลือกไฟล์ Excel/CSV", command=self.select_file).pack(side=tk.LEFT, padx=5, pady=10)
        
        # ปุ่มดาวน์โหลด template
        ttk.Button(file_frame, text="ดาวน์โหลด Template", command=self.download_template).pack(side=tk.LEFT, padx=5, pady=10)
        
        # แสดงชื่อไฟล์ที่เลือก
        self.file_label = ttk.Label(file_frame, text="ยังไม่ได้เลือกไฟล์")
        self.file_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Frame สำหรับการตรวจสอบข้อมูล
        preview_frame = ttk.LabelFrame(main_frame, text="ตรวจสอบข้อมูล")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Treeview สำหรับแสดงข้อมูล
        columns = ("แถว", "Barcode", "Job Type", "Sub Job Type", "หมายเหตุ", "สถานะ")
        self.preview_tree = ttk.Treeview(preview_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.preview_tree.heading(col, text=col)
            self.preview_tree.column(col, width=120)
        
        self.preview_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar สำหรับ Treeview
        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_tree.configure(yscrollcommand=scrollbar.set)
        
        # Frame สำหรับปุ่ม
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="ตรวจสอบข้อมูล", command=self.validate_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="นำเข้าข้อมูล", command=self.import_data_to_db).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="ล้างข้อมูล", command=self.clear_data).pack(side=tk.LEFT, padx=5)
    
    def select_file(self):
        """เลือกไฟล์"""
        file_path = filedialog.askopenfilename(
            title="เลือกไฟล์ Excel/CSV",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            self.file_label.config(text=f"ไฟล์: {file_path}")
            self.load_file(file_path)
    
    def load_file(self, file_path: str):
        """โหลดไฟล์"""
        try:
            # Read Excel or CSV file using pandas
            if file_path.endswith('.csv'):
                self.import_data = pd.read_csv(file_path)
            else:
                self.import_data = pd.read_excel(file_path)

            if self.import_data is not None and not self.import_data.empty:
                self.display_preview()
            else:
                messagebox.showerror("ผิดพลาด", "ไม่สามารถอ่านไฟล์ได้หรือไฟล์ว่างเปล่า")

        except Exception as e:
            messagebox.showerror("ผิดพลาด", f"เกิดข้อผิดพลาดในการโหลดไฟล์: {str(e)}")
    
    def display_preview(self):
        """แสดงตัวอย่างข้อมูล"""
        # ล้างข้อมูลเก่า
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        
        if self.import_data is None or self.import_data.empty:
            return
        
        # แสดงข้อมูล 20 แถวแรก
        preview_data = self.import_data.head(20)
        
        for index, row in preview_data.iterrows():
            barcode = str(row.get('barcode', '')) if pd.notna(row.get('barcode')) else ''
            job_type = str(row.get('job_type', '')) if pd.notna(row.get('job_type')) else ''
            sub_job_type = str(row.get('sub_job_type', '')) if pd.notna(row.get('sub_job_type')) else ''
            notes = str(row.get('notes', '')) if pd.notna(row.get('notes')) else ''
            
            self.preview_tree.insert("", tk.END, values=(
                index + 1, barcode, job_type, sub_job_type, notes, "รอตรวจสอบ"
            ))
    
    def download_template(self):
        """ดาวน์โหลด template"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="บันทึก Template",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")]
            )

            if file_path:
                # Use ImportService to generate template data
                template_info = self.import_service.generate_template_data()

                # Create DataFrame with sample data
                df = pd.DataFrame(template_info['sample_data'], columns=template_info['columns'])

                # Save to Excel
                df.to_excel(file_path, index=False, sheet_name='Template')
                messagebox.showinfo("สำเร็จ", f"บันทึก template เรียบร้อยแล้วที่: {file_path}")

        except Exception as e:
            messagebox.showerror("ผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")
    
    def validate_data(self):
        """ตรวจสอบข้อมูล"""
        if self.import_data is None or self.import_data.empty:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกไฟล์ก่อน")
            return

        try:
            # Convert DataFrame to list of dicts for ImportService
            data_list = self.import_data.to_dict('records')

            # Use ImportService to validate
            result = self.import_service.validate_import_data(data_list)

            if result['success']:
                valid_count = result['data']['valid_count']
                invalid_count = result['data']['invalid_count']

                if invalid_count == 0:
                    messagebox.showinfo("สำเร็จ", f"ข้อมูลถูกต้องทั้งหมด ({valid_count} รายการ)")
                    self.update_preview_status("ผ่าน")
                else:
                    # Show errors
                    errors = [r['error'] for r in result['data']['results'] if not r['valid']]
                    error_message = "\n".join(errors[:10])  # Show first 10 errors
                    if len(errors) > 10:
                        error_message += f"\n... และอีก {len(errors) - 10} ข้อผิดพลาด"

                    messagebox.showerror("ข้อผิดพลาด",
                        f"พบข้อผิดพลาดในข้อมูล:\nถูกต้อง: {valid_count} | ผิดพลาด: {invalid_count}\n\n{error_message}")
                    self.update_preview_status("ไม่ผ่าน")
            else:
                messagebox.showerror("ผิดพลาด", result['message'])

        except Exception as e:
            messagebox.showerror("ผิดพลาด", f"เกิดข้อผิดพลาดในการตรวจสอบ: {str(e)}")
    
    def update_preview_status(self, status: str):
        """อัปเดตสถานะใน preview"""
        for item in self.preview_tree.get_children():
            values = list(self.preview_tree.item(item)['values'])
            values[-1] = status
            self.preview_tree.item(item, values=values)
    
    def import_data_to_db(self):
        """นำเข้าข้อมูลลงฐานข้อมูล"""
        if self.import_data is None or self.import_data.empty:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกไฟล์ก่อน")
            return

        if not messagebox.askyesno("ยืนยัน", "คุณต้องการนำเข้าข้อมูลหรือไม่?"):
            return

        try:
            # Convert DataFrame to list of dicts
            data_list = self.import_data.to_dict('records')

            # Use ImportService to import scans
            result = self.import_service.import_scans(data_list)

            if result['success']:
                success_count = result['data']['success_count']
                error_count = result['data']['error_count']

                messagebox.showinfo("เสร็จสิ้น",
                    f"นำเข้าข้อมูลเสร็จสิ้น\nสำเร็จ: {success_count} รายการ\nผิดพลาด: {error_count} รายการ")

                # Call callback
                if self.on_import_completed:
                    self.on_import_completed()
            else:
                messagebox.showerror("ผิดพลาด", result['message'])

        except Exception as e:
            messagebox.showerror("ผิดพลาด", f"เกิดข้อผิดพลาดในการนำเข้าข้อมูล: {str(e)}")
    
    def clear_data(self):
        """ล้างข้อมูล"""
        if messagebox.askyesno("ยืนยัน", "คุณต้องการล้างข้อมูลหรือไม่?"):
            self.import_data = None
            self.file_label.config(text="ยังไม่ได้เลือกไฟล์")
            
            # ล้าง preview
            for item in self.preview_tree.get_children():
                self.preview_tree.delete(item) 