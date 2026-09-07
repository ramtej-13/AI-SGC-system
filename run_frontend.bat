@echo off
echo =====================================================================
echo  AI-Based Student Grievance Classification & Smart Routing System
echo  Starting React + Vite Frontend on http://localhost:5173
echo =====================================================================
cd /d "%~dp0frontend"
set PATH=C:\Users\koneAjay\AppData\Local\Microsoft\WinGet\Packages\OpenJS.NodeJS.LTS_Microsoft.Winget.Source_8wekyb3d8bbwe\node-v24.19.0-win-x64;%PATH%
cmd /c npm run dev
pause
