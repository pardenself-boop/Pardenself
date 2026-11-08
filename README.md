# BOOM BAP TOOLBOXX — Windows v0.5 / Track City Advanced Edit

## Launch
Windows: install Python 3.11+, extract folder, double-click `START_WINDOWS.bat`. First run installs `sounddevice`, `mido`, and `python-rtmidi`. Connect audio output and load a 16-bit PCM WAV sample into a pad. Maschine Studio USB HID/screen output is not yet implemented: virtual screens only.

## Track City advanced editing
- **MRQ**: drag empty arranger space to marquee-select clips. Shift-click toggles selection.
- **TRK**: clicking a clip selects the clips on that track.
- **ARR**: click to select, drag the body to move; drag the first/last ~8 pixels to trim. Trim-left adjusts source offset without destructive modification.
- **Loop brace**: mint horizontal strip at the top of the arrangement. Drag left/right triangular handles to resize; drag the middle to move the loop. Loop playback follows the brace.
- **Snap**: toggles between 1/16-note equivalent (0.25 beat in the prototype's timeline units) and free movement.
- **Copy/Paste/Paste Merge**: paste at playhead. Merge is a **container-length union** for same-start/same-track/same-kind clips; it is **not MIDI event merging** yet.
- **Split**: at playhead, preserves source offsets. Right-click in the arranger splits selected clips at pointer position.
- **Undo/Redo**: 100 snapshot editing history, Ctrl+Z/Ctrl+Y. Drag gesture is one undo checkpoint.
- **Jog**: cycle modes including LOOP START, LOOP END and LOOP MOVE. Virtual jog buttons execute the same commands.
- **Save/Load**: persists loop, edit mode, snap, clips, and mappings. Old v0.4 JSON clips import supported.

## Limitations
This is a Python/Tkinter development prototype, not a finished Windows native compiled DAW. No VST hosting, stems, hardware screens, live waveform/audio-region arrangement, arbitrary MIDI event merge, or ASIO-exclusive routing yet. Clip containers are editable project metadata; only the separate 16-step pad sequencer produces sound. Audio timing is prototype-level Tkinter scheduling. MIDI hardware and audio device behavior must be tested on the user's Windows computer.

## Run tests
`python -m unittest -v test_arranger`
