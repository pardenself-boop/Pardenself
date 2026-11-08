# Codex instructions — BOOM BAP TOOLBOXX

This is an existing Windows 11 Python/Tkinter DAW prototype. Continue the current codebase; do not replace it with a web mockup or redesign the approved UI.

## Non-negotiable product requirements
- Preserve Track City, existing 22 LABB navigation, rugged translucent TOOLBOXX aesthetic, robot/PSG helicopter, orange waveform, arranger, 32 default pads and bottom device chain.
- NI Maschine Studio is the primary controller. Support MIDI learn and jog/transport/pads; do not claim hardware verification without testing on the device.
- Real audio is essential: imported PCM WAV, sample-pad triggers, audio regions, LABB instruments, offline stereo WAV bounce, and Windows playback.
- Keep VST audio separate from browser UI; do not introduce AudioContext into a VST editor.
- Use original code and names; do not copy third-party proprietary assets/code.

## Working method
1. Read CODEX_START_HERE.md and inspect app/toolboxx.py, app/street_song_bounce.py, app/track_city_bounce.py (if present), tests, installer scripts.
2. Run `python -m unittest discover -s tests -v` from repository root before changes. Record baseline; investigate any failing tests.
3. Implement one coherent, testable improvement at a time, add regression tests, rerun suite, and report changed files.
4. Prefer repairs to live audio/Track City integration, then a reproducible Windows installer and MIDI diagnostics. Do not hide missing functionality behind decorative UI.
5. Never say Setup.exe or Maschine Studio works until validated on Windows 11 with the actual hardware. Never claim the DAW or VST is finished without evidence.
6. Never delete original source, previous features, or change user-visible layout without explicit approval.

## Windows build
`BUILD_SETUP_DOUBLE_CLICK.cmd` invokes `BUILD_SETUP_WINDOWS.ps1`; inspect version-specific output and Inno Setup paths before running. Current installer scripts may still refer to Build 050; repair version consistency and add an automated build in GitHub Actions if needed. Windows builds cannot be validated on Linux.
