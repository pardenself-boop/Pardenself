@echo off
cd /d "%~dp0app"
py -3 street_bounce.py --output "%USERPROFILE%\Desktop\TOOLBOXX_BOUNCE.wav" --seconds 4
pause
