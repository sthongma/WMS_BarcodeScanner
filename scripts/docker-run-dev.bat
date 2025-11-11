@echo off
REM ===================================================================
REM WMS Barcode Scanner - Docker Run Development (Windows)
REM ===================================================================

echo ========================================
echo WMS Barcode Scanner - Development Mode
echo ========================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found
    echo.
    echo Creating .env from .env.example...
    copy .env.example .env
    echo.
    echo [IMPORTANT] Please edit .env file with your database configuration
    echo Then run this script again.
    echo.
    pause
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)

echo [INFO] Starting development environment...
echo.
echo Features:
echo   - Hot-reload enabled
echo   - Debug mode ON
echo   - Source code mounted for live editing
echo   - Logs persisted to ./logs
echo.

REM Run docker-compose (automatically uses docker-compose.override.yml)
docker-compose up

REM Note: docker-compose up will run in foreground
REM Press Ctrl+C to stop
