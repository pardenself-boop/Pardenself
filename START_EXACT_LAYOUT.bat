@echo off
cd /d "%~dp0app"
py -3 -m pip install -r requirements.txt
if errorlevel 1 (echo Dependency installation failed & pause & exit /b 1)
py -3 launch_reference.py
if errorlevel 1 pause
