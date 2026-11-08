# BOOM BAP TOOLBOXX Build 040 — Audio diagnostic

Adds `app/street_audio_diagnostic.py` and `TEST_AUDIO_OFFLINE_DOUBLE_CLICK.cmd`.
The offline diagnostic renders an actual LABB note through the existing master engine, checks for silence and non-finite samples, exports a playable 16-bit stereo WAV and a JSON report. No sound card or GUI is required. Four new unit tests cover export, validation and duration handling.

**Important:** This is a developer source package. The batch launcher still requires Python. It is not the finished Setup.exe and does not establish Windows audio-device or physical MIDI performance.
