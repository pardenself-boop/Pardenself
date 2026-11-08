@echo off
setlocal
cd /d "%~dp0"
title BOOM BAP TOOLBOXX Installer Builder 048
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0BUILD_SETUP_WINDOWS.ps1"
if errorlevel 1 (
  echo.
  echo BUILD FAILED. Please send BUILD_048_LOG.txt for diagnosis.
) else (
  echo.
  echo Installer is in the dist folder. Test it before sharing.
)
pause
