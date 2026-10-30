@echo off
title AI-SGC System Launcher
echo =====================================================================
echo  AI-Based Student Grievance Classification ^& Smart Routing System
echo  Starting FastAPI Backend and React Frontend...
echo =====================================================================

start "AI-SGC Backend [Port 8000]" cmd /k "%~dp0run_backend.bat"
start "AI-SGC Frontend [Port 5173]" cmd /k "%~dp0run_frontend.bat"

echo.
echo Launching browser at http://localhost:5173 in 3 seconds...
timeout /t 3 /nobreak >nul
start http://localhost:5173

echo.
echo =====================================================================
echo  Both services are running in their respective windows!
echo  Backend:  http://127.0.0.1:8000 (Docs: http://127.0.0.1:8000/docs)
echo  Frontend: http://localhost:5173
echo =====================================================================
