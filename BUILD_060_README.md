# BOOM BAP TOOLBOXX — Build 060 development package

This is the current source build of the existing Tkinter DAW prototype. Native Instruments Maschine Studio remains the primary controller. Original uploads and previous release notes are preserved.

## Launch on Windows

Install Python 3.11+ x64, extract the complete folder, and double-click START_EXACT_LAYOUT.bat. This installs app/requirements.txt and opens Cook Up Matrix. The UI, 22 LABBs, 32 sample pads across two banks, Track City and device-chain area remain in the native Tkinter app.

## Build the Windows installer

Run BUILD_SETUP_DOUBLE_CLICK.cmd or `powershell -ExecutionPolicy Bypass -File BUILD_SETUP_WINDOWS.ps1`. The script installs pinned direct build dependencies, runs tests, performs source preflight, packages the application, checks real Tk startup in the executable, compiles Inno Setup, validates output signatures and writes a SHA256 checksum.

Expected successful Windows outputs:

- build/BOOM_BAP_TOOLBOXX/BOOM_BAP_TOOLBOXX.exe
- dist/BOOM_BAP_TOOLBOXX_Setup_060.exe
- dist/SHA256.txt
- BUILD_060_LOG.txt and BUILD_DEPENDENCIES.txt

The GitHub workflow at .github/workflows/windows-installer.yml performs the same build on windows-2022 and uploads TOOLBOXX-Windows-installer. The workflow additionally checks silent installation, installed-app startup and uninstallation. Its installer artifact contains only the single Setup.exe; build logs are a separate diagnostic artifact. It has not been run in this session. No executable or installer is included in this source archive; Windows compilation and installation have not been verified.

## Build 060 changes

- MASCHINE SETUP now offers MIDI port scan, connect and disconnect without leaving Cook Up.
- Port scanning prefers a matching Maschine Studio input while preserving an existing selection; it never connects automatically. Connection failure clears the stale closed port and reports the reason.
- Physical MIDI learn captures the incoming address and selected mode, consumes the learn event, displays the captured address and lets the following press/turn execute the command. Encoder modes ignore note events; note releases do not complete button learning. Cancel and window close disarm learning.
- BANK PAD 1–16 commands address the active bank, so the same physical 16-pad map can access all 32 DAW slots. PAD 1–32 and default MIDI notes 36–67 retain their absolute meaning. Bank navigation keeps the selected physical position.
- Controller profiles serialize into projects and restore through the existing router object, preserving the live dispatcher's reference. Corrupt profiles leave the session untouched; old projects retain the current hardware profile. Successful load cancels pending learn and discards queued old-session events.
- Corrected virtual jog test direction for the selected encoder mode and made setup fields readable in a two-row layout. Cook Up's footer reflects actual MIDI connection state.
- Expanded sound-check window so audio/MIDI controls remain visible. Added TEST_AUDIO_MIDI_DOUBLE_CLICK.cmd and TEST_AUDIO_MIDI_WINDOWS.md for later local device tests.

## Earlier improvements included

Build 058 fixed Cook Up initialization and the inconsistent Windows installer pipeline. Build 059 added the playable pad deck, actual sample waveform, selected-pad step editing, relative media references and staged project loading. The reference image remains the visual direction; its detailed decorative artwork has not been recreated. FX marked as planned remain previews.

## Session validation

- Baseline: 101 unittests passed before this release's edits.
- Final: 111 unittests passed, including controller learning, bank-aware pads, failed reconnect handling, profile validation and project recall through the live dispatcher.
- Source preflight and compilation: passed, 41 app modules.
- Real Tk workstation/Cook Up startup: passed on a Linux Xorg dummy display with system Python.
- Real Tk controller setup interactions: passed for note learn, bank-aware command dispatch, encoder learn and cancellation, without callback errors. MIDI events were simulated; no NI hardware was attached.
- Offline audio: 48 kHz stereo PCM, 48,000 frames, peak 0.086170, RMS 0.038923, no clipped frames. Left/right contain the engine's mono signal.

See validation/ for logs and UI screenshots. Windows live audio, physical Maschine Studio operation, native HID/screens/LEDs, installer execution and a VST build remain unverified or unimplemented as documented. This package is a tested development milestone, not a finished commercial DAW.

## Changed files since Build 059

app/toolboxx.py, app/studio_midi_adapter.py, app/project_io.py, app/hardware_setup_window.py, app/cookup_ui.py, app/audio_smoke_test.py, release.json, .gitignore, CONTROLLER_MASCHINE_STUDIO.md, installer/toolboxx.iss, .github/workflows/windows-installer.yml.

Added: tests/test_maschine_workflow_060.py, TEST_AUDIO_MIDI_DOUBLE_CLICK.cmd, TEST_AUDIO_MIDI_WINDOWS.md, BUILD_060_README.md and validation evidence.

## User delivery requirement

Deliver one all-in-one Windows 11 Setup.exe, not loose Python files or a source ZIP. The source archive is only a development backup. Inno Setup embeds the bundled runtime and libraries with disk spanning disabled. Windows compilation remains blocked until a Windows runner or accessible project repository is available.
