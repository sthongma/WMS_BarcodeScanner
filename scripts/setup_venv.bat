@echo off
REM ===================================================================
REM WMS Barcode Scanner - Virtual Environment Setup (Windows)
REM ===================================================================
REM This script creates and configures a Python virtual environment
REM for the Desktop application.
REM ===================================================================

echo ========================================
echo WMS Barcode Scanner - Virtual Environment Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Checking Python version...
python --version

REM Check if .venv already exists
if exist ".venv" (
    echo.
    echo [WARNING] Virtual environment already exists at .venv
    echo.
    set /p RECREATE="Do you want to recreate it? (y/N): "
    if /i not "%RECREATE%"=="y" (
        echo Setup cancelled.
        pause
        exit /b 0
    )
    echo Removing existing virtual environment...
    rmdir /s /q .venv
)

echo.
echo [2/5] Creating virtual environment at .venv...
python -m venv .venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

echo.
echo [3/5] Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo [4/5] Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo [WARNING] Failed to upgrade pip, continuing anyway...
)

echo.
echo [5/5] Installing production dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo To activate the virtual environment, run:
echo   .venv\Scripts\activate.bat
echo.
echo Or use the convenience script:
echo   scripts\activate_dev.bat
echo.
echo To install development dependencies:
echo   pip install -r requirements-dev.txt
echo.
echo To run the Desktop application:
echo   python run.py
echo.

pause
