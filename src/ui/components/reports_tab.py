#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reports Tab Component
UI component for generating and exporting reports
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, Callable, Optional
from datetime import datetime, date
import pandas as pd
from ..tabs.base_tab import BaseTab


class ReportsTab(BaseTab):
    """แท็บรายงาน"""

    def __init__(
        self,
        parent: tk.Widget,
        db_manager: Any,
        repositories: Dict[str, Any],
        services: Dict[str, Any],
        on_report_generated: Optional[Callable] = None
    ):
        self.on_report_generated = on_report_generated
        self.current_report_data = []
        self.current_report_summary = {}
        self.report_job_types_data = {}
        self.report_sub_job_types_data = {}
        super().__init__(parent, db_manager, repositories, services)
        self.refresh_job_types()

    def build_ui(self):
        """สร้าง UI"""
        # Use the frame provided by BaseTab
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # หัวข้อ
        title_label = ttk.Label(main_frame, text="รายงาน", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))

        # Filter selection frame
        filter_frame = ttk.LabelFrame(main_frame, text="เลือกเงื่อนไขรายงาน", padding=10)
        filter_frame.pack(fill=tk.X, pady=(0, 20))

        # Date selection
        date_frame = ttk.Frame(filter_frame)
        date_frame.pack(fill=tk.X, pady=5)
        ttk.Label(date_frame, text="วันที่:").pack(side=tk.LEFT)
        self.report_date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        report_date_entry = ttk.Entry(date_frame, textvariable=self.report_date_var, width=15)
        report_date_entry.pack(side=tk.LEFT, padx=10)

        # Job Type selection
        job_type_frame = ttk.Frame(filter_frame)
        job_type_frame.pack(fill=tk.X, pady=5)
        ttk.Label(job_type_frame, text="งานหลัก:").pack(side=tk.LEFT)
        self.report_job_type_var = tk.StringVar()
        self.report_job_type_combo = ttk.Combobox(
            job_type_frame,
            textvariable=self.report_job_type_var,
            state="readonly",
            width=30
        )
        self.report_job_type_combo.pack(side=tk.LEFT, padx=10)
        self.report_job_type_combo.bind("<<ComboboxSelected>>", self.on_job_type_change)

        # Sub Job Type selection
        sub_job_type_frame = ttk.Frame(filter_frame)
        sub_job_type_frame.pack(fill=tk.X, pady=5)
        ttk.Label(sub_job_type_frame, text="งานรอง:").pack(side=tk.LEFT)
        self.report_sub_job_type_var = tk.StringVar()
        self.report_sub_job_type_combo = ttk.Combobox(
            sub_job_type_frame,
            textvariable=self.report_sub_job_type_var,
            state="readonly",
            width=30
        )
        self.report_sub_job_type_combo.pack(side=tk.LEFT, padx=10)

        # Note filter
        note_filter_frame = ttk.Frame(filter_frame)
        note_filter_frame.pack(fill=tk.X, pady=5)
        ttk.Label(note_filter_frame, text="กรองหมายเหตุ:").pack(side=tk.LEFT)
        self.report_note_filter_var = tk.StringVar()
        note_filter_entry = ttk.Entry(note_filter_frame, textvariable=self.report_note_filter_var, width=40)
        note_filter_entry.pack(side=tk.LEFT, padx=10)

        # Run buttons
        button_frame = ttk.Frame(filter_frame)
        button_frame.pack(fill=tk.X, pady=10)
        ttk.Button(button_frame, text="ดูรายงาน", command=self.run_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="ส่งออก Excel", command=self.export_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="ล้างข้อมูล", command=self.clear_report).pack(side=tk.LEFT, padx=5)

        # Results table
        self.create_report_table(main_frame)

    def create_report_table(self, parent):
        """Create table for report display"""
        table_frame = ttk.LabelFrame(parent, text="ผลลัพธ์รายงาน")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Dynamic treeview (columns will be set when data loads)
        self.report_tree = ttk.Treeview(table_frame, show='headings', height=20)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.report_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.report_tree.xview)
        self.report_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack
        self.report_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    def refresh_job_types(self):
        """Refresh job types for report selection"""
        try:
            # Use JobTypeRepository to get all job types
            results = self.job_type_repo.get_all_job_types()

            job_types = ["ทั้งหมด"] + [f"{row['id']} - {row['name']}" for row in results]
            self.report_job_type_combo['values'] = job_types

            # Store job types data for easier access
            self.report_job_types_data = {f"{row['id']} - {row['name']}": row['id'] for row in results}
            self.report_job_types_data["ทั้งหมด"] = None

        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถโหลดรายการงานหลักได้: {str(e)}")

    def on_job_type_change(self, event=None):
        """Handle job type change in report"""
        selected_job_type = self.report_job_type_var.get()
        job_type_id = self.report_job_types_data.get(selected_job_type)

        # Clear sub job type selection
        self.report_sub_job_type_var.set("")
        self.report_sub_job_type_combo['values'] = []

        if job_type_id:
            try:
                # Use SubJobRepository to get sub jobs for selected job type
                results = self.sub_job_repo.get_by_main_job(job_type_id, active_only=True)

                sub_job_types = ["ทั้งหมด"] + [f"{row['id']} - {row['name']}" for row in results]
                self.report_sub_job_type_combo['values'] = sub_job_types

                # Store sub job types data
                self.report_sub_job_types_data = {f"{row['id']} - {row['name']}": row['id'] for row in results}
                self.report_sub_job_types_data["ทั้งหมด"] = None

            except Exception as e:
                messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถโหลดรายการงานรองได้: {str(e)}")
        else:
            # If "ทั้งหมด" is selected, load all sub job types
            try:
                # Use SubJobRepository to get all active sub jobs
                results = self.sub_job_repo.get_all_active()

                sub_job_types = ["ทั้งหมด"] + [f"{row['id']} - {row['name']}" for row in results]
                self.report_sub_job_type_combo['values'] = sub_job_types

                self.report_sub_job_types_data = {f"{row['id']} - {row['name']}": row['id'] for row in results}
                self.report_sub_job_types_data["ทั้งหมด"] = None

            except Exception as e:
                self.report_sub_job_types_data = {"ทั้งหมด": None}

    def run_report(self):
        """Generate report using ReportService"""
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
            if job_type_id is None and selected_job_type != "ทั้งหมด":
                messagebox.showerror("ข้อผิดพลาด", "ไม่พบงานหลักที่เลือก")
                return

            sub_job_type_id = None
            if selected_sub_job_type and hasattr(self, 'report_sub_job_types_data'):
                sub_job_type_id = self.report_sub_job_types_data.get(selected_sub_job_type)

            # Use ReportService to generate report (handles all business logic and SQL)
            result = self.report_service.generate_report(
                report_date=report_date,
                job_id=job_type_id,
                sub_job_id=sub_job_type_id,
                notes_filter=note_filter if note_filter else None
            )

            # Handle the result
            if not result['success']:
                messagebox.showerror("ข้อผิดพลาด", result['message'])
                self.clear_table()
                return

            # Get report data from result
            report_data = result['data']
            results = report_data['scans']
            statistics = report_data['statistics']

            # Store data for export
            self.current_report_data = results
            self.current_report_summary = {
                'report_date': report_date,
                'job_type_name': selected_job_type,
                'sub_job_type_name': selected_sub_job_type or 'ทั้งหมด',
                'note_filter': note_filter if note_filter else None,
                'total_count': statistics['total_scans'],
                'unique_barcodes': statistics['unique_barcodes'],
                'generated_at': datetime.now().isoformat()
            }

            if not results:
                messagebox.showinfo("ผลลัพธ์", "ไม่พบข้อมูลในวันที่ที่เลือก")
                self.clear_table()
                return

            # Display results
            self.display_report(results)

            messagebox.showinfo(
                "สำเร็จ",
                f"รันรายงานสำเร็จ พบข้อมูล {statistics['total_scans']} รายการ "
                f"(บาร์โค้ดที่ไม่ซ้ำ: {statistics['unique_barcodes']})"
            )

            # Call callback
            if self.on_report_generated:
                self.on_report_generated()

        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถรันรายงานได้: {str(e)}")

    def display_report(self, results: list):
        """Display report results in table"""
        # Clear existing data
        self.clear_table()

        # Setup columns
        columns = ['barcode', 'scan_date', 'job_type_name', 'sub_job_type_name', 'user_id', 'notes']
        self.report_tree['columns'] = columns
        self.report_tree['show'] = 'headings'

        # Configure column headings and widths
        column_widths = {
            'barcode': 150,
            'scan_date': 150,
            'job_type_name': 120,
            'sub_job_type_name': 120,
            'user_id': 100,
            'notes': 200
        }

        column_names = {
            'barcode': 'บาร์โค้ด',
            'scan_date': 'วันที่/เวลา',
            'job_type_name': 'งานหลัก',
            'sub_job_type_name': 'งานรอง',
            'user_id': 'ผู้ใช้',
            'notes': 'หมายเหตุ'
        }

        for col in columns:
            self.report_tree.heading(col, text=column_names.get(col, col))
            self.report_tree.column(col, width=column_widths.get(col, 120))

        # Populate data
        for row in results:
            values = []
            for col in columns:
                value = row.get(col, "")
                if col == 'scan_date' and value:
                    # Format datetime
                    if isinstance(value, datetime):
                        value = value.strftime("%Y-%m-%d %H:%M:%S")
                values.append(str(value) if value is not None else "")
            self.report_tree.insert('', tk.END, values=values)

    def clear_table(self):
        """Clear all items from the report table"""
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)

    def clear_report(self):
        """Clear report data and filters"""
        if messagebox.askyesno("ยืนยัน", "คุณต้องการล้างข้อมูลรายงานหรือไม่?"):
            self.clear_table()
            self.current_report_data = []
            self.current_report_summary = {}
            self.report_date_var.set(date.today().strftime("%Y-%m-%d"))
            self.report_job_type_var.set("")
            self.report_sub_job_type_var.set("")
            self.report_note_filter_var.set("")

    def export_report(self):
        """Export current report data to Excel with summary"""
        if not self.current_report_data:
            messagebox.showwarning("คำเตือน", "ไม่มีข้อมูลสำหรับส่งออก กรุณารันรายงานก่อน")
            return

        try:
            # Create filename with current date
            today = date.today().strftime("%Y%m%d")
            default_filename = f"รายงาน_{today}.xlsx"

            # Ask user for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=default_filename
            )

            if filename:
                # Create Excel workbook with multiple sheets
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:

                    # Summary sheet
                    if self.current_report_summary:
                        summary_data = {
                            'รายการ': [
                                'วันที่รายงาน',
                                'งานหลัก',
                                'งานรอง',
                                'กรองหมายเหตุ',
                                'จำนวนรวม',
                                'บาร์โค้ดไม่ซ้ำ',
                                'วันที่สร้างรายงาน'
                            ],
                            'ค่า': [
                                self.current_report_summary.get('report_date', ''),
                                self.current_report_summary.get('job_type_name', ''),
                                self.current_report_summary.get('sub_job_type_name', ''),
                                self.current_report_summary.get('note_filter', 'ไม่มี') or 'ไม่มี',
                                self.current_report_summary.get('total_count', 0),
                                self.current_report_summary.get('unique_barcodes', 0),
                                datetime.fromisoformat(
                                    self.current_report_summary.get('generated_at', '')
                                ).strftime('%Y-%m-%d %H:%M:%S') if self.current_report_summary.get('generated_at') else ''
                            ]
                        }
                        summary_df = pd.DataFrame(summary_data)
                        summary_df.to_excel(writer, sheet_name='สรุป', index=False)

                    # Detail data sheet
                    df = pd.DataFrame(self.current_report_data)
                    if not df.empty:
                        # Rename columns to Thai
                        column_mapping = {
                            'barcode': 'บาร์โค้ด',
                            'scan_date': 'วันที่/เวลา',
                            'job_type_name': 'งานหลัก',
                            'sub_job_type_name': 'งานรอง',
                            'user_id': 'ผู้ใช้',
                            'notes': 'หมายเหตุ'
                        }

                        # Rename only existing columns
                        df_columns = {col: column_mapping.get(col, col) for col in df.columns if col in column_mapping}
                        df = df.rename(columns=df_columns)

                        # Format datetime columns
                        for col in df.columns:
                            if df[col].dtype == 'datetime64[ns]' or 'date' in col.lower():
                                df[col] = pd.to_datetime(df[col], errors='ignore').dt.strftime('%Y-%m-%d %H:%M:%S')

                        df.to_excel(writer, sheet_name='รายละเอียด', index=False)

                messagebox.showinfo(
                    "สำเร็จ",
                    f"ส่งออกไฟล์สำเร็จ\n{filename}\n\n"
                    f"ประกอบด้วย:\n- แผ่นสรุป: ข้อมูลสรุปรายงาน\n- แผ่นรายละเอียด: ข้อมูลทั้งหมด"
                )

        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถส่งออกไฟล์ได้: {str(e)}")
