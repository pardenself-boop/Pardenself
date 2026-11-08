@echo off
setlocal
cd /d "%~dp0"
title BOOM BAP TOOLBOXX Installer Builder
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0BUILD_SETUP_WINDOWS.ps1"
if errorlevel 1 (
  echo.
  echo BUILD FAILED. Please send the BUILD_*_LOG.txt file for diagnosis.
) else (
  echo.
  echo Installer is in the dist folder. Test it before sharing.
)
pause
