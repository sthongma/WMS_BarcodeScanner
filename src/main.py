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
from PIL import Image, ImageTk

# Use relative imports (run.py handles path setup)
from .ui.login_window import LoginWindow
from .ui.main_window import WMSScannerApp


def set_app_icon(root):
    """ตั้งค่า icon สำหรับแอพ"""
    try:
        # พยายามโหลด icon จากไฟล์ PNG
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icons', 'app_icon.png')
        
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
            root.iconphoto(True, *icons)
            
            # ตั้งค่า icon สำหรับ taskbar (Windows)
            if hasattr(root, 'iconbitmap'):
                try:
                    # สร้างไฟล์ ICO ชั่วคราว
                    temp_ico_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icons', 'temp_icon.ico')
                    image.save(temp_ico_path, format='ICO', sizes=icon_sizes)
                    root.iconbitmap(temp_ico_path)
                    
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


def main():
    """จุดเริ่มต้นของโปรแกรม"""
    try:
        # แสดงหน้าต่าง login
        login_window = LoginWindow()
        connection_info = login_window.run()
        
        if connection_info:
            # สร้าง root window ใหม่สำหรับ main application
            main_root = tk.Tk()
            main_root.title("WMS Barcode Scanner")
            main_root.geometry("1200x800")
            
            # ตั้งค่า icon สำหรับแอพ
            set_app_icon(main_root)
            
            # สร้าง main application
            app = WMSScannerApp(main_root, connection_info)
            
            # เริ่ม main loop
            main_root.mainloop()
        else:
            # ปิดโปรแกรมถ้าไม่มีการเชื่อมต่อ
            sys.exit(0)
            
    except Exception as e:
        messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการเริ่มโปรแกรม: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 