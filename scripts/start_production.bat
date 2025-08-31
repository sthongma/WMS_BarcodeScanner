@echo off
REM WMS Barcode Scanner - Production Startup Script
REM Phase 1 Production-Ready Configuration

echo ========================================
echo  WMS Barcode Scanner - Production Mode
echo ========================================

REM Change to project root directory
cd /d "%~dp0\.."

REM Create logs directory
if not exist logs mkdir logs

REM Set environment variables
set FLASK_ENV=production
set WMS_ENV=production
set PYTHONPATH=%CD%\src

echo [1/3] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [2/3] Starting Redis server (if not running)...
REM Check if Redis is running on default port
netstat -an | find "6379" >nul
if errorlevel 1 (
    echo Starting Redis server...
    start "Redis Server" redis-server
    timeout /t 3
) else (
    echo Redis server already running
)

echo [3/3] Starting WMS application in Production Mode...
echo.
echo Server will be available at:
echo   http://localhost:5003
echo   http://[YOUR_IP]:5003
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start with Flask in production mode (Gunicorn not supported on Windows)
python run_web.py

echo.
echo Server stopped.
pause