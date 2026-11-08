# BOOM BAP TOOLBOXX Build 050 — integration repair

**This is a source release candidate, not a finished DAW or precompiled Setup.exe.**

Fixed a real Windows packaging blocker: `verify_release.py` still expected Setup_046.exe even though the installer script was creating Setup_048.exe. All three build references now consistently target `BOOM_BAP_TOOLBOXX_Setup_050.exe`.

Main workstation MIDI input now uses a bounded, nonblocking queue (2048 events) so a fast controller cannot block the MIDI callback thread. Each Tk poll processes at most 256 events, preserving GUI responsiveness; overflow is reported rather than silently hanging.

## On Windows 11
1. Extract the entire ZIP to a folder.
2. Double-click `BUILD_SETUP_DOUBLE_CLICK.cmd` to attempt the Windows installer build (internet required for build dependencies).
3. If successful, run `dist\BOOM_BAP_TOOLBOXX_Setup_050.exe`.
4. Use STREET SOUND CHECK before depending on the DAW for sessions.
5. If anything fails, send `BUILD_050_LOG.txt` and the on-screen error.

Not verified here: Windows compilation, installer execution, live audio device, NI Maschine Studio. All 22 LABBs are not production complete.
