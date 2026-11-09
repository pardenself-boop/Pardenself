# TOOLBOXX Build 064 — audio and MIDI inside Cook Up

In Build 063, use **MENU → CHECK FOR UPDATES…** to get this build. Save your project, download and install the update. Or run BOOM_BAP_TOOLBOXX_Setup_064.exe over your existing installation.

- **MENU → AUDIO + MIDI SETUP…** opens shared output/MIDI controls directly from Cook Up. The main layout and visual design are preserved.
- Choose an output, START AUDIO and TEST BASS or TEST KEYS. The test notes use the same instruments, FX and output as the DAW without editing your project or patch.
- Scan/select the Maschine Studio MIDI input and CONNECT. Watch the MIDI IN indicator, message count and recent note/CC values. Learn events appear too, without consuming a message twice.
- COPY TEST REPORT copies device/status information and the last 64 MIDI messages for troubleshooting. The log is bounded and stays on the GUI thread.
- Audio scans preserve the selected output when still present; failed scans clear stale choices. Opening setup does not start or connect devices. Closing it keeps the current audio/MIDI session running.

184 automated tests pass locally. Native Tk checks cover setup startup, no automatic device connections, clipboard reports and closing without stopping the app. Windows publication requires packaging, an in-place upgrade from Build 063, user-file preservation, installed startup, normal launch/close and uninstall checks.

This is an unsigned development build. Actual Windows 11 audio and physical Maschine Studio operation still require testing. Physical Studio screens/LEDs and other documented unfinished features are not added by this release.
