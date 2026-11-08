# BOOM BAP TOOLBOXX Build 046 — Installer Sound Check Integration

- Packaged EXE now accepts `--sound-check`, opening the existing combined audio/MIDI/pad diagnostic window.
- Inno Setup Start Menu installs two shortcuts: main TOOLBOXX and STREET SOUND CHECK.
- Installer and verification scripts now agree on the `Setup_046.exe` filename, replacing stale 027/030 expectations.
- Three automated tests verify both launcher paths without a Windows machine.
- To build on Windows, double-click BUILD_SETUP_DOUBLE_CLICK.cmd. This downloads build dependencies; the resulting installer is for end users and does not require Python.
- No Windows installer was compiled in this Linux environment. Windows hardware and installation tests remain required.
