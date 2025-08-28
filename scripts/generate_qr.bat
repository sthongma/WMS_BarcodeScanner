@echo off
chcp 65001 >nul
title WMS Barcode Scanner - QR Code Generator

echo.
echo ========================================
echo    QR Code Generator สำหรับ Android
echo ========================================
echo.

echo 🔍 กำลังตรวจสอบ Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ไม่พบ Python กรุณาติดตั้ง Python ก่อน
    pause
    exit /b 1
)

echo ✅ พบ Python แล้ว
echo.

echo 📦 กำลังติดตั้ง QR Code Library...
pip install qrcode[pil]
if errorlevel 1 (
    echo ❌ เกิดข้อผิดพลาดในการติดตั้ง QR Code Library
    pause
    exit /b 1
)

echo ✅ ติดตั้ง QR Code Library สำเร็จ
echo.

echo 🎯 กำลังสร้าง QR Code...
python generate_qr.py

echo.
echo 💡 ไฟล์ QR Code จะถูกสร้างในโฟลเดอร์ปัจจุบัน
echo 💡 เปิดไฟล์ wms_scanner_qr.png เพื่อดู QR Code
echo.

pause 