@echo off
echo =====================================================================
echo  AI-SGC System - Temporary Live Public URL (Cloudflare Tunnel)
echo =====================================================================
echo.
echo NOTE: Ensure both Backend and Frontend are running first!
echo (run_backend.bat and run_frontend.bat)
echo.
echo Generating public HTTPS link...
echo.
set PATH=C:\Users\koneAjay\AppData\Local\Microsoft\WinGet\Packages\OpenJS.NodeJS.LTS_Microsoft.Winget.Source_8wekyb3d8bbwe\node-v24.19.0-win-x64;%PATH%
cmd /c npx --yes cloudflared tunnel --url http://localhost:5173
pause
