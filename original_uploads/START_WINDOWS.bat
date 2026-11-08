@echo off
cd /d "%~dp0"
py -3 -m pip install -r requirements.txt
if errorlevel 1 (echo Python 3 not found or package installation failed & pause & exit /b 1)
py -3 toolboxx.py
if errorlevel 1 pause
