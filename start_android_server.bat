@echo off
chcp 65001 >nul
title WMS Barcode Scanner - Android Server

echo.
echo ========================================
echo    WMS Barcode Scanner สำหรับ Android
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

echo 📦 กำลังติดตั้ง Dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ⚠️  มีข้อผิดพลาดในการติดตั้ง Dependencies บางตัว
    echo 💡 ลองติดตั้งทีละตัว...
    
    echo 📦 ติดตั้ง Flask...
    pip install flask>=2.3.0 flask-cors>=4.0.0
    if errorlevel 1 (
        echo ❌ ไม่สามารถติดตั้ง Flask ได้
        pause
        exit /b 1
    )
    
    echo 📦 ติดตั้ง QR Code...
    pip install qrcode[pil]>=7.4.0
    if errorlevel 1 (
        echo ⚠️ ไม่สามารถติดตั้ง QR Code ได้ (ไม่บังคับ)
    )
    
    echo 📦 ติดตั้ง Utilities...
    pip install typing-extensions>=4.0.0
    if errorlevel 1 (
        echo ⚠️ ไม่สามารถติดตั้ง Utilities ได้ (ไม่บังคับ)
    )
)

echo ✅ ติดตั้ง Dependencies สำเร็จ
echo.

echo 🌐 กำลังแสดง IP Address ของเครื่อง...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set ip=%%a
    set ip=!ip: =!
    echo 📱 IP Address: !ip!
    echo 📱 URL สำหรับ Android: http://!ip!:5000
)

echo.
echo 🚀 กำลังเริ่มต้น Web Server...
echo 📱 สามารถเข้าถึงได้ที่: http://localhost:5000
echo 📱 สำหรับ Android: http://[IP_ADDRESS]:5000
echo.
echo 💡 กด Ctrl+C เพื่อหยุดการทำงาน
echo.

python web_app.py

pause 