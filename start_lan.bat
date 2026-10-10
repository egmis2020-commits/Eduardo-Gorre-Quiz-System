@echo off
setlocal
cd /d "%~dp0"
title EGMIS TLE CSS Quiz V24.2 - LAN Setup

echo.
echo ================================================================
echo   EGMIS TLE CSS QUIZ V24.2 - SAFE WINDOWS LAN STARTUP + WAITRESS
echo ================================================================
echo   This check does NOT disable Windows Defender or antivirus.
echo   It checks Python, packages, Wi-Fi profile, LAN IP, TCP 8000, and Waitress.
echo ================================================================
echo.

where py >nul 2>nul
if %errorlevel%==0 (
    py start_lan.py
    set EXITCODE=%errorlevel%
) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
        python start_lan.py
        set EXITCODE=%errorlevel%
    ) else (
        echo [ERROR] Python was not found.
        echo.
        echo Install Python 3.12-3.14 from the official Python installer,
        echo then run this file again. Select "Add Python to PATH" during setup.
        echo.
        set EXITCODE=10
    )
)
echo.
if not "%EXITCODE%"=="0" (
    echo Startup stopped with code %EXITCODE%.
    echo Read the diagnostic messages above for the exact correction.
)
pause
exit /b %EXITCODE%
