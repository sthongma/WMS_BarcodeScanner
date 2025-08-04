@echo off
chcp 65001 >nul
title WMS Barcode Scanner Launcher

:menu
cls
echo ========================================
echo      WMS Barcode Scanner Launcher
echo ========================================
echo.
echo เลือกประเภทการใช้งาน:
echo.
echo [1] Desktop Application (GUI)
echo     - ใช้งานบนคอมพิวเตอร์
echo     - มีหน้าต่าง GUI แบบเต็มรูปแบบ
echo.
echo [2] Web Application (Android)
echo     - ใช้งานบน Android ผ่านเว็บเบราว์เซอร์
echo     - เข้าถึงได้จาก http://localhost:5000
echo.
echo [3] ออกจากโปรแกรม
echo.
echo ========================================
echo.

set /p choice="กรุณาเลือก (1-3): "

if "%choice%"=="1" goto desktop
if "%choice%"=="2" goto web
if "%choice%"=="3" goto exit
echo.
echo [ERROR] กรุณาเลือก 1, 2 หรือ 3 เท่านั้น
timeout /t 2 >nul
goto menu

:desktop
echo.
echo [INFO] กำลังเริ่ม Desktop Application...
call run_wms_scanner.bat
goto menu

:web
echo.
echo [INFO] กำลังเริ่ม Web Application...
call start_android_server.bat
goto menu

:exit
echo.
echo [INFO] ขอบคุณที่ใช้งาน WMS Barcode Scanner
timeout /t 2 >nul
exit 