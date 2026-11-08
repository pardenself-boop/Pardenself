# BOOM BAP TOOLBOXX Build 038 — STREET TAP / CRATE BLOCK

**New:** Advanced Menu → STREET TAP / CRATE BLOCK.

- STREET TAP: user-initiated Windows WASAPI output-loopback recording using `soundcard` and `numpy`. Pick the active Windows playback endpoint, name the capture, press RECORD and STOP. Captures stereo 16-bit PCM WAV, max 10 minutes, no input monitoring to avoid feedback. On STOP, loads the WAV onto the currently selected pad using the existing engine.
- CRATE BLOCK: persistent bookmarks for sample sites and local sample/download folders. Double-click bookmarks to open them; list supported audio files in configured directories. No automated downloading, subscription authentication, or scraping.
- Windows builder updated to bundle `soundcard` and `numpy`.

**Limitations:** Windows WASAPI capture and the full installer require real Windows testing. Not every endpoint or protected audio stream is capturable. The system output loopback captures all audible programs routed to that output, not just one browser tab. This feature does not bypass DRM or confer permission to reuse copyrighted recordings. Audio files listed as MP3/FLAC/etc. are browsable; the current pad loader only accepts its supported WAV encoding. The recorder uses a background thread, and may take a moment to stop and flush.

**Design:** Original Track City, MRQ/TRK/ARR, loop brace, waveform, pads and hardware mappings unchanged.
