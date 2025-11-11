@echo off
REM ===================================================================
REM WMS Barcode Scanner - Docker Run Production (Windows)
REM ===================================================================

echo ========================================
echo WMS Barcode Scanner - Production Mode
echo ========================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo [ERROR] .env file not found
    echo Please create .env file from .env.example
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

echo [INFO] Starting production environment...
echo.
echo Features:
echo   - Optimized build
echo   - Debug mode OFF
echo   - Resource limits enabled
echo   - Auto-restart on failure
echo   - Logs persisted to ./logs
echo.

set /p CONFIRM="Are you sure you want to run in PRODUCTION mode? (y/N): "
if /i not "%CONFIRM%"=="y" (
    echo Cancelled.
    pause
    exit /b 0
)

echo.
echo Starting containers...

REM Run docker-compose with production config
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start containers
    pause
    exit /b 1
)

echo.
echo ========================================
echo Production environment started!
echo ========================================
echo.
echo Access the application at:
echo   http://localhost:5000
echo.
echo To view logs:
echo   docker-compose logs -f wms-web
echo.
echo To stop:
echo   scripts\docker-stop.bat
echo.

pause
