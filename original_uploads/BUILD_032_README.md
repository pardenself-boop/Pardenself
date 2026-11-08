# BOOM BAP TOOLBOXX — Build 032: STREET CRATE

## Implemented
- New `app/street_sample_engine.py`: reads PCM 8/16/24/32-bit mono/stereo WAV, downmixes to mono and validates file length/encoding.
- Up to 32 sample voices; MIDI note pitch transposition from user-specified root note, velocity and note-off fade.
- Sample voices mix into existing `LabbEngine.render_raw` and shared master bus; instrument volume, mute and solo apply.
- Existing oscillator reference patches remain available when no sample is loaded.
- `LabbEngine.load_sample(labb_index, path, root_note=60)` is the integration entry point.
- Eight automated tests pass (3 patch-vault, 5 sample engine).

## Limitations
- No sample file picker/UI added in this build; load_sample is an engine API.
- Sample playback is mono; stereo WAV is downmixed. No warp/time stretch, slice editing, or disk streaming.
- WAV slots are not yet saved with projects or restored on startup.
- The reference Python audio renderer is not a production DAW or VST.
- Windows installer, live audio, and physical MIDI tests remain pending.

## Test
`python -m unittest discover -s tests -v`
