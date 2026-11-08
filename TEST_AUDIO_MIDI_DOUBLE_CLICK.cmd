@echo off
setlocal
cd /d "%~dp0"
title BOOM BAP TOOLBOXX - AUDIO AND MASCHINE STUDIO TEST
where py >nul 2>nul
if errorlevel 1 (
  set "TEST_PYTHON=python"
) else (
  set "TEST_PYTHON=py -3"
)
%TEST_PYTHON% -m venv .test-venv
if errorlevel 1 goto failed
".test-venv\Scripts\python.exe" -m pip install -r app\requirements.txt
if errorlevel 1 goto failed
".test-venv\Scripts\python.exe" app\audio_smoke_test.py
if errorlevel 1 goto failed
exit /b 0
:failed
echo Test could not start. Install Python 3.11 or newer and retry.
pause
exit /b 1
