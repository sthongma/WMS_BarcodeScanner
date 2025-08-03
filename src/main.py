#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WMS Barcode Scanner Application
Main entry point for the application
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
from typing import Optional, Dict, Any

# Add src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.login_window import LoginWindow
from ui.main_window import WMSScannerApp


def main():
    """จุดเริ่มต้นของโปรแกรม"""
    try:
        # สร้าง root window สำหรับ login
        root = tk.Tk()
        root.withdraw()  # ซ่อน root window
        
        # แสดงหน้าต่าง login
        login_window = LoginWindow()
        connection_info = login_window.run()
        
        if connection_info:
            # ปิด root window เดิม
            root.destroy()
            
            # สร้าง root window ใหม่สำหรับ main application
            main_root = tk.Tk()
            main_root.title("WMS Barcode Scanner")
            main_root.geometry("1200x800")
            
            # สร้าง main application
            app = WMSScannerApp(main_root, connection_info)
            
            # เริ่ม main loop
            main_root.mainloop()
        else:
            # ปิดโปรแกรมถ้าไม่มีการเชื่อมต่อ
            root.destroy()
            sys.exit(0)
            
    except Exception as e:
        messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการเริ่มโปรแกรม: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 