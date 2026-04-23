@echo off
cd /d "%~dp0backend"
echo Starting VeriClip AI Backend...
echo API Docs: http://localhost:8001/docs
echo Health Check: http://localhost:8001/api/v1/health
echo.
%~dp0.venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
