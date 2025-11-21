@echo off
echo ========================================
echo Starting Cloudflare Tunnel for WMS App
echo ========================================
echo.

REM Check if cloudflared is installed
where cloudflared >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: cloudflared is not installed or not in PATH
    echo Please install cloudflared first. See CLOUDFLARE_TUNNEL_SETUP.md
    pause
    exit /b 1
)

REM Check if config file exists
if not exist "%~dp0cloudflare\config.yml" (
    echo ERROR: config.yml not found
    echo Please run setup first. See CLOUDFLARE_TUNNEL_SETUP.md
    pause
    exit /b 1
)

echo Starting tunnel...
cloudflared tunnel --config "%~dp0cloudflare\config.yml" run

pause
