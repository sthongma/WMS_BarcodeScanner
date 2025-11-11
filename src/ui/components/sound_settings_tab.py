#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sound Settings Tab Component
UI component for sound configuration
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, Callable, Optional
from src.services.sound_service import SoundService
from src.services.job_service import JobService
from src.utils.sound_manager import get_sound_manager


class SoundSettingsTab:
    """แท็บการตั้งค่าเสียง"""

    def __init__(self, parent: ttk.Frame, db_manager, on_settings_changed: Callable = None):
        self.parent = parent
        self.db_manager = db_manager
        self.on_settings_changed = on_settings_changed

        # Initialize services
        self.sound_service = SoundService("UI: SoundSettingsTab")
        self.job_service = JobService("UI: SoundSettingsTab")
        self.sound_manager = get_sound_manager()

        # Cache data
        self.job_types_cache = []
        self.sub_job_types_cache = {}

        self.setup_ui()

    def setup_ui(self):
        """สร้าง UI"""
        # สร้าง frame หลัก
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # หัวข้อ
        title_label = ttk.Label(main_frame, text="การตั้งค่าเสียง", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))

        # Global Settings Frame
        self._create_global_settings_frame(main_frame)

        # Sound Settings List Frame
        self._create_sound_settings_list_frame(main_frame)

        # Control Buttons Frame
        self._create_control_buttons_frame(main_frame)

        # โหลดข้อมูลเริ่มต้น
        self.load_job_types()
        self.refresh_sound_settings()

    def _create_global_settings_frame(self, parent):
        """สร้าง frame สำหรับการตั้งค่าทั่วไป"""
        frame = ttk.LabelFrame(parent, text="การตั้งค่าทั่วไป")
        frame.pack(fill=tk.X, pady=(0, 10))

        # Sound enabled checkbox
        self.sound_enabled_var = tk.BooleanVar(value=self.sound_manager.is_enabled())
        sound_enabled_check = ttk.Checkbutton(
            frame,
            text="เปิดใช้งานเสียง",
            variable=self.sound_enabled_var,
            command=self.toggle_global_sound
        )
        sound_enabled_check.pack(anchor=tk.W, padx=10, pady=5)

        # Sound status
        status = "พร้อมใช้งาน" if self.sound_manager.is_available() else "ไม่พร้อมใช้งาน (pygame ไม่ได้ติดตั้ง)"
        status_color = "green" if self.sound_manager.is_available() else "red"
        status_label = ttk.Label(frame, text=f"สถานะ: {status}", foreground=status_color)
        status_label.pack(anchor=tk.W, padx=10, pady=5)

    def _create_sound_settings_list_frame(self, parent):
        """สร้าง frame สำหรับแสดงรายการการตั้งค่าเสียง"""
        frame = ttk.LabelFrame(parent, text="รายการการตั้งค่าเสียง")
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Treeview สำหรับแสดงการตั้งค่าเสียง
        columns = ("ID", "Job Type", "Sub Job Type", "Event", "Sound File", "Volume", "Status")
        self.sound_tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)

        # กำหนดหัวคอลัมน์และขนาด
        column_widths = {"ID": 50, "Job Type": 120, "Sub Job Type": 120, "Event": 80,
                        "Sound File": 200, "Volume": 60, "Status": 80}

        for col in columns:
            self.sound_tree.heading(col, text=col)
            self.sound_tree.column(col, width=column_widths.get(col, 100))

        # Scrollbars
        vsb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.sound_tree.yview)
        hsb = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.sound_tree.xview)
        self.sound_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Pack
        self.sound_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        vsb.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        hsb.pack(side=tk.BOTTOM, fill=tk.X, padx=5)

        # Bind double-click
        self.sound_tree.bind("<Double-1>", lambda e: self.edit_sound_setting())

    def _create_control_buttons_frame(self, parent):
        """สร้าง frame สำหรับปุ่มควบคุม"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X)

        # ปุ่มต่างๆ
        ttk.Button(frame, text="➕ เพิ่มการตั้งค่า", command=self.add_sound_setting).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(frame, text="✏️ แก้ไข", command=self.edit_sound_setting).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(frame, text="🗑️ ลบ", command=self.delete_sound_setting).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(frame, text="🔊 ทดสอบ", command=self.test_sound).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(frame, text="🔄 รีเฟรช", command=self.refresh_sound_settings).pack(
            side=tk.LEFT, padx=5
        )

    def load_job_types(self):
        """โหลดรายการ Job Types"""
        try:
            self.job_types_cache = self.job_service.get_all_job_types()
        except Exception as e:
            print(f"Error loading job types: {e}")
            self.job_types_cache = []

    def refresh_sound_settings(self):
        """รีเฟรชรายการการตั้งค่าเสียง"""
        # ล้างข้อมูลเก่า
        for item in self.sound_tree.get_children():
            self.sound_tree.delete(item)

        try:
            # ดึงข้อมูลจาก SoundService
            settings = self.sound_service.get_all_sound_settings()

            for setting in settings:
                status = "✅ เปิด" if setting.get('is_enabled') else "❌ ปิด"
                volume_percent = f"{int(setting.get('volume', 0) * 100)}%"

                self.sound_tree.insert("", tk.END, values=(
                    setting.get('id'),
                    setting.get('job_name', 'Default'),
                    setting.get('sub_job_name', '-'),
                    setting.get('event_type'),
                    setting.get('sound_file'),
                    volume_percent,
                    status
                ))

        except Exception as e:
            messagebox.showerror("ผิดพลาด", f"ไม่สามารถโหลดข้อมูล: {str(e)}")

    def add_sound_setting(self):
        """เพิ่มการตั้งค่าเสียง"""
        self._show_sound_setting_dialog()

    def edit_sound_setting(self):
        """แก้ไขการตั้งค่าเสียง"""
        selected = self.sound_tree.selection()
        if not selected:
            messagebox.showwarning("แจ้งเตือน", "กรุณาเลือกการตั้งค่าที่ต้องการแก้ไข")
            return

        item = self.sound_tree.item(selected[0])
        values = item['values']

        # ดึงข้อมูลที่เลือก
        setting_id = values[0]
        job_name = values[1]
        sub_job_name = values[2]
        event_type = values[3]
        sound_file = values[4]
        volume_str = values[5]
        is_enabled = values[6].startswith("✅")

        # แปลง volume string เป็น float
        volume = float(volume_str.rstrip('%')) / 100.0

        self._show_sound_setting_dialog(setting_id, job_name, sub_job_name,
                                        event_type, sound_file, volume, is_enabled)

    def _show_sound_setting_dialog(self, setting_id=None, job_name="Default",
                                   sub_job_name="-", event_type="success",
                                   sound_file="", volume=0.8, is_enabled=True):
        """แสดง dialog สำหรับเพิ่ม/แก้ไขการตั้งค่าเสียง"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("เพิ่มการตั้งค่าเสียง" if setting_id is None else "แก้ไขการตั้งค่าเสียง")
        dialog.geometry("500x400")
        dialog.transient(self.parent)
        dialog.grab_set()

        # Job Type
        ttk.Label(dialog, text="Job Type:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        job_var = tk.StringVar(value=job_name)
        job_combo = ttk.Combobox(dialog, textvariable=job_var, state="readonly", width=30)
        job_values = ["Default"] + [j['name'] for j in self.job_types_cache]
        job_combo['values'] = job_values
        job_combo.grid(row=0, column=1, padx=10, pady=5)

        # Sub Job Type
        ttk.Label(dialog, text="Sub Job Type:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        sub_job_var = tk.StringVar(value=sub_job_name)
        sub_job_combo = ttk.Combobox(dialog, textvariable=sub_job_var, state="readonly", width=30)
        sub_job_combo['values'] = ["-"]
        sub_job_combo.grid(row=1, column=1, padx=10, pady=5)

        def on_job_changed(event=None):
            """อัพเดท Sub Job Types เมื่อเลือก Job Type"""
            selected_job = job_var.get()
            if selected_job == "Default":
                sub_job_combo['values'] = ["-"]
                sub_job_var.set("-")
            else:
                # หา job_id
                job_id = next((j['id'] for j in self.job_types_cache if j['name'] == selected_job), None)
                if job_id:
                    sub_jobs = self.job_service.get_sub_job_types(job_id)
                    sub_job_combo['values'] = ["-"] + [sj['name'] for sj in sub_jobs]
                    sub_job_var.set("-")

        job_combo.bind("<<ComboboxSelected>>", on_job_changed)

        # Event Type
        ttk.Label(dialog, text="Event Type:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        event_var = tk.StringVar(value=event_type)
        event_combo = ttk.Combobox(dialog, textvariable=event_var, state="readonly", width=30)
        event_combo['values'] = ["success", "error", "duplicate", "warning"]
        event_combo.grid(row=2, column=1, padx=10, pady=5)

        # Sound File
        ttk.Label(dialog, text="Sound File:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        sound_file_var = tk.StringVar(value=sound_file)
        sound_entry = ttk.Entry(dialog, textvariable=sound_file_var, width=32)
        sound_entry.grid(row=3, column=1, padx=10, pady=5)

        def browse_sound():
            """เปิด file dialog เพื่อเลือกไฟล์เสียง"""
            filename = filedialog.askopenfilename(
                title="เลือกไฟล์เสียง",
                filetypes=[("Sound files", "*.mp3 *.wav *.ogg"), ("All files", "*.*")]
            )
            if filename:
                # แปลงเป็น relative path จาก project root
                import os
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__)))))
                try:
                    rel_path = os.path.relpath(filename, project_root)
                    sound_file_var.set(f"/{rel_path.replace(os.sep, '/')}")
                except:
                    sound_file_var.set(filename)

        ttk.Button(dialog, text="เลือกไฟล์...", command=browse_sound).grid(
            row=3, column=2, padx=5, pady=5
        )

        # Volume
        ttk.Label(dialog, text="Volume (0-100%):").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        volume_var = tk.IntVar(value=int(volume * 100))
        volume_scale = ttk.Scale(dialog, from_=0, to=100, orient=tk.HORIZONTAL,
                                variable=volume_var, length=200)
        volume_scale.grid(row=4, column=1, padx=10, pady=5)
        volume_label = ttk.Label(dialog, text=f"{volume_var.get()}%")
        volume_label.grid(row=4, column=2, padx=5, pady=5)

        def on_volume_changed(event=None):
            volume_label.config(text=f"{volume_var.get()}%")

        volume_scale.bind("<Motion>", on_volume_changed)
        volume_scale.bind("<ButtonRelease-1>", on_volume_changed)

        # Enabled checkbox
        enabled_var = tk.BooleanVar(value=is_enabled)
        ttk.Checkbutton(dialog, text="เปิดใช้งาน", variable=enabled_var).grid(
            row=5, column=1, sticky=tk.W, padx=10, pady=5
        )

        def save_setting():
            """บันทึกการตั้งค่า"""
            try:
                # หา job_id และ sub_job_id
                job_id = None
                sub_job_id = None

                if job_var.get() != "Default":
                    job_id = next((j['id'] for j in self.job_types_cache if j['name'] == job_var.get()), None)

                    if sub_job_var.get() != "-":
                        sub_jobs = self.job_service.get_sub_job_types(job_id)
                        sub_job_id = next((sj['id'] for sj in sub_jobs if sj['name'] == sub_job_var.get()), None)

                # บันทึก
                result = self.sound_service.save_sound_setting(
                    job_id=job_id,
                    sub_job_id=sub_job_id,
                    event_type=event_var.get(),
                    sound_file=sound_file_var.get(),
                    volume=volume_var.get() / 100.0,
                    is_enabled=enabled_var.get()
                )

                if result['success']:
                    messagebox.showinfo("สำเร็จ", result['message'])
                    dialog.destroy()
                    self.refresh_sound_settings()
                    if self.on_settings_changed:
                        self.on_settings_changed()
                else:
                    messagebox.showerror("ผิดพลาด", result['message'])

            except Exception as e:
                messagebox.showerror("ผิดพลาด", f"ไม่สามารถบันทึกได้: {str(e)}")

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=6, column=0, columnspan=3, pady=20)

        ttk.Button(button_frame, text="บันทึก", command=save_setting).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="ยกเลิก", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def delete_sound_setting(self):
        """ลบการตั้งค่าเสียง"""
        selected = self.sound_tree.selection()
        if not selected:
            messagebox.showwarning("แจ้งเตือน", "กรุณาเลือกการตั้งค่าที่ต้องการลบ")
            return

        if not messagebox.askyesno("ยืนยัน", "คุณต้องการลบการตั้งค่านี้หรือไม่?"):
            return

        try:
            item = self.sound_tree.item(selected[0])
            setting_id = item['values'][0]

            result = self.sound_service.delete_sound_setting(setting_id)

            if result['success']:
                messagebox.showinfo("สำเร็จ", result['message'])
                self.refresh_sound_settings()
                if self.on_settings_changed:
                    self.on_settings_changed()
            else:
                messagebox.showerror("ผิดพลาด", result['message'])

        except Exception as e:
            messagebox.showerror("ผิดพลาด", f"ไม่สามารถลบได้: {str(e)}")

    def test_sound(self):
        """ทดสอบเสียง"""
        selected = self.sound_tree.selection()
        if not selected:
            messagebox.showwarning("แจ้งเตือน", "กรุณาเลือกการตั้งค่าที่ต้องการทดสอบ")
            return

        try:
            item = self.sound_tree.item(selected[0])
            sound_file = item['values'][4]
            volume_str = item['values'][5]
            volume = float(volume_str.rstrip('%')) / 100.0

            if self.sound_manager.test_sound(sound_file):
                messagebox.showinfo("สำเร็จ", "เล่นเสียงทดสอบแล้ว")
            else:
                messagebox.showwarning("แจ้งเตือน", "ไม่สามารถเล่นเสียงได้")

        except Exception as e:
            messagebox.showerror("ผิดพลาด", f"ไม่สามารถทดสอบเสียงได้: {str(e)}")

    def toggle_global_sound(self):
        """เปิด/ปิดเสียงทั้งหมด"""
        enabled = self.sound_enabled_var.get()
        self.sound_manager.set_enabled(enabled)

        if self.on_settings_changed:
            self.on_settings_changed()
