@echo off
REM ===================================================================
REM WMS Barcode Scanner - Docker Stop (Windows)
REM ===================================================================

echo ========================================
echo WMS Barcode Scanner - Stopping Containers
echo ========================================
echo.

docker-compose down

echo.
echo Containers stopped successfully!
echo.

pause
