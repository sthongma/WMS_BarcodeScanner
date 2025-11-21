@echo off
echo ========================================
echo Starting WMS App with Quick Tunnel
echo ========================================
echo.
echo กำลังรัน WMS Web App และ Cloudflare Quick Tunnel...
echo URL จะแสดงด้านล่างนี้ (ประมาณ 5-10 วินาที)
echo.

REM Check if cloudflared is installed
where cloudflared >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: cloudflared is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if WMS is running on port 5003
netstat -ano | findstr :5003 >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo WMS Web App ไม่ได้รันอยู่!
    echo กำลังเปิด WMS Web App...
    start "WMS Web App" cmd /k "python run_web.py"
    timeout /t 5 /nobreak >nul
)

echo.
echo ========================================
echo กำลังเชื่อมต่อ Cloudflare Quick Tunnel...
echo ========================================
echo.

cloudflared tunnel --url http://localhost:5003

pause
