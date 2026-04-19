@echo off
title LAZPOOL Server
color 0B

cd /d "%~dp0"

echo.
echo  ================================================
echo    LAZPOOL v2.0
echo  ================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo  Python not found. Install from https://python.org
    pause
    exit /b 1
)

echo  Starting servers...
echo  App:   http://localhost:3000
echo  Proxy: http://localhost:3001  (internal)
echo.
echo  Minimize this window. Press Ctrl+C to stop.
echo  ================================================
echo.

REM Open browser after 1.5s
start "" /b cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:3000"

REM Run server
python server.py
pause
