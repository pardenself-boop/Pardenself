@echo off
cd /d "%~dp0"
py -3 app\street_song_bounce.py app\SONG_DEMO_052.json --output "%USERPROFILE%\Desktop\TOOLBOXX_SONG.wav"
pause
