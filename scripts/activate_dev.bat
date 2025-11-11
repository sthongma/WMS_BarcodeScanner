@echo off
REM ===================================================================
REM WMS Barcode Scanner - Activate Development Environment (Windows)
REM ===================================================================
REM This script activates the virtual environment and optionally
REM installs development dependencies.
REM ===================================================================

echo ========================================
echo WMS Barcode Scanner - Development Environment
echo ========================================
echo.

REM Check if .venv exists
if not exist ".venv" (
    echo [ERROR] Virtual environment not found at .venv
    echo.
    echo Please run setup first:
    echo   scripts\setup_venv.bat
    echo.
    pause
    exit /b 1
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Virtual environment activated!
echo Python location:
where python
echo.

REM Check if dev dependencies are installed
python -c "import pytest" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Development dependencies not found.
    set /p INSTALL_DEV="Install development dependencies? (Y/n): "
    if /i not "%INSTALL_DEV%"=="n" (
        echo.
        echo Installing development dependencies...
        pip install -r requirements-dev.txt
        echo.
        echo Development dependencies installed!
    )
)

echo.
echo ========================================
echo Ready for development!
echo ========================================
echo.
echo Available commands:
echo   python run.py              - Run Desktop App
echo   pytest                     - Run tests
echo   pytest --cov=src           - Run tests with coverage
echo   black src/ tests/          - Format code
echo   flake8 src/ tests/         - Lint code
echo   mypy src/                  - Type check
echo.
echo To deactivate: deactivate
echo.

REM Keep the shell open with virtual environment activated
cmd /k
