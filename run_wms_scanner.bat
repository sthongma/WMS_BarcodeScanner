@echo off
chcp 65001 >nul
title WMS Barcode Scanner - Desktop Application

echo ========================================
echo    WMS Barcode Scanner - Desktop App
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo [WARNING] Virtual environment not found at .venv
    echo.
    echo Please run setup first:
    echo   scripts\setup_venv.bat
    echo.
    set /p SETUP="Do you want to run setup now? (Y/n): "
    if /i not "%SETUP%"=="n" (
        echo.
        echo Running setup...
        call scripts\setup_venv.bat
        if errorlevel 1 (
            echo.
            echo [ERROR] Setup failed
            pause
            exit /b 1
        )
    ) else (
        echo.
        echo [ERROR] Cannot run without virtual environment
        pause
        exit /b 1
    )
)

echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat

if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

echo [INFO] Virtual environment activated
echo.

REM Check if run.py exists
if not exist "run.py" (
    echo [ERROR] run.py not found
    echo Please make sure you're in the correct directory
    pause
    exit /b 1
)

echo [INFO] Starting WMS Barcode Scanner Desktop Application...
echo.

REM Run the application
python run.py

REM Deactivate virtual environment when done
deactivate

echo.
echo [INFO] Application closed
pause
