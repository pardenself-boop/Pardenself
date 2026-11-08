@echo off
setlocal
cd /d "%~dp0"
title BOOM BAP TOOLBOXX - OFFLINE AUDIO CHECK
where py >nul 2>nul
if %errorlevel%==0 (
 py -3 app\street_audio_diagnostic.py --output "%USERPROFILE%\Desktop\TOOLBOXX_Sound_Check"
) else (
 python app\street_audio_diagnostic.py --output "%USERPROFILE%\Desktop\TOOLBOXX_Sound_Check"
)
echo.
echo Check Desktop\TOOLBOXX_Sound_Check for WAV and JSON report.
pause
