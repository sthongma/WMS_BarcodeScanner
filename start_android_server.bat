@echo off
chcp 65001 >nul
title WMS Barcode Scanner - Android Server

REM Change directory to batch file location
cd /d "%~dp0"

echo.
echo ========================================
echo    WMS Barcode Scanner for Android
echo ========================================
echo.

echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python first.
    pause
    exit /b 1
)

echo Python found successfully
echo.

echo Installing Dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo WARNING: Some errors occurred while installing Dependencies
    echo TIP: Try installing them one by one...
    
    echo Installing Flask...
    pip install flask>=2.3.0 flask-cors>=4.0.0
    if errorlevel 1 (
        echo ERROR: Cannot install Flask
        pause
        exit /b 1
    )
    
    echo Installing QR Code...
    pip install qrcode[pil]>=7.4.0
    if errorlevel 1 (
        echo WARNING: Cannot install QR Code (optional)
    )
    
    echo Installing Utilities...
    pip install typing-extensions>=4.0.0
    if errorlevel 1 (
        echo WARNING: Cannot install Utilities (optional)
    )
)

echo Dependencies installed successfully
echo.

echo Showing IP Address of this machine...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set ip=%%a
    set ip=!ip: =!
    echo IP Address: !ip!
    echo URL for Android: http://!ip!:5000
)

echo.
echo Starting Web Server...
echo Accessible at: http://localhost:5000
echo For Android: http://[IP_ADDRESS]:5000
echo.
echo TIP: Press Ctrl+C to stop
echo.

python web_app.py

pause 