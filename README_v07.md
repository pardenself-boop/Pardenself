# BOOM BAP TOOLBOXX v0.7 — Arrangement playback milestone

Based on the previous v0.6 Windows/Tkinter prototype. Run `START_WINDOWS.bat` from this directory. Requires Python 3.11+, dependencies in requirements.txt.

## What's new
- Arrangement now **gates pattern triggers by clip time**, rather than playing the global 16-step grid everywhere.
- Clips reference `pattern_id` and a separate 16-step / 32-pad pattern; new clips copy the currently selected pattern so they can be edited independently.
- Select a pattern clip in Track City to edit its steps, then select a pad. Existing clips from older projects share the `main` pattern for compatibility.
- Clip trimming, splitting, and slip offsets preserve source-pattern phase. Loop brace determines playhead wrapping.
- Pattern data persists in the project JSON; older `pattern` projects still load.
- 19 automated tests passed (7 new playback tests + 12 existing tests).

## Limitations
- Python/Tkinter `after()` clock has jitter and is not sample-accurate. Audio voices are played by the existing sounddevice sampler, but sequencer timing is not yet scheduled in the audio callback.
- Pattern clips are now audible *when corresponding pads have WAV samples loaded*. Audio-file clips, stem separation, piano roll, true MIDI-event merge, VST hosting, physical Studio screens, and ASIO-specific support are NOT implemented.
- The simulator and controller mapping are development prototypes, not verified on real Maschine Studio hardware.
- Samples are not embedded in projects and must be reloaded.

## Smoke test
1. Run START_WINDOWS.bat, choose audio output, click START AUDIO.
2. Load a 16-bit PCM WAV into pad 1.
3. Select the DRUM A clip, select pad 1, enable step 1 and 5.
4. Press PLAY: it triggers during the DRUM A clip, not throughout empty timeline space.
5. Add a clip, change its steps, move it, and test loop brace handles and MRQ/TRK/ARR.
