@echo off
echo =====================================================================
echo  AI-Based Student Grievance Classification & Smart Routing System
echo  Starting FastAPI Monolith Server on http://127.0.0.1:8000
echo =====================================================================
cd /d "%~dp0backend"
set PYTHONPATH=%~dp0backend
"%~dp0backend\venv\Scripts\uvicorn.exe" app.main:app --host 127.0.0.1 --port 8000 --reload
pause
