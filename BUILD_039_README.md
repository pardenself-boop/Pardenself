# BOOM BAP TOOLBOXX Build 039 — STREET SOUND CHECK

Added `app/audio_smoke_test.py`, a separate audio output diagnostic with device selector, START/STOP, four instrument triggers, panic, peak indicator, and offline stereo WAV export. `TEST_AUDIO_DOUBLE_CLICK.cmd` launches it on Windows when Python dependencies are installed.

**Testing:** Engine audio-render tests pass in this environment. Live Windows 11 device output, soundcard loopback capture, Maschine Studio and packaging into a signed Setup.exe have not been verified. This is a source/testing package, not the promised customer installer. The test launcher requires Python, sounddevice and other app requirements. Offline WAV export needs only the Python standard library and existing engine source.

To test on Windows: extract ZIP, install Python 3 if needed, `py -m pip install -r app\requirements.txt`, then double-click `TEST_AUDIO_DOUBLE_CLICK.cmd`. Press START AUDIO and a LABB. If silent, export WAV and play in Windows to separate DSP from output-device problems. Use headphones or low volume for first test.

The approved MPC-style DAW UI remains unchanged.
