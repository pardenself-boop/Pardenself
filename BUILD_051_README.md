# BOOM BAP TOOLBOXX Build 051 — Offline Stereo Bounce

Added `app/street_bounce.py`: render the existing TOOLBOXX Engine to a stereo 16-bit WAV file **without requiring an audio output device**. Reports peak and clipped frames, checks finite samples, and validates render duration. Supports `--sample path.wav` for triggering a user WAV on pad 1 or a default synthetic instrument note.

Windows quick test: double-click `BOUNCE_WAV_DOUBLE_CLICK.cmd` (Python and app requirements required). This writes `TOOLBOXX_BOUNCE.wav` on Desktop. CLI: `py -3 app/street_bounce.py --sample myloop.wav --output bounce.wav --seconds 4`.

**Not a full song arranger export**: this renders the currently instantiated Engine state, including triggered voices, not a saved project timeline. Does not prove real-time Windows audio, installer, or Maschine Studio functionality.
