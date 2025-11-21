@echo off
echo ========================================
echo Starting WMS App + Cloudflare Tunnel
echo ========================================
echo.

REM Start WMS Web App in a new window
echo [1/2] Starting WMS Web App on port 5003...
start "WMS Web App" cmd /k "python run_web.py"

REM Wait a bit for web app to start
timeout /t 3 /nobreak >nul

REM Start Cloudflare Tunnel in current window
echo [2/2] Starting Cloudflare Tunnel...
echo.
cloudflared tunnel --config "%~dp0cloudflare\config.yml" run

pause
