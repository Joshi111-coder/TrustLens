@echo off
title TrustLens Frontend Server
cd /d "%~dp0frontend"
set "PATH=C:\Users\shubh\nodejs;%PATH%"
echo ========================================================
echo Starting TrustLens Frontend (Vite + React)
echo URL: http://localhost:5173
echo ========================================================
npm run dev -- --host 127.0.0.1 --port 5173
pause
