@echo off
setlocal
title Push AI-SGC System to GitHub
cd /d "%~dp0"

echo ======================================================================
echo           AI-SGC SYSTEM - PUSH TO GITHUB REPOSITORY
echo ======================================================================
echo Target: https://github.com/ramtej-13/AI-SGC-system.git
echo.

echo [1/3] Verifying Git environment...
git --version
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Git was not found.
    pause
    exit /b 1
)

echo.
echo [2/3] Committed status:
git log -1 --oneline

echo.
echo [3/3] Pushing backend/, frontend/, datasets, and models to GitHub...
echo If a GitHub popup opens in your browser, click 'Sign in' or 'Authorize'!
echo.

git push -u origin main --force

if %ERRORLEVEL% equ 0 (
    echo.
    echo ======================================================================
    echo [SUCCESS] Your repository is now fully uploaded!
    echo Refresh https://github.com/ramtej-13/AI-SGC-system in your browser.
    echo You will see 'backend/' and 'frontend/' folders present.
    echo ======================================================================
) else (
    echo.
    echo ======================================================================
    echo [ACTION NEEDED] GitHub authentication was not completed.
    echo If browser sign-in did not appear, you can use a GitHub Personal Token:
    echo 1. Open: https://github.com/settings/tokens
    echo 2. Click "Generate new token (classic)", select "repo" checkmark
    echo 3. Copy token, then run in CMD:
    echo    git push https://YOUR_TOKEN@github.com/ramtej-13/AI-SGC-system.git main --force
    echo ======================================================================
)

echo.
pause
