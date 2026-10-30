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
npx --yes cloudflared tunnel --url http://localhost:5173
pause
