@echo off
echo Starting WMS Barcode Scanner in Production Mode...
echo.

REM Change to script directory
cd /d "%~dp0"

REM Set environment variables
set FLASK_ENV=production
set PYTHONPATH=%CD%

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import flask, pyodbc" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Required packages not installed. Please run: pip install flask pyodbc flask-cors
    pause
    exit /b 1
)

echo Starting server...
echo You can access the application at:
echo - Local: http://localhost:5000
echo - Network: http://[YOUR_IP]:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python run_production.py

pause