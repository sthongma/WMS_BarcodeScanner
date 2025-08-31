@echo off
REM Redis Installation Script for Windows
REM Downloads and sets up Redis for WMS Barcode Scanner

echo ========================================
echo  Redis Installation for Windows
echo ========================================

echo.
echo This script will help you install Redis on Windows.
echo Redis is required for optimal session management and performance.
echo.

REM Check if Redis is already installed
redis-server --version >nul 2>&1
if not errorlevel 1 (
    echo Redis is already installed and available in PATH.
    redis-server --version
    echo.
    echo To start Redis manually, run: redis-server
    pause
    exit /b 0
)

echo Redis not found in PATH. Installation options:
echo.
echo 1. Install using Chocolatey (Recommended):
echo    choco install redis-64
echo.
echo 2. Install using Windows Subsystem for Linux (WSL):
echo    wsl --install
echo    wsl sudo apt-get install redis-server
echo.
echo 3. Download Redis for Windows from:
echo    https://github.com/MicrosoftArchive/redis/releases
echo.
echo 4. Use Redis Cloud (external service):
echo    https://redis.com/redis-enterprise-cloud/
echo.

choice /c 1234 /m "Select installation method"
if errorlevel 4 goto cloud
if errorlevel 3 goto manual
if errorlevel 2 goto wsl  
if errorlevel 1 goto chocolatey

:chocolatey
echo Installing Redis using Chocolatey...
choco install redis-64
if errorlevel 1 (
    echo Failed to install with Chocolatey. Please install Chocolatey first:
    echo https://chocolatey.org/install
) else (
    echo Redis installed successfully!
    echo Starting Redis service...
    redis-server --service-install
    redis-server --service-start
)
goto end

:wsl
echo Installing Redis in WSL...
echo Please run the following commands in WSL:
echo   sudo apt-get update
echo   sudo apt-get install redis-server
echo   sudo service redis-server start
goto end

:manual
echo Please download Redis from:
echo https://github.com/MicrosoftArchive/redis/releases
echo.
echo Extract and run redis-server.exe
goto end

:cloud
echo For Redis Cloud setup, please:
echo 1. Sign up at https://redis.com/redis-enterprise-cloud/
echo 2. Create a database
echo 3. Update your config with the connection URL
goto end

:end
echo.
echo Installation guide completed.
pause