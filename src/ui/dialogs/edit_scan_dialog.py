#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edit Scan Dialog
Dialog for editing scan record information
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Callable, Optional, List, Tuple


class EditScanDialog:
    """
    Dialog for editing scan record

    Allows editing of barcode, job types, and notes for an existing scan record.
    Dynamically updates sub job list when main job is changed.
    """

    def __init__(
        self,
        parent: tk.Widget,
        job_types_data: Dict[str, int],
        sub_job_repo: Any,
        scan_log_repo: Any,
        record_id: int,
        current_values: Tuple,
        on_save_callback: Optional[Callable] = None
    ):
        """
        Initialize edit scan dialog

        Args:
            parent: Parent window
            job_types_data: Dictionary mapping job type names to IDs
            sub_job_repo: SubJobRepository for loading sub jobs
            scan_log_repo: ScanLogRepository for updating records
            record_id: ID of the scan record being edited
            current_values: Tuple with current values:
                (id, barcode, scan_date, main_job_name, sub_job_name, notes, user_id)
            on_save_callback: Optional callback to execute after successful save
        """
        self.parent = parent
        self.job_types_data = job_types_data
        self.sub_job_repo = sub_job_repo
        self.scan_log_repo = scan_log_repo
        self.record_id = record_id
        self.current_values = current_values
        self.on_save_callback = on_save_callback

        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("แก้ไขข้อมูลการสแกน")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self.center_dialog()

        # Variables for combo boxes
        self.main_job_var = tk.StringVar()
        self.sub_job_var = tk.StringVar()

        # Sub job data cache
        self.sub_job_types_data = {}

        # Build UI
        self.build_ui()

    def center_dialog(self):
        """Center dialog relative to parent window"""
        self.dialog.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 100,
            self.parent.winfo_rooty() + 100
        ))

    def build_ui(self):
        """Build dialog UI"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ID (readonly)
        id_frame = ttk.Frame(main_frame)
        id_frame.pack(fill=tk.X, pady=5)
        ttk.Label(id_frame, text="ID:", width=15).pack(side=tk.LEFT)
        id_entry = ttk.Entry(id_frame, width=20, state="readonly")
        id_entry.pack(side=tk.LEFT, padx=10)
        id_entry.config(state="normal")
        id_entry.insert(0, self.current_values[0])
        id_entry.config(state="readonly")

        # Barcode
        barcode_frame = ttk.Frame(main_frame)
        barcode_frame.pack(fill=tk.X, pady=5)
        ttk.Label(barcode_frame, text="บาร์โค้ด:", width=15).pack(side=tk.LEFT)
        self.barcode_entry = ttk.Entry(barcode_frame, width=30)
        self.barcode_entry.pack(side=tk.LEFT, padx=10)
        self.barcode_entry.insert(0, self.current_values[1])

        # Scan date (readonly - informative)
        date_frame = ttk.Frame(main_frame)
        date_frame.pack(fill=tk.X, pady=5)
        ttk.Label(date_frame, text="วันที่/เวลา:", width=15).pack(side=tk.LEFT)
        date_entry = ttk.Entry(date_frame, width=30, state="readonly")
        date_entry.pack(side=tk.LEFT, padx=10)
        date_entry.config(state="normal")
        date_entry.insert(0, self.current_values[2])
        date_entry.config(state="readonly")

        # Main job type
        main_job_frame = ttk.Frame(main_frame)
        main_job_frame.pack(fill=tk.X, pady=5)
        ttk.Label(main_job_frame, text="ประเภทงานหลัก:", width=15).pack(side=tk.LEFT)
        self.main_job_combo = ttk.Combobox(
            main_job_frame,
            textvariable=self.main_job_var,
            state="readonly",
            width=25
        )
        self.main_job_combo.pack(side=tk.LEFT, padx=10)

        # Sub job type
        sub_job_frame = ttk.Frame(main_frame)
        sub_job_frame.pack(fill=tk.X, pady=5)
        ttk.Label(sub_job_frame, text="ประเภทงานย่อย:", width=15).pack(side=tk.LEFT)
        self.sub_job_combo = ttk.Combobox(
            sub_job_frame,
            textvariable=self.sub_job_var,
            state="readonly",
            width=25
        )
        self.sub_job_combo.pack(side=tk.LEFT, padx=10)

        # Notes
        notes_frame = ttk.Frame(main_frame)
        notes_frame.pack(fill=tk.X, pady=5)
        ttk.Label(notes_frame, text="หมายเหตุ:", width=15).pack(side=tk.LEFT)
        self.notes_entry = ttk.Entry(notes_frame, width=40)
        self.notes_entry.pack(side=tk.LEFT, padx=10)
        if len(self.current_values) > 5:
            self.notes_entry.insert(0, self.current_values[5] or "")

        # User (readonly - informative)
        user_frame = ttk.Frame(main_frame)
        user_frame.pack(fill=tk.X, pady=5)
        ttk.Label(user_frame, text="ผู้ใช้:", width=15).pack(side=tk.LEFT)
        user_entry = ttk.Entry(user_frame, width=30, state="readonly")
        user_entry.pack(side=tk.LEFT, padx=10)
        user_entry.config(state="normal")
        user_entry.insert(0, self.current_values[6] if len(self.current_values) > 6 else self.current_values[4])
        user_entry.config(state="readonly")

        # Setup job type combos
        self.setup_job_combos()

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)

        ttk.Button(
            button_frame,
            text="บันทึกการเปลี่ยนแปลง",
            command=self.save_changes
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="ยกเลิก",
            command=self.cancel
        ).pack(side=tk.LEFT, padx=5)

        # Focus on barcode entry and select all text
        self.barcode_entry.focus_set()
        self.barcode_entry.select_range(0, tk.END)

    def setup_job_combos(self):
        """Setup job type combo boxes with current values"""
        try:
            # Load job types
            job_types = list(self.job_types_data.keys())
            self.main_job_combo['values'] = job_types
            self.main_job_var.set(self.current_values[3])  # Main job name

            # Bind main job change to update sub jobs
            self.main_job_combo.bind('<<ComboboxSelected>>', self.on_main_job_change)

            # Load initial sub jobs and set current sub job
            self.load_sub_jobs()  # Load sub jobs for current main job
            if len(self.current_values) > 4:
                self.sub_job_var.set(self.current_values[4] or "")  # Sub job name

        except Exception as e:
            print(f"Error setting up edit dialog: {str(e)}")

    def on_main_job_change(self, event=None):
        """Handle main job change - update sub job list"""
        self.load_sub_jobs()

        # Clear current sub job selection if this was triggered by user change
        if event:
            self.sub_job_var.set('')

    def load_sub_jobs(self):
        """Load sub jobs for currently selected main job"""
        selected_main_job = self.main_job_var.get()
        main_job_id = self.job_types_data.get(selected_main_job)

        if main_job_id:
            try:
                # Load sub jobs for selected main job
                results = self.sub_job_repo.get_by_main_job(main_job_id, active_only=True)
                sub_job_names = [row['sub_job_name'] for row in results]
                self.sub_job_combo['values'] = sub_job_names

                # Cache sub job data for save operation
                self.sub_job_types_data = {row['sub_job_name']: row['id'] for row in results}

            except Exception as e:
                print(f"Error loading sub jobs in edit dialog: {str(e)}")
                self.sub_job_combo['values'] = []
                self.sub_job_types_data = {}

    def save_changes(self):
        """Save changes to database"""
        new_barcode = self.barcode_entry.get().strip()
        new_main_job = self.main_job_var.get()
        new_sub_job = self.sub_job_var.get()
        new_notes = self.notes_entry.get().strip()

        # Validate
        if not new_barcode:
            messagebox.showwarning("คำเตือน", "กรุณาใส่บาร์โค้ด")
            return

        if not new_main_job:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกประเภทงานหลัก")
            return

        if not new_sub_job:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกประเภทงานย่อย")
            return

        try:
            # Get job IDs
            new_main_job_id = self.job_types_data.get(new_main_job, 0)

            # Get sub job ID from cache or repository
            if new_sub_job in self.sub_job_types_data:
                new_sub_job_id = self.sub_job_types_data[new_sub_job]
            else:
                # Fallback: query repository
                sub_job_data = self.sub_job_repo.find_by_name(new_main_job_id, new_sub_job)
                if not sub_job_data:
                    messagebox.showerror("ข้อผิดพลาด", "ไม่พบประเภทงานย่อยที่เลือก")
                    return
                new_sub_job_id = sub_job_data['id']

            # Update database
            self.scan_log_repo.update(
                self.record_id,
                {
                    'barcode': new_barcode,
                    'job_type': new_main_job,
                    'job_id': new_main_job_id,
                    'sub_job_id': new_sub_job_id,
                    'notes': new_notes
                }
            )

            messagebox.showinfo("สำเร็จ", "อัพเดทข้อมูลเรียบร้อยแล้ว")
            self.dialog.destroy()

            # Execute callback if provided
            if self.on_save_callback:
                self.on_save_callback()

        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถอัพเดทข้อมูลได้: {str(e)}")

    def cancel(self):
        """Cancel and close dialog"""
        self.dialog.destroy()

    def show(self):
        """Show the dialog and wait for it to close"""
        self.parent.wait_window(self.dialog)
