#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sub Job Edit Dialog
Dialog for editing sub job type information
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Callable, Optional


class SubJobEditDialog:
    """
    Dialog for editing sub job type

    Allows editing of sub job name and description. Validates that the
    new name doesn't conflict with existing sub jobs for the same main job.
    """

    def __init__(
        self,
        parent: tk.Widget,
        sub_job_repo: Any,
        sub_job_id: int,
        main_job_id: int,
        current_data: Dict[str, Any],
        on_save_callback: Optional[Callable] = None
    ):
        """
        Initialize sub job edit dialog

        Args:
            parent: Parent window
            sub_job_repo: SubJobRepository instance for database operations
            sub_job_id: ID of the sub job being edited
            main_job_id: ID of the main job this sub job belongs to
            current_data: Dictionary with current sub job data:
                - sub_job_name: Current name
                - description: Current description (optional)
            on_save_callback: Optional callback to execute after successful save
        """
        self.parent = parent
        self.sub_job_repo = sub_job_repo
        self.sub_job_id = sub_job_id
        self.main_job_id = main_job_id
        self.current_data = current_data
        self.on_save_callback = on_save_callback

        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("แก้ไขประเภทงานย่อย")
        self.dialog.geometry("400x220")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self.center_dialog()

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

        # Sub job name
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill=tk.X, pady=5)
        ttk.Label(name_frame, text="ชื่อประเภทงานย่อย:").pack(anchor=tk.W)
        self.name_entry = ttk.Entry(name_frame, width=40)
        self.name_entry.pack(fill=tk.X, pady=2)
        self.name_entry.insert(0, self.current_data.get('sub_job_name', ''))

        # Description
        desc_frame = ttk.Frame(main_frame)
        desc_frame.pack(fill=tk.X, pady=5)
        ttk.Label(desc_frame, text="คำอธิบาย:").pack(anchor=tk.W)
        self.desc_entry = ttk.Entry(desc_frame, width=40)
        self.desc_entry.pack(fill=tk.X, pady=2)
        self.desc_entry.insert(0, self.current_data.get('description', '') or "")

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

        # Focus on name entry and select all text
        self.name_entry.focus_set()
        self.name_entry.select_range(0, tk.END)

    def save_changes(self):
        """Save changes to database"""
        new_name = self.name_entry.get().strip()
        new_desc = self.desc_entry.get().strip()

        # Validate
        if not new_name:
            messagebox.showwarning("คำเตือน", "กรุณาใส่ชื่อประเภทงานย่อย")
            return

        try:
            # Check for duplicate name (excluding current record)
            if self.sub_job_repo.duplicate_exists(
                main_job_id=self.main_job_id,
                sub_job_name=new_name,
                exclude_id=self.sub_job_id
            ):
                messagebox.showwarning("คำเตือน", "ชื่อประเภทงานย่อยนี้มีอยู่แล้ว")
                return

            # Update database
            self.sub_job_repo.update_sub_job(
                sub_job_id=self.sub_job_id,
                sub_job_name=new_name,
                description=new_desc
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
