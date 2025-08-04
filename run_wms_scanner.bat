@echo off
chcp 65001 >nul
title WMS Barcode Scanner

echo ========================================
echo    WMS Barcode Scanner Application
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

:: ตรวจสอบว่าไฟล์ run.py มีอยู่หรือไม่
if not exist "run.py" (
    echo [ERROR] ไม่พบไฟล์ run.py
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
echo [INFO] กำลังเริ่มโปรแกรม WMS Barcode Scanner ในพื้นหลัง...
echo [INFO] โปรแกรมจะทำงานในพื้นหลัง
echo [INFO] สามารถปิดโปรแกรมได้จาก Task Manager หรือ System Tray
echo.

:: รันโปรแกรมแบบซ่อนหน้าต่าง
start /min python run.py

echo [INFO] โปรแกรมเริ่มทำงานแล้วในพื้นหลัง
timeout /t 1 /nobreak >nul
exit
