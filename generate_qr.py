#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QR Code Generator สำหรับ WMS Barcode Scanner
สร้าง QR Code เพื่อให้ Android เข้าถึงแอปพลิเคชันได้ง่าย
"""

import qrcode
import socket
import os
import sys

def get_local_ip():
    """ดึง IP Address ของเครื่อง"""
    try:
        # เชื่อมต่อกับ DNS server เพื่อดึง IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

def generate_qr_code(url, filename="wms_scanner_qr.png"):
    """สร้าง QR Code"""
    try:
        # สร้าง QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        # สร้างภาพ
        img = qr.make_image(fill_color="black", back_color="white")
        
        # บันทึกไฟล์
        img.save(filename)
        
        print(f"✅ สร้าง QR Code สำเร็จ: {filename}")
        print(f"📱 URL: {url}")
        print(f"📱 สแกน QR Code ด้วยมือถือเพื่อเข้าถึงแอป")
        
        return True
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการสร้าง QR Code: {e}")
        return False

def main():
    """ฟังก์ชันหลัก"""
    print("🎯 WMS Barcode Scanner - QR Code Generator")
    print("=" * 50)
    
    # ดึง IP Address
    ip = get_local_ip()
    url = f"http://{ip}:5000"
    
    print(f"🌐 IP Address: {ip}")
    print(f"📱 URL: {url}")
    print()
    
    # สร้าง QR Code
    if generate_qr_code(url):
        print()
        print("💡 วิธีใช้งาน:")
        print("1. เปิดแอป Camera บน Android")
        print("2. สแกน QR Code ที่สร้างขึ้น")
        print("3. กดลิงก์ที่ปรากฏเพื่อเข้าถึงแอป")
        print()
        print("🔧 หรือเปิดเว็บเบราว์เซอร์และเข้าไปที่ URL ข้างต้น")
    else:
        print("❌ ไม่สามารถสร้าง QR Code ได้")
        print("💡 ลองติดตั้ง qrcode library:")
        print("   pip install qrcode[pil]")

if __name__ == "__main__":
    main() 