@echo off
setlocal
cd /d "%~dp0"
title BOOM BAP TOOLBOXX - STREET SOUND CHECK
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 app\audio_smoke_test.py
) else (
  python app\audio_smoke_test.py
)
if errorlevel 1 (
  echo Audio test could not launch. Python 3 and requirements may be needed.
  pause
)
