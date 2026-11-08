# BOOM BAP TOOLBOXX — Build 031

## Implemented
- STREET PATCH VAULT: permanent per-LABB instrument presets, saved as `.tbxi.json` in `%LOCALAPPDATA%\BOOM_BAP_TOOLBOXX\Patches` on Windows.
- Existing instrument editor STORE and RECALL now use disk persistence, not temporary in-memory snapshots.
- Atomic writes to reduce risk of truncated presets.
- Strict schema, LABB identity, parameter-range and finite-number validation before applying patches.
- Three new automated regression tests, all passing in Linux development environment.

## Not completed or verified
- No finished Windows Setup.exe is included. The Windows installer build scripts still need to run and be verified on Windows 11.
- Maschine Studio and Logitech Trackman Marble physical input and audio output remain untested on user's PC.
- Many of the 22 LABBs still use reference oscillator patches rather than dedicated sampling/DSP engines.
- Full feature completeness and production readiness are NOT claimed.

## Test
`python -m unittest discover -s tests -v`

## Build
Run `BUILD_SETUP_DOUBLE_CLICK.cmd` on Windows after inspecting the script. This is a developer builder, not the customer installer.
