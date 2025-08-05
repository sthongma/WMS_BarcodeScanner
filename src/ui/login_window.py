#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WMS Barcode Scanner - Login Window
Database connection login window
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
import json
import os
from typing import Optional, Dict, Any
from PIL import Image, ImageTk

class LoginWindow:
    """Database connection login window"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WMS Barcode Scanner - เข้าสู่ระบบ")
        self.root.geometry("550x550")
        self.root.resizable(False, False)
        
        # ตั้งค่า icon สำหรับแอพ
        self.set_app_icon()
        
        # Center window
        self.center_window()
        
        # Configuration
        self.config_file = "config/sql_config.json"
        self.connection_string = ""
        self.current_user = ""
        self.config = None
        
        # Load saved configuration
        self.load_config()
        
        # Setup UI
        self.setup_ui()
        
        # Load saved settings to UI
        self.load_settings_to_ui()
        
        # Focus on server entry
        self.root.after(100, lambda: self.server_entry.focus_set())
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda e: self.login())
        
    def set_app_icon(self):
        """ตั้งค่า icon สำหรับแอพ"""
        try:
            # พยายามโหลด icon จากไฟล์ PNG
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'icons', 'app_icon.png')
            
            if os.path.exists(icon_path):
                # โหลดและปรับขนาด icon
                image = Image.open(icon_path)
                
                # สร้าง icon ขนาดต่างๆ สำหรับ Windows
                icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
                icons = []
                
                for size in icon_sizes:
                    resized_image = image.resize(size, Image.Resampling.LANCZOS)
                    icon = ImageTk.PhotoImage(resized_image)
                    icons.append(icon)
                
                # ตั้งค่า icon สำหรับ window
                self.root.iconphoto(True, *icons)
                
                # ตั้งค่า icon สำหรับ taskbar (Windows)
                if hasattr(self.root, 'iconbitmap'):
                    try:
                        # สร้างไฟล์ ICO ชั่วคราว
                        temp_ico_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'icons', 'temp_icon.ico')
                        image.save(temp_ico_path, format='ICO', sizes=icon_sizes)
                        self.root.iconbitmap(temp_ico_path)
                        
                        # ลบไฟล์ชั่วคราว
                        if os.path.exists(temp_ico_path):
                            os.remove(temp_ico_path)
                    except Exception as e:
                        print(f"ไม่สามารถตั้งค่า icon สำหรับ taskbar ได้: {e}")
                        
            else:
                print(f"ไม่พบไฟล์ icon ที่: {icon_path}")
                print("กรุณาใส่ไฟล์ app_icon.png ในโฟลเดอร์ assets/icons/")
                
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการตั้งค่า icon: {e}")
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def load_config(self) -> bool:
        """โหลดการตั้งค่าจากไฟล์"""
        try:
            default_config = {
                "server": os.environ.get('COMPUTERNAME', 'localhost') + '\\SQLEXPRESS',
                "database": "WMS_EP",
                "auth_type": "Windows",  # Windows หรือ SQL
                "username": "",
                "password": ""
            }
            
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.config = default_config.copy()
                    self.config.update(saved_config)
            else:
                self.config = default_config.copy()
                self.save_config()
            
            return True
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการโหลดการตั้งค่า: {str(e)}")
            return False
    
    def save_config(self) -> bool:
        """บันทึกการตั้งค่าลงไฟล์"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการบันทึกการตั้งค่า: {str(e)}")
            return False
    
    def update_connection_string(self):
        """อัพเดท connection string ตามการตั้งค่า"""
        if not self.config:
            return
        
        # หา driver ที่เหมาะสม
        best_driver = self.find_best_driver()
        if not best_driver:
            raise Exception("ไม่พบ ODBC Driver สำหรับ SQL Server กรุณาติดตั้ง ODBC Driver 17 หรือ 18")
        
        if self.config['auth_type'] == "Windows":
            self.connection_string = (
                f"DRIVER={{{best_driver}}};"
                f"SERVER={self.config['server']};"
                f"DATABASE={self.config['database']};"
                f"Trusted_Connection=yes;"
                f"TrustServerCertificate=yes;"
            )
            self.current_user = os.environ.get('USERNAME', 'WindowsUser')
        else:  # SQL Authentication
            self.connection_string = (
                f"DRIVER={{{best_driver}}};"
                f"SERVER={self.config['server']};"
                f"DATABASE={self.config['database']};"
                f"UID={self.config['username']};"
                f"PWD={self.config['password']};"
                f"TrustServerCertificate=yes;"
            )
            self.current_user = self.config['username']
    
    def find_best_driver(self) -> str:
        """หา driver ที่เหมาะสมที่สุด"""
        try:
            import pyodbc
            available_drivers = pyodbc.drivers()
            
            # เรียงลำดับความสำคัญ
            recommended_drivers = [
                "ODBC Driver 17 for SQL Server",
                "ODBC Driver 18 for SQL Server", 
                "ODBC Driver 13 for SQL Server",
                "SQL Server Native Client 11.0",
                "SQL Server"
            ]
            
            for driver in recommended_drivers:
                if driver in available_drivers:
                    return driver
            
            # ถ้าไม่มี driver ที่แนะนำ ให้ใช้ driver แรกที่มี
            sql_drivers = [d for d in available_drivers if 'SQL Server' in d or 'SQL' in d]
            if sql_drivers:
                return sql_drivers[0]
            
            return ""
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการตรวจสอบ drivers: {e}")
            return ""
    
    def check_drivers(self):
        """ตรวจสอบ ODBC drivers ที่มีอยู่"""
        try:
            import pyodbc
            available_drivers = pyodbc.drivers()
            best_driver = self.find_best_driver()
            
            info = f"""📋 **ข้อมูล ODBC Drivers**

🔍 **Drivers ที่มีอยู่ทั้งหมด ({len(available_drivers)}):**
"""
            
            for driver in available_drivers:
                info += f"  • {driver}\n"
            
            info += f"\n🎯 **SQL Server Drivers:**\n"
            recommended_drivers = [
                "ODBC Driver 17 for SQL Server",
                "ODBC Driver 18 for SQL Server", 
                "ODBC Driver 13 for SQL Server",
                "SQL Server Native Client 11.0",
                "SQL Server"
            ]
            
            for driver in recommended_drivers:
                status = "✅ มี" if driver in available_drivers else "❌ ไม่มี"
                info += f"  • {driver}: {status}\n"
            
            info += f"\n🏆 **Driver ที่จะใช้:** {best_driver or 'ไม่พบ'}"
            
            if not best_driver:
                info += "\n\n⚠️ **คำแนะนำ:** กรุณาติดตั้ง ODBC Driver for SQL Server"
                info += "\n\n📥 **ดาวน์โหลดได้ที่:**"
                info += "\nhttps://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server"
            
            messagebox.showinfo("ตรวจสอบ ODBC Drivers", info)
            
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการตรวจสอบ drivers: {str(e)}")
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with pyodbc.connect(self.connection_string, timeout=5) as conn:
                return True
        except Exception:
            return False
    
    def setup_ui(self):
        """Setup the login UI"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="WMS Barcode Scanner", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        subtitle_label = ttk.Label(main_frame, text="การเชื่อมต่อฐานข้อมูล", 
                                  font=("Arial", 12))
        subtitle_label.pack(pady=(0, 30))
        
        # Connection settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="ตั้งค่าการเชื่อมต่อ", padding=15)
        settings_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Server settings
        server_frame = ttk.Frame(settings_frame)
        server_frame.pack(fill=tk.X, pady=5)
        ttk.Label(server_frame, text="เซิร์ฟเวอร์:", width=15).pack(side=tk.LEFT)
        self.server_entry = ttk.Entry(server_frame, width=35)
        self.server_entry.pack(side=tk.LEFT, padx=10)
        
        # Database settings
        db_frame = ttk.Frame(settings_frame)
        db_frame.pack(fill=tk.X, pady=5)
        ttk.Label(db_frame, text="ฐานข้อมูล:", width=15).pack(side=tk.LEFT)
        self.database_entry = ttk.Entry(db_frame, width=35)
        self.database_entry.pack(side=tk.LEFT, padx=10)
        
        # Authentication type
        auth_frame = ttk.Frame(settings_frame)
        auth_frame.pack(fill=tk.X, pady=5)
        ttk.Label(auth_frame, text="การยืนยันตัวตน:", width=15).pack(side=tk.LEFT)
        self.auth_var = tk.StringVar()
        auth_combo = ttk.Combobox(auth_frame, textvariable=self.auth_var, 
                                 values=["Windows", "SQL"], state="readonly", width=15)
        auth_combo.pack(side=tk.LEFT, padx=10)
        auth_combo.bind('<<ComboboxSelected>>', self.on_auth_change)
        
        # Username (for SQL auth)
        user_frame = ttk.Frame(settings_frame)
        user_frame.pack(fill=tk.X, pady=5)
        self.user_label = ttk.Label(user_frame, text="ผู้ใช้:", width=15)
        self.user_label.pack(side=tk.LEFT)
        self.username_entry = ttk.Entry(user_frame, width=35)
        self.username_entry.pack(side=tk.LEFT, padx=10)
        
        # Password (for SQL auth)
        pass_frame = ttk.Frame(settings_frame)
        pass_frame.pack(fill=tk.X, pady=5)
        self.pass_label = ttk.Label(pass_frame, text="รหัสผ่าน:", width=15)
        self.pass_label.pack(side=tk.LEFT)
        self.password_entry = ttk.Entry(pass_frame, width=35, show="*")
        self.password_entry.pack(side=tk.LEFT, padx=10)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        # Center the buttons
        center_button_frame = ttk.Frame(button_frame)
        center_button_frame.pack(expand=True)
        
        # Test connection button
        test_btn = ttk.Button(center_button_frame, text="ทดสอบการเชื่อมต่อ (Test)", 
                             command=self.test_db_connection, width=25)
        test_btn.pack(side=tk.LEFT, padx=10)
        
        # Check drivers button
        drivers_btn = ttk.Button(center_button_frame, text="ตรวจสอบ Drivers", 
                                command=self.check_drivers, width=20)
        drivers_btn.pack(side=tk.LEFT, padx=5)
        
        # Login button
        login_btn = ttk.Button(center_button_frame, text="เข้าสู่ระบบ (Login)", 
                              command=self.login, width=25)
        login_btn.pack(side=tk.LEFT, padx=10)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="กรุณาใส่ข้อมูลการเชื่อมต่อและกดปุ่ม 'เข้าสู่ระบบ'", 
                                     foreground="blue")
        self.status_label.pack(pady=10)
        
        # Progress bar (hidden initially)
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        
        # Additional options frame
        options_frame = ttk.LabelFrame(main_frame, text="ตัวเลือกเพิ่มเติม", padding=10)
        options_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Remember settings checkbox
        self.remember_var = tk.BooleanVar(value=True)
        remember_check = ttk.Checkbutton(options_frame, text="จำการตั้งค่าไว้", 
                                        variable=self.remember_var)
        remember_check.pack(anchor=tk.W)
        
        # Auto-login checkbox
        self.auto_login_var = tk.BooleanVar(value=False)
        auto_login_check = ttk.Checkbutton(options_frame, text="เข้าสู่ระบบอัตโนมัติ", 
                                          variable=self.auto_login_var)
        auto_login_check.pack(anchor=tk.W)
        
        # Instructions label
        instructions_label = ttk.Label(main_frame, text="คำแนะนำ: กรุณาใส่ข้อมูลการเชื่อมต่อแล้วกดปุ่ม 'เข้าสู่ระบบ (Login)'", 
                                     foreground="green", font=("Arial", 10, "bold"))
        instructions_label.pack(pady=10)
        
        # Button reminder label
        button_reminder = ttk.Label(main_frame, text="ปุ่มอยู่ด้านล่าง: [ทดสอบการเชื่อมต่อ (Test)] และ [เข้าสู่ระบบ (Login)]", 
                                   foreground="red", font=("Arial", 9))
        button_reminder.pack(pady=5)
        
        # Force update to ensure buttons are visible
        self.root.update_idletasks()
    
    def load_settings_to_ui(self):
        """โหลดการตั้งค่าลง UI"""
        if self.config:
            self.server_entry.delete(0, tk.END)
            self.server_entry.insert(0, self.config.get('server', ''))
            
            self.database_entry.delete(0, tk.END)
            self.database_entry.insert(0, self.config.get('database', ''))
            
            self.auth_var.set(self.config.get('auth_type', 'Windows'))
            
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, self.config.get('username', ''))
            
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, self.config.get('password', ''))
            
            self.on_auth_change()
    
    def on_auth_change(self, event=None):
        """เมื่อเปลี่ยนประเภทการยืนยันตัวตน"""
        auth_type = self.auth_var.get()
        if auth_type == "Windows":
            # ซ่อนช่องผู้ใช้และรหัสผ่าน
            self.user_label.pack_forget()
            self.username_entry.pack_forget()
            self.pass_label.pack_forget()
            self.password_entry.pack_forget()
        else:
            # แสดงช่องผู้ใช้และรหัสผ่าน
            self.user_label.pack(side=tk.LEFT)
            self.username_entry.pack(side=tk.LEFT, padx=10)
            self.pass_label.pack(side=tk.LEFT)
            self.password_entry.pack(side=tk.LEFT, padx=10)
    
    def test_db_connection(self):
        """ทดสอบการเชื่อมต่อฐานข้อมูล"""
        # อัพเดทการตั้งค่าชั่วคราว
        temp_config = {
            'server': self.server_entry.get().strip(),
            'database': self.database_entry.get().strip(),
            'auth_type': self.auth_var.get(),
            'username': self.username_entry.get().strip(),
            'password': self.password_entry.get()
        }
        
        # ตรวจสอบข้อมูลที่จำเป็น
        if not temp_config['server']:
            messagebox.showwarning("คำเตือน", "กรุณาใส่ชื่อเซิร์ฟเวอร์")
            return
        
        if not temp_config['database']:
            messagebox.showwarning("คำเตือน", "กรุณาใส่ชื่อฐานข้อมูล")
            return
        
        if temp_config['auth_type'] == "SQL":
            if not temp_config['username']:
                messagebox.showwarning("คำเตือน", "กรุณาใส่ชื่อผู้ใช้")
                return
            if not temp_config['password']:
                messagebox.showwarning("คำเตือน", "กรุณาใส่รหัสผ่าน")
                return
        
        # แสดง progress bar
        self.progress.pack(pady=5)
        self.progress.start()
        self.status_label.config(text="กำลังทดสอบการเชื่อมต่อ...", foreground="blue")
        self.root.update()
        
        # สร้าง connection string ชั่วคราว
        original_config = self.config.copy() if self.config else {}
        original_connection = self.connection_string
        
        try:
            self.config = temp_config
            self.update_connection_string()
            
            if self.test_connection():
                self.status_label.config(text="✓ เชื่อมต่อสำเร็จ", foreground="green")
                messagebox.showinfo("สำเร็จ", "ทดสอบการเชื่อมต่อสำเร็จ!")
            else:
                self.status_label.config(text="✗ เชื่อมต่อไม่สำเร็จ", foreground="red")
                messagebox.showerror("ข้อผิดพลาด", "ไม่สามารถเชื่อมต่อฐานข้อมูลได้")
        
        except Exception as e:
            self.status_label.config(text="✗ เกิดข้อผิดพลาด", foreground="red")
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")
        
        finally:
            # ซ่อน progress bar
            self.progress.stop()
            self.progress.pack_forget()
            
            # คืนค่าการตั้งค่าเดิม
            self.config = original_config
            self.connection_string = original_connection
    
    def login(self):
        """เข้าสู่ระบบ"""
        # อัพเดทการตั้งค่า
        new_config = {
            'server': self.server_entry.get().strip(),
            'database': self.database_entry.get().strip(),
            'auth_type': self.auth_var.get(),
            'username': self.username_entry.get().strip(),
            'password': self.password_entry.get()
        }
        
        # ตรวจสอบข้อมูลที่จำเป็น
        if not new_config['server']:
            messagebox.showwarning("คำเตือน", "กรุณาใส่ชื่อเซิร์ฟเวอร์")
            return
        
        if not new_config['database']:
            messagebox.showwarning("คำเตือน", "กรุณาใส่ชื่อฐานข้อมูล")
            return
        
        if new_config['auth_type'] == "SQL":
            if not new_config['username']:
                messagebox.showwarning("คำเตือน", "กรุณาใส่ชื่อผู้ใช้")
                return
            if not new_config['password']:
                messagebox.showwarning("คำเตือน", "กรุณาใส่รหัสผ่าน")
                return
        
        # แสดง progress bar
        self.progress.pack(pady=5)
        self.progress.start()
        self.status_label.config(text="กำลังเชื่อมต่อ...", foreground="blue")
        self.root.update()
        
        try:
            # อัพเดทการตั้งค่า
            self.config = new_config
            self.update_connection_string()
            
            # ทดสอบการเชื่อมต่อ
            if not self.test_connection():
                self.status_label.config(text="✗ เชื่อมต่อไม่สำเร็จ", foreground="red")
                messagebox.showerror("ข้อผิดพลาด", "ไม่สามารถเชื่อมต่อฐานข้อมูลได้")
                return
            
            # บันทึกการตั้งค่าถ้าต้องการ
            if self.remember_var.get():
                self.save_config()
            
            # เก็บข้อมูลการเชื่อมต่อสำหรับส่งไปยังโปรแกรมหลัก
            self.connection_info = {
                'connection_string': self.connection_string,
                'current_user': self.current_user,
                'config': self.config.copy()
            }
            
            self.status_label.config(text="✓ เข้าสู่ระบบสำเร็จ", foreground="green")
            
            # ปิดหน้าต่าง login อย่างถูกต้อง
            self.root.destroy()
            
        except Exception as e:
            self.status_label.config(text="✗ เกิดข้อผิดพลาด", foreground="red")
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการเข้าสู่ระบบ: {str(e)}")
        
        finally:
            # ซ่อน progress bar (ตรวจสอบว่า window ยังมีอยู่หรือไม่)
            try:
                if hasattr(self, 'progress') and self.progress.winfo_exists():
                    self.progress.stop()
                    self.progress.pack_forget()
            except tk.TclError:
                # Window ถูกทำลายไปแล้ว ไม่ต้องทำอะไร
                pass
    
    def run(self) -> Optional[Dict[str, Any]]:
        """รันหน้าต่าง login และส่งคืนข้อมูลการเชื่อมต่อ"""
        self.root.mainloop()
        
        # ตรวจสอบว่ามีข้อมูลการเชื่อมต่อหรือไม่
        if hasattr(self, 'connection_info'):
            return self.connection_info
        else:
            return None

def main():
    """Main function for testing"""
    login = LoginWindow()
    result = login.run()
    
    if result:
        print("Login successful!")
        print(f"User: {result['current_user']}")
        print(f"Server: {result['config']['server']}")
        print(f"Database: {result['config']['database']}")
    else:
        print("Login cancelled or failed")

if __name__ == "__main__":
    main() 