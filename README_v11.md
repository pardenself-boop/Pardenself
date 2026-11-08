# BOOM BAP TOOLBOXX v1.1 — 22-suite browser + shared hardware routing

This is an incremental upgrade to v1.0, not a new DAW engine. All 22 named suites are present in a navigable registry. Their implementation status is displayed accurately: working, foundation, or planned. **This does not mean all 22 DSP instruments are implemented.**

## New
- 22-suite navigator with categories, status and descriptions.
- Toolbar **22 SUITES** button; double-click a suite or click OPEN FOCUSED SUITE.
- Studio simulator mappings: SUITES, SUITE NEXT, SUITE PREV, SUITE CLICK.
- The selected suite persists with the project. Windows UI and Studio simulator use the same SuiteRouter state.
- Track City and existing audio/pattern arrangement engine are preserved.

## Run
Windows 10/11, Python 3.11+. Run START_WINDOWS.bat, then 22 SUITES or STUDIO HARDWARE MAP.

## Limitations
No physical NI Studio USB driver, no native screens, no stem separation or 22 completed instrument engines. The Python Tkinter audio prototype is not a production DAW or VST host. Audio timing is not sample accurate. Audio clips need existing WAV paths; sampler samples must be reloaded after project load.

Tests: `python -m unittest discover -p 'test_*.py' -v`

## Track City addition
- MUTE TRACK and SOLO TRACK controls in the arranger mode bar and Studio command map.
- Playback event scheduling honors track mute/solo; state saves with the project.
- Limitation: already-running audio-region voices are not stopped by toggling mute/solo; this affects future clip launches.
