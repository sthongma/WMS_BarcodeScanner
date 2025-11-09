#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sub Job Settings Tab Component
UI component for managing sub job types
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Callable, Optional
from ..tabs.base_tab import BaseTab
from ..dialogs.sub_job_edit_dialog import SubJobEditDialog


class SubJobSettingsTab(BaseTab):
    """แท็บจัดการประเภทงานย่อย"""

    def __init__(
        self,
        parent: tk.Widget,
        db_manager: Any,
        repositories: Dict[str, Any],
        services: Dict[str, Any],
        on_sub_job_updated: Optional[Callable] = None
    ):
        self.on_sub_job_updated = on_sub_job_updated
        self.current_selected_main_job_id = None
        self.current_selected_sub_job_id = None
        self.job_types_data = {}
        self.sub_job_types_data = {}
        super().__init__(parent, db_manager, repositories, services)
        self.refresh_main_job_list()

    def build_ui(self):
        """สร้าง UI"""
        # Use the frame provided by BaseTab
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # หัวข้อ
        title_label = ttk.Label(main_frame, text="จัดการประเภทงานย่อย", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))

        # Main container
        container = ttk.Frame(main_frame)
        container.pack(fill=tk.BOTH, expand=True)

        # Left side - Main job selection
        left_frame = ttk.LabelFrame(container, text="เลือกประเภทงานหลัก", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Main job listbox
        ttk.Label(left_frame, text="ประเภทงานหลัก:").pack(anchor=tk.W)

        main_job_list_frame = ttk.Frame(left_frame)
        main_job_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        main_scrollbar = ttk.Scrollbar(main_job_list_frame)
        main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.main_job_listbox = tk.Listbox(
            main_job_list_frame,
            yscrollcommand=main_scrollbar.set,
            width=25
        )
        self.main_job_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        main_scrollbar.config(command=self.main_job_listbox.yview)
        self.main_job_listbox.bind('<<ListboxSelect>>', self.on_main_job_select)

        # Right side - Sub job management
        right_frame = ttk.LabelFrame(container, text="จัดการประเภทงานย่อย", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Selected main job display
        self.selected_main_job_label = ttk.Label(
            right_frame,
            text="เลือกประเภทงานหลักเพื่อจัดการงานย่อย",
            font=("Arial", 10, "bold")
        )
        self.selected_main_job_label.pack(pady=5)

        # Add new sub job
        add_sub_frame = ttk.Frame(right_frame)
        add_sub_frame.pack(fill=tk.X, pady=10)

        ttk.Label(add_sub_frame, text="ชื่อประเภทงานย่อย:").pack(anchor=tk.W)
        self.new_sub_job_entry = ttk.Entry(add_sub_frame, width=30)
        self.new_sub_job_entry.pack(fill=tk.X, pady=2)

        ttk.Label(add_sub_frame, text="คำอธิบาย (ไม่บังคับ):").pack(anchor=tk.W, pady=(10, 0))
        self.sub_job_desc_entry = ttk.Entry(add_sub_frame, width=30)
        self.sub_job_desc_entry.pack(fill=tk.X, pady=2)

        add_sub_btn_frame = ttk.Frame(add_sub_frame)
        add_sub_btn_frame.pack(fill=tk.X, pady=10)

        self.add_sub_job_btn = ttk.Button(
            add_sub_btn_frame,
            text="เพิ่มประเภทงานย่อย",
            command=self.add_sub_job_type,
            state=tk.DISABLED
        )
        self.add_sub_job_btn.pack(side=tk.LEFT)

        # Sub job list
        sub_list_frame = ttk.Frame(right_frame)
        sub_list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        ttk.Label(sub_list_frame, text="รายการประเภทงานย่อย:").pack(anchor=tk.W)

        sub_job_list_container = ttk.Frame(sub_list_frame)
        sub_job_list_container.pack(fill=tk.BOTH, expand=True, pady=5)

        sub_scrollbar = ttk.Scrollbar(sub_job_list_container)
        sub_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.sub_job_listbox = tk.Listbox(sub_job_list_container, yscrollcommand=sub_scrollbar.set)
        self.sub_job_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sub_scrollbar.config(command=self.sub_job_listbox.yview)
        self.sub_job_listbox.bind('<<ListboxSelect>>', self.on_sub_job_select)

        # Sub job management buttons
        sub_btn_frame = ttk.Frame(sub_list_frame)
        sub_btn_frame.pack(fill=tk.X, pady=5)

        self.edit_sub_job_btn = ttk.Button(
            sub_btn_frame,
            text="แก้ไข",
            command=self.edit_sub_job_type,
            state=tk.DISABLED
        )
        self.edit_sub_job_btn.pack(side=tk.LEFT, padx=5)

        self.delete_sub_job_btn = ttk.Button(
            sub_btn_frame,
            text="ลบ",
            command=self.delete_sub_job_type,
            state=tk.DISABLED
        )
        self.delete_sub_job_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            sub_btn_frame,
            text="รีเฟรช",
            command=self.refresh_sub_job_list
        ).pack(side=tk.LEFT, padx=5)

    def refresh_main_job_list(self):
        """Refresh main job list in sub job management tab"""
        try:
            # Clear existing items
            self.main_job_listbox.delete(0, tk.END)

            # Use JobTypeRepository to get all job types
            results = self.job_type_repo.get_all_job_types()

            # Clear and rebuild job types data
            self.job_types_data = {}

            # Add job types to main job listbox
            for job in results:
                job_name = job['name']
                job_id = job['id']
                self.job_types_data[job_name] = job_id

                display_text = f"{job_name} (ID: {job_id})"
                self.main_job_listbox.insert(tk.END, display_text)

        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถโหลดประเภทงานหลักได้: {str(e)}")

    def on_main_job_select(self, event):
        """Handle main job selection for sub job management"""
        selection = self.main_job_listbox.curselection()
        if not selection:
            return

        # Get selected job
        display_text = self.main_job_listbox.get(selection[0])
        job_name = display_text.split(" (ID: ")[0]
        job_id = self.job_types_data.get(job_name)

        self.current_selected_main_job_id = job_id
        self.selected_main_job_label.config(text=f"จัดการประเภทงานย่อยสำหรับ: {job_name}")
        self.add_sub_job_btn.config(state=tk.NORMAL)

        # Load sub job types for this main job
        self.refresh_sub_job_list()

    def refresh_sub_job_list(self):
        """Refresh sub job types list for selected main job"""
        if not self.current_selected_main_job_id:
            return

        try:
            # Clear existing items
            self.sub_job_listbox.delete(0, tk.END)

            # Use SubJobRepository instead of direct SQL
            results = self.sub_job_repo.get_by_main_job(
                main_job_id=self.current_selected_main_job_id,
                active_only=True
            )

            # Update sub_job_types_data
            self.sub_job_types_data = {}

            for row in results:
                sub_job_id = row['id']
                sub_job_name = row['name']
                description = row.get('description', '') or ""

                self.sub_job_types_data[sub_job_name] = sub_job_id

                # Display in listbox
                display_text = f"{sub_job_name}"
                if description:
                    display_text += f" - {description}"
                display_text += f" (ID: {sub_job_id})"

                self.sub_job_listbox.insert(tk.END, display_text)

        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถโหลดรายการงานย่อยได้: {str(e)}")

    def on_sub_job_select(self, event):
        """Handle sub job selection"""
        selection = self.sub_job_listbox.curselection()
        if selection:
            self.edit_sub_job_btn.config(state=tk.NORMAL)
            self.delete_sub_job_btn.config(state=tk.NORMAL)

            # Get selected sub job ID
            display_text = self.sub_job_listbox.get(selection[0])
            # Extract ID from the end of the string
            if "(ID: " in display_text:
                id_part = display_text.split("(ID: ")[-1].rstrip(")")
                try:
                    self.current_selected_sub_job_id = int(id_part)
                except ValueError:
                    self.current_selected_sub_job_id = None
        else:
            self.edit_sub_job_btn.config(state=tk.DISABLED)
            self.delete_sub_job_btn.config(state=tk.DISABLED)
            self.current_selected_sub_job_id = None

    def add_sub_job_type(self):
        """Add new sub job type"""
        if not self.current_selected_main_job_id:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกประเภทงานหลักก่อน")
            return

        sub_job_name = self.new_sub_job_entry.get().strip()
        description = self.sub_job_desc_entry.get().strip()

        if not sub_job_name:
            messagebox.showwarning("คำเตือน", "กรุณาใส่ชื่อประเภทงานย่อย")
            return

        try:
            # Use SubJobRepository instead of direct SQL
            # Check for duplicate name within the same main job
            if self.sub_job_repo.duplicate_exists(self.current_selected_main_job_id, sub_job_name):
                messagebox.showwarning("คำเตือน", "ชื่อประเภทงานย่อยนี้มีอยู่แล้ว")
                return

            # Insert new sub job type
            self.sub_job_repo.create_sub_job(
                main_job_id=self.current_selected_main_job_id,
                sub_job_name=sub_job_name,
                description=description
            )

            # Clear input fields
            self.new_sub_job_entry.delete(0, tk.END)
            self.sub_job_desc_entry.delete(0, tk.END)

            # Refresh list
            self.refresh_sub_job_list()

            messagebox.showinfo("สำเร็จ", f"เพิ่มประเภทงานย่อย '{sub_job_name}' แล้ว")

            # Call callback
            if self.on_sub_job_updated:
                self.on_sub_job_updated()

        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถเพิ่มประเภทงานย่อยได้: {str(e)}")

    def edit_sub_job_type(self):
        """Edit selected sub job type"""
        if not self.current_selected_sub_job_id:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกประเภทงานย่อยที่จะแก้ไข")
            return

        # Get current data using SubJobRepository
        try:
            current_data = self.sub_job_repo.find_by_id(self.current_selected_sub_job_id)

            if not current_data:
                messagebox.showerror("ข้อผิดพลาด", "ไม่พบข้อมูลประเภทงานย่อย")
                return

            # Show edit dialog
            self.show_edit_dialog(self.current_selected_sub_job_id, current_data)

        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถโหลดข้อมูลได้: {str(e)}")

    def show_edit_dialog(self, sub_job_id: int, current_data: Dict):
        """Show dialog for editing sub job type"""
        # Use SubJobEditDialog
        dialog = SubJobEditDialog(
            parent=self.frame.winfo_toplevel(),
            sub_job_repo=self.sub_job_repo,
            sub_job_id=sub_job_id,
            main_job_id=self.current_selected_main_job_id,
            current_data=current_data,
            on_save_callback=self.on_edit_complete
        )
        dialog.show()

    def on_edit_complete(self):
        """Callback when edit is complete"""
        self.refresh_sub_job_list()
        if self.on_sub_job_updated:
            self.on_sub_job_updated()

    def delete_sub_job_type(self):
        """Delete selected sub job type"""
        if not self.current_selected_sub_job_id:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกประเภทงานย่อยที่จะลบ")
            return

        # Get sub job name for confirmation using SubJobRepository
        try:
            sub_job_data = self.sub_job_repo.find_by_id(self.current_selected_sub_job_id)

            if not sub_job_data:
                messagebox.showerror("ข้อผิดพลาด", "ไม่พบข้อมูลประเภทงานย่อย")
                return

            sub_job_name = sub_job_data['name']

            # Confirm deletion
            if messagebox.askyesno(
                "ยืนยัน",
                f"ต้องการลบประเภทงานย่อย '{sub_job_name}' หรือไม่?\n\n" +
                "หมายเหตุ: ข้อมูลการสแกนที่ใช้ประเภทงานย่อยนี้จะยังคงอยู่ แต่จะไม่สามารถเลือกใช้ได้อีก"
            ):
                # Soft delete (set is_active = 0) using SubJobRepository
                self.sub_job_repo.soft_delete(self.current_selected_sub_job_id)

                messagebox.showinfo("สำเร็จ", f"ลบประเภทงานย่อย '{sub_job_name}' แล้ว")

                # Refresh list
                self.refresh_sub_job_list()

                # Reset button states
                self.edit_sub_job_btn.config(state=tk.DISABLED)
                self.delete_sub_job_btn.config(state=tk.DISABLED)
                self.current_selected_sub_job_id = None

                # Call callback
                if self.on_sub_job_updated:
                    self.on_sub_job_updated()

        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถลบประเภทงานย่อยได้: {str(e)}")
