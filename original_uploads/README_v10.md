# BOOM BAP TOOLBOXX v1.0 — Hardware-first arranger controls

This builds on v0.9, retaining the sampler, Track City arranger, audio regions and virtual Maschine Studio mapping editor.

## New in v1.0
- Jog click selects the focused clip, or commits a pending edit.
- Jog rotation navigates clips; edit operations accumulate preview deltas until confirmed.
- `EDIT TRACK` moves selected clip(s) vertically one track per detent.
- `EDIT LOOP MOVE` repositions the entire loop brace.
- SHIFT + jog enables 1/16-beat adjustments (0.0625 beats) in the editor.
- BACK cancels a pending edit with no arranger mutation.
- Hardware simulator visually outlines the currently focused clip.
- Fixed SHIFT routing so simulator and shared command editor stay synchronized.
- Added six command-parity tests; 35 total automated tests pass.

## Run on Windows
1. Install Python 3.11 or later.
2. Extract this ZIP and enter the `toolboxx_v09` folder.
3. Double-click `START_WINDOWS.bat` (installs requirements if needed).
4. Click `STUDIO HARDWARE MAP`.
5. Use `EDIT MOVE`, `EDIT TRACK`, `EDIT LOOP MOVE`, `JOG LEFT/RIGHT`, `JOG CLICK`, `BACK`, and `SHIFT`.

## Limits
- The hardware layout is a virtual command simulator, **not** a verified USB driver for Maschine Studio.
- The dual screens in this version are simulated in Tkinter and do not output to the physical Studio screens.
- This is a Python prototype, not a compiled VST or production-grade DAW. Audio timing and ASIO support are not guaranteed.
- Some advanced MIDI note selection, stem separation and native USB hardware I/O remain unimplemented.
- The 1/16-beat preview may be quantized by the arranger's current snap setting on commit. Turn snap off for unquantized fine edits.

Run automated tests: `python -m unittest discover -p "test_*.py" -v`
