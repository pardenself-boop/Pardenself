# BOOM BAP TOOLBOXX — Build 058 development source

This continues the uploaded Build 057 Tkinter prototype. It is not a compiled Windows installer or a completed DAW. No layout redesign was made. The supplied image remains a visual target; the source's drawn interface does not reproduce all of its artwork.

## Run on Windows

Install Python 3.11 x64. Extract the whole folder and double-click START_EXACT_LAYOUT.bat to install runtime requirements and open the existing Cook Up workstation. START_WINDOWS.bat opens the underlying workstation; START_DUAL_SCREEN.bat also opens the LABB editor. Audio playback and MIDI are started explicitly in the app.

For a Windows installer, run BUILD_SETUP_DOUBLE_CLICK.cmd. Python packages and Inno Setup may be downloaded. Expected output, only after a successful build: `dist/BOOM_BAP_TOOLBOXX_Setup_058.exe`. No Setup.exe is included in this package.

For GitHub Actions, put this folder's contents at your repository root, including `.github/workflows/windows-installer.yml`, then run **Build TOOLBOXX Windows Installer**. The workflow runs tests, freezes the dependency inventory, packages the app, opens its real Tk windows through `--smoke-test`, compiles the installer, verifies output files, and uploads **TOOLBOXX-Windows-installer**. This workflow has not been run from this chat. Its output is conditional on a successful Windows runner execution.

## Repairs

- Initialize the selected SOUL orb before widget creation and refresh. Previously Cook Up could raise AttributeError on startup.
- Use release.json for Build 058 version and installer naming. Remove conflicting Build 027/050 installer references from active build logic.
- Pin direct build dependencies; record all resolved package versions. Include soundcard and numpy in runtime requirements for capture.
- Remove COOK_UP_REFERENCE.png from mandatory packaging inputs. It was absent from the uploads and no runtime module loads it; no replacement artwork was fabricated.
- Run regression tests and a packaged Tk startup check before compiling the installer. Add timeout and failure gates. Verify Windows executable signatures and SHA256.
- Fix the source launchers to locate app/ and the song demo JSON.
- Preserve every uploaded file unchanged in original_uploads/ for comparison.

## Validation in this session

- Baseline: 90 tests passed.
- After changes: 93 tests passed, including startup-state and release-validation regressions.
- Source preflight and compilation: passed (40 Python app modules).
- Offline audio diagnostic: 48,000 stereo PCM frames at 48 kHz, peak 0.086170, RMS 0.038923, zero clipped frames. The two channels contain the same mono engine signal.
- Full Tk startup: not executed here; no active display or Xvfb available. Windows pipeline contains the actual startup check.
- Windows build, installation, live sound-device playback, and Maschine Studio hardware: not tested. No VST build is included. Existing preview FX slots remain labeled as planned.

Inspect validation/ for the test transcript, package preflight, and generated diagnostic WAV/JSON. Run TEST_AUDIO_DOUBLE_CLICK.cmd and TEST_MIDI_DOUBLE_CLICK.cmd on the target Windows machine to check actual devices. MIDI mode requires a visible MIDI input port; this does not implement or verify NI HID screens/LEDs.

## Changed files

app/cookup_ui.py, app/toolboxx_launcher.py, app/requirements.txt, BUILD_SETUP_WINDOWS.ps1, BUILD_SETUP_DOUBLE_CLICK.cmd, build_windows.ps1, installer/toolboxx.iss, verify_package.py, verify_release.py, .github/workflows/windows-installer.yml, START_WINDOWS.bat, START_EXACT_LAYOUT.bat, START_DUAL_SCREEN.bat, SONG_BOUNCE_DOUBLE_CLICK.cmd, tests/test_release_050.py.

Added: release.json, requirements-build.txt, app/startup_check.py, tests/test_build_058.py, BUILD_058_README.md, validation/, original_uploads/.
