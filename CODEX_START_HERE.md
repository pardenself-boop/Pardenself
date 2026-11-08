# BOOM BAP TOOLBOXX — Codex handoff (Build 057)

## What this package is
Full available Build 057 development source, tests, assets and Windows installer-building scripts. **It is not a precompiled Windows installer, finished VST, or completed DAW.**

## Fast start with Codex
1. Unzip this package into a local project folder (prefer a private Git repository).
2. Open the folder in Codex (local desktop or repository workspace).
3. Paste the prompt in `CODEX_FIRST_PROMPT.md`.
4. Install Python 3.11+ and dependencies from `app/requirements.txt` (Windows recommended).
5. Run `python -m unittest discover -s tests -v` before modifying code.
6. On Windows only, run `BUILD_SETUP_DOUBLE_CLICK.cmd` to attempt installer compilation after reviewing scripts. No verified Setup.exe is included.

## Current verified state
- Prior Build 057 development run reported 90 passing unittest cases and successful compilation/ZIP integrity.
- Offline song bounce combines pad patterns, audio-region clips and LABB MIDI notes; event sorting and tempo validation repaired.
- Live Windows audio, actual Maschine Studio mapping and installer are not verified.

## Suggested first milestone
Make a repeatable Windows build pipeline that runs tests, packages the current Tkinter app, validates launch, and produces a version-consistent Setup.exe artifact. Then validate audio/MIDI on the user's Windows 11 machine.

## Main files
- `app/toolboxx.py`: main GUI and audio engine
- `app/street_song_bounce.py`: offline song bounce and scheduling
- `tests/`: automated tests
- `BUILD_SETUP_WINDOWS.ps1`, `BUILD_SETUP_DOUBLE_CLICK.cmd`, `installer/`: Windows packaging
- `BUILD_057_README.md`: most recent change summary
