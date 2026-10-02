@echo off
title TrustLens Launcher
echo ========================================================
echo Launching TrustLens Financial Verification Assistant
echo ========================================================
echo.
echo 1. Launching Backend on port 8000...
start "TrustLens Backend" cmd /c "%~dp0run_backend.bat"

echo 2. Launching Frontend on port 5173...
start "TrustLens Frontend" cmd /c "%~dp0run_frontend.bat"

echo.
echo Both servers are launching in separate windows!
echo Once started, open: http://localhost:5173
echo.
timeout /t 3 >nul
start http://localhost:5173
exit
