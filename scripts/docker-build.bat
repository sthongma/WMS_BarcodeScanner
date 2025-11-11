@echo off
REM ===================================================================
REM WMS Barcode Scanner - Docker Build Script (Windows)
REM ===================================================================

echo ========================================
echo WMS Barcode Scanner - Docker Build
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)

echo [INFO] Building Docker image...
echo.

REM Build the image
docker build -t wms-barcode-scanner-web:latest .

if errorlevel 1 (
    echo.
    echo [ERROR] Docker build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Image: wms-barcode-scanner-web:latest
echo.
echo Next steps:
echo   Development: scripts\docker-run-dev.bat
echo   Production:  scripts\docker-run-prod.bat
echo.

pause
