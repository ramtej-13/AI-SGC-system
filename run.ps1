$root = $PSScriptRoot
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host " Starting AI-SGC System (Backend + Frontend)..." -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan

Start-Process -FilePath "cmd.exe" -ArgumentList "/k `"$root\run_backend.bat`""
Start-Process -FilePath "cmd.exe" -ArgumentList "/k `"$root\run_frontend.bat`""

Start-Sleep -Seconds 3
Start-Process "http://localhost:5173"
Write-Host "`nBoth services are up! Opened http://localhost:5173 in your browser." -ForegroundColor Green
