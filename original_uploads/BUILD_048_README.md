# BOOM BAP TOOLBOXX — Build 048 Release Candidate

**Windows installer source kit; no compiled Setup.exe is included.**

## Windows quick start
1. Extract this ZIP to a folder.
2. Double-click `BUILD_SETUP_DOUBLE_CLICK.cmd` on a Windows 11 x64 PC with internet access.
3. The script checks Python, installs isolated build dependencies, packages the app, and installs Inno Setup if needed.
4. On success, open `dist/BOOM_BAP_TOOLBOXX_Setup_048.exe` and install.
5. From Start Menu launch **STREET SOUND CHECK (Audio + MIDI)** before the full DAW. Select your sound output and MIDI input and test a pad.

**Important:** This is a release candidate, not a validated finished DAW. Windows packaging, audio output, MIDI device enumeration, Maschine Studio mappings, and installer/uninstaller have NOT been tested on actual Windows hardware here. All 22 LABBs are not production complete.

## Release repair
- Unified the two installer build entry points so they cannot build conflicting version numbers.
- Matched Inno Setup output, build validation, hash output, and builder instructions to version 048.
- Retained the original workstation source and tests.
