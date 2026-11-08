# TOOLBOXX Build 059 — playable Cook Up UI and project recall

Continues Build 058 and the uploaded Tkinter DAW. Native Instruments Maschine Studio remains the primary controller; see CONTROLLER_MASCHINE_STUDIO.md. No physical hardware verification is claimed.

## UI

- Clickable 4x4 pad deck follows hardware orientation, pads 1–4 along the bottom. Banks A/B address all 32 sample slots.
- Click to select/audition; double-click to assign a WAV. Orange markers indicate loaded audio; mint marks selection.
- The waveform displays the selected pad's actual PCM audio, duration and sample rate. Empty pads display an explicit load prompt.
- The four-row step editor follows the selected pad's group instead of addressing only pads 1, 5, 9 and 13.
- Tempo/playback text reflects session state. Controller-triggered pad selection updates the pad and waveform views.
- MASCHINE SETUP opens the existing Controller Editor MIDI assignment window. Its command list now includes all 32 pad commands and bank navigation.
- Removed the fabricated rage percentage from the banner; it now shows loaded pad count.

## Project recall

Projects save pad WAV sources, audio-region sources and LABB sample paths/root notes relative to the project folder where possible. Moving a project folder together with its media preserves these references. Audio is referenced, not embedded or copied. Sources on other Windows drives remain absolute.

All media and session data are staged before replacing the active session. Invalid patterns/tempo or missing audio cause an error and leave the open session and playback intact. Successful loading stops transport, clears old voices and restores session state. Save uses an atomic file replacement. Legacy files remain readable, but missing pad references cannot be recovered from older saves.

## Validation

101 unittests passed. Source compilation and preflight passed (41 app modules). Real Tk startup passed on Linux using the system Python and an Xorg dummy display. UI interaction checks passed for pad clicks, bank switching, step editing, controller-command selection refresh and opening Maschine setup, with no Tk callback errors. validation/cookup-ui059.png is a screenshot of the running UI with the uploaded AUDIO_TEST.wav assigned to pad 1.

Windows executable packaging, Windows device audio playback and physical Maschine Studio remain untested. The Windows workflow has not been run here. Expected future successful build output is dist/BOOM_BAP_TOOLBOXX_Setup_059.exe; no Setup.exe is included.

## Run

On Windows, extract the complete folder and use START_EXACT_LAYOUT.bat. For installer generation, use BUILD_SETUP_DOUBLE_CLICK.cmd. Existing 22 LABBs, Track City and device chain are preserved. Preview FX remain labeled as planned; the screenshot's detailed decorative artwork is not reproduced.

## Changed since Build 058

app/toolboxx.py, app/cookup_ui.py, app/hardware_setup_window.py, release.json.

Added: app/project_io.py, tests/test_project_ui_059.py, CONTROLLER_MASCHINE_STUDIO.md, BUILD_059_README.md and validation evidence.
