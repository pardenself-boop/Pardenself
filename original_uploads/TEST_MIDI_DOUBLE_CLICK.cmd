@echo off
cd /d "%~dp0app"
where py >nul 2>nul
if %errorlevel%==0 (py street_midi_test.py) else (python street_midi_test.py)
if errorlevel 1 (echo MIDI test failed. Python 3.11+ and mido/python-rtmidi may be required.& pause)
