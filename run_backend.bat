@echo off
title TrustLens Backend Server
cd /d "%~dp0backend"
echo ========================================================
echo Starting TrustLens Backend (FastAPI + Uvicorn)
echo API Docs: http://127.0.0.1:8000/docs
echo ========================================================
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
