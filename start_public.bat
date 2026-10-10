@echo off
cd /d "%~dp0"
title TLE CSS Quiz - Cloudflare Public Access
where py >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install Python first.
  pause
  exit /b 1
)

echo Installing/updating required Python packages...
py -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo Python package installation failed.
  pause
  exit /b 1
)

where cloudflared >nul 2>nul
if errorlevel 1 (
  echo.
  echo Cloudflare Tunnel is not installed.
  echo Installing with Windows Package Manager...
  winget install --id Cloudflare.cloudflared
  echo.
  echo If installation completed successfully, CLOSE this window and
  echo run start_public.bat again.
  pause
  exit /b 0
)

py start_public.py
pause
