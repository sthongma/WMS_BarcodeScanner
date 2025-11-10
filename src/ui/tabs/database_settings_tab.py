#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Settings Tab Component
UI component for database settings
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Callable, Optional
from ..tabs.base_tab import BaseTab


class DatabaseSettingsTab(BaseTab):
    """แท็บการตั้งค่าฐานข้อมูล"""

    def __init__(
        self,
        parent: tk.Widget,
        db_manager: Any,
        repositories: Dict[str, Any],
        services: Dict[str, Any],
        on_settings_changed: Optional[Callable] = None
    ):
        self.on_settings_changed = on_settings_changed
        super().__init__(parent, db_manager, repositories, services)
        self.load_settings()

    def build_ui(self):
        """สร้าง UI"""
        # Use the frame provided by BaseTab
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # หัวข้อ
        title_label = ttk.Label(main_frame, text="การตั้งค่าฐานข้อมูล", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Frame สำหรับการตั้งค่า
        settings_frame = ttk.LabelFrame(main_frame, text="การตั้งค่าการเชื่อมต่อ")
        settings_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Server
        ttk.Label(settings_frame, text="Server:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.server_entry = ttk.Entry(settings_frame, width=40)
        self.server_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Database
        ttk.Label(settings_frame, text="Database:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.database_entry = ttk.Entry(settings_frame, width=40)
        self.database_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Authentication Type
        ttk.Label(settings_frame, text="Authentication:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.auth_var = tk.StringVar(value="SQL")
        auth_combo = ttk.Combobox(settings_frame, textvariable=self.auth_var, 
                                 values=["Windows", "SQL"], state="readonly", width=37)
        auth_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        auth_combo.bind("<<ComboboxSelected>>", self.on_auth_change)
        
        # Username
        ttk.Label(settings_frame, text="Username:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.username_entry = ttk.Entry(settings_frame, width=40)
        self.username_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Password
        ttk.Label(settings_frame, text="Password:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.password_entry = ttk.Entry(settings_frame, width=40, show="*")
        self.password_entry.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Frame สำหรับปุ่ม
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        # ปุ่มทดสอบการเชื่อมต่อ
        test_button = ttk.Button(button_frame, text="ทดสอบการเชื่อมต่อ", command=self.test_connection)
        test_button.pack(side=tk.LEFT, padx=5)
        
        # ปุ่มบันทึก
        save_button = ttk.Button(button_frame, text="บันทึก", command=self.save_settings)
        save_button.pack(side=tk.LEFT, padx=5)
        
        # ปุ่มรีเซ็ต
        reset_button = ttk.Button(button_frame, text="รีเซ็ต", command=self.reset_settings)
        reset_button.pack(side=tk.LEFT, padx=5)
    
    def load_settings(self):
        """โหลดการตั้งค่าปัจจุบัน"""
        config = self.db.config_manager.get_config()
        
        self.server_entry.delete(0, tk.END)
        self.server_entry.insert(0, config.get("server", ""))
        
        self.database_entry.delete(0, tk.END)
        self.database_entry.insert(0, config.get("database", ""))
        
        self.auth_var.set(config.get("auth_type", "SQL"))
        
        self.username_entry.delete(0, tk.END)
        self.username_entry.insert(0, config.get("username", ""))
        
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, config.get("password", ""))
        
        self.on_auth_change()
    
    def on_auth_change(self, event=None):
        """เมื่อเปลี่ยนประเภทการยืนยันตัวตน"""
        if self.auth_var.get() == "Windows":
            self.username_entry.config(state="disabled")
            self.password_entry.config(state="disabled")
        else:
            self.username_entry.config(state="normal")
            self.password_entry.config(state="normal")
    
    def test_connection(self):
        """ทดสอบการเชื่อมต่อ"""
        try:
            # สร้างการตั้งค่าใหม่
            new_config = {
                "server": self.server_entry.get(),
                "database": self.database_entry.get(),
                "auth_type": self.auth_var.get(),
                "username": self.username_entry.get(),
                "password": self.password_entry.get()
            }
            
            # อัปเดตการเชื่อมต่อ
            if self.db.update_connection(new_config):
                # ทดสอบการเชื่อมต่อ
                if self.db.test_connection():
                    messagebox.showinfo("สำเร็จ", "การเชื่อมต่อฐานข้อมูลสำเร็จ")
                else:
                    messagebox.showerror("ผิดพลาด", "ไม่สามารถเชื่อมต่อฐานข้อมูลได้")
            else:
                messagebox.showerror("ผิดพลาด", "ไม่สามารถอัปเดตการตั้งค่าได้")
                
        except Exception as e:
            messagebox.showerror("ผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")
    
    def save_settings(self):
        """บันทึกการตั้งค่า"""
        try:
            new_config = {
                "server": self.server_entry.get(),
                "database": self.database_entry.get(),
                "auth_type": self.auth_var.get(),
                "username": self.username_entry.get(),
                "password": self.password_entry.get()
            }
            
            if self.db.update_connection(new_config):
                messagebox.showinfo("สำเร็จ", "บันทึกการตั้งค่าเรียบร้อยแล้ว")
                if self.on_settings_changed:
                    self.on_settings_changed()
            else:
                messagebox.showerror("ผิดพลาด", "ไม่สามารถบันทึกการตั้งค่าได้")
                
        except Exception as e:
            messagebox.showerror("ผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")
    
    def reset_settings(self):
        """รีเซ็ตการตั้งค่า"""
        if messagebox.askyesno("ยืนยัน", "คุณต้องการรีเซ็ตการตั้งค่าเป็นค่าเริ่มต้นหรือไม่?"):
            if self.db.config_manager.reset_to_default():
                self.load_settings()
                messagebox.showinfo("สำเร็จ", "รีเซ็ตการตั้งค่าเรียบร้อยแล้ว")
            else:
                messagebox.showerror("ผิดพลาด", "ไม่สามารถรีเซ็ตการตั้งค่าได้") 