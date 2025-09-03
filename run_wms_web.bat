@echo off
chcp 65001 >nul
title WMS Barcode Scanner - Web Application

echo ========================================
echo    WMS Barcode Scanner Web Application
echo ========================================
echo.

:: ตรวจสอบว่า Python ติดตั้งแล้วหรือไม่
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] ไม่พบ Python ในระบบ
    echo กรุณาติดตั้ง Python จาก https://www.python.org/downloads/
    echo อย่าลืมเลือก "Add Python to PATH" ตอนติดตั้ง
    pause
    exit /b 1
)

echo [INFO] พบ Python ในระบบแล้ว
echo.

:: ตรวจสอบว่าไฟล์ requirements.txt มีอยู่หรือไม่
if not exist "requirements.txt" (
    echo [ERROR] ไม่พบไฟล์ requirements.txt
    echo กรุณาตรวจสอบว่าไฟล์อยู่ในโฟลเดอร์ที่ถูกต้อง
    pause
    exit /b 1
)

:: ตรวจสอบว่าไฟล์ run_web.py มีอยู่หรือไม่
if not exist "run_web.py" (
    echo [ERROR] ไม่พบไฟล์ run_web.py
    echo กรุณาตรวจสอบว่าไฟล์อยู่ในโฟลเดอร์ที่ถูกต้อง
    pause
    exit /b 1
)

echo [INFO] กำลังตรวจสอบและติดตั้ง dependencies...
echo.

:: ติดตั้ง dependencies
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] ไม่สามารถติดตั้ง dependencies ได้
    echo กรุณาตรวจสอบการเชื่อมต่ออินเทอร์เน็ตและลองใหม่อีกครั้ง
    pause
    exit /b 1
)

echo.
echo [INFO] Dependencies ติดตั้งเสร็จแล้ว
echo [INFO] กำลังเริ่ม WMS Web Server...
echo.
echo ========================================
echo    เข้าใช้งานได้ที่:
echo    http://localhost:5003
echo    http://127.0.0.1:5003
echo.
echo    สำหรับ Mobile/Android:
echo    http://[IP_ADDRESS]:5003
echo    (แทน [IP_ADDRESS] ด้วย IP ของเครื่องนี้)
echo ========================================
echo.
echo [INFO] กด Ctrl+C เพื่อหยุดเซิร์ฟเวอร์
echo [INFO] ปิดหน้าต่างนี้เพื่อหยุดโปรแกรม
echo.

:: รัน web server
python run_web.py

echo.
echo [INFO] Web Server หยุดทำงานแล้ว
pause