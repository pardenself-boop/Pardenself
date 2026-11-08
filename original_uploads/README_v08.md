# BOOM BAP TOOLBOXX v0.8 — Track City audio region upgrade

This is a continuation of the v0.7 Windows Python prototype, not a native compiled VST or production DAW.

## New in v0.8
- `+ AUDIO WAV` imports a mono or stereo 16-bit PCM WAV as a timeline audio region.
- Each audio region has a source path, beat-based timeline start and length, non-destructive source offset, gain, and fade-in/fade-out values.
- Existing ARR trim, slip, split, move, duplicate and undo/redo work with the audio-region metadata.
- Audio regions mix with the pad sampler in the existing sounddevice output callback. Two overlapping regions sum; final output is clamped.
- Region playback is triggered from the existing 16th-note Python GUI timer, so timing is NOT sample accurate. A true audio-thread timeline scheduler is required before serious recording/editing.
- The imported file is referenced by absolute path, not embedded. Keep WAV files in place when moving projects.
- Region gain/fades are editable in project data but **do not yet have GUI handles**. There is no time-stretch, stem separation, MIDI piano roll, VST hosting or native Studio screen connection yet.

## Start
Install Python 3.11+, extract ZIP, run `START_WINDOWS.bat` inside `toolboxx_v08`.
Choose an output, click START AUDIO, use `+ AUDIO WAV` to import a clip, then Play.

## Test
`python -m unittest discover -p "test_*.py" -v`

## Known limitations
- Playback of a region imported after its timeline start, transport seeks, and looping while an audio voice is active needs a unified audio-clock transport. This build is a functional experimental integration, not a full audio clip engine.
- The MPC Key 61 is not mapped; audio availability depends on Windows drivers.
- Hardware and GUI were not exercised on a real Windows PC here.
