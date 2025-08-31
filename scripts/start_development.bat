@echo off
REM WMS Barcode Scanner - Development Startup Script
REM For testing and development purposes

echo ========================================
echo  WMS Barcode Scanner - Development Mode
echo ========================================

REM Change to project root directory
cd /d "%~dp0\.."

REM Create logs directory
if not exist logs mkdir logs

REM Set environment variables
set FLASK_ENV=development
set WMS_ENV=development
set PYTHONPATH=%CD%\src

echo [1/2] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [2/2] Starting WMS application in development mode...
echo.
echo Server will be available at:
echo   http://localhost:5003
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start with Flask development server
python run_web.py

echo.
echo Server stopped.
pause