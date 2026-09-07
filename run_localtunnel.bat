@echo off
echo =====================================================================
echo  AI-SGC System - Temporary Live Public URL (LocalTunnel)
echo =====================================================================
echo.
echo NOTE: Ensure both Backend and Frontend are running first!
echo.
set PATH=C:\Users\koneAjay\AppData\Local\Microsoft\WinGet\Packages\OpenJS.NodeJS.LTS_Microsoft.Winget.Source_8wekyb3d8bbwe\node-v24.19.0-win-x64;%PATH%
cmd /c npx --yes localtunnel --port 5173
pause
