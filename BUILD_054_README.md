# Build 054 — Track City WAV bridge

Added **BOUNCE WAV** to the main workstation transport. It converts actual Track City pattern clips to sample-accurate pad hits, respecting clip trim, source offset, repeat, track mute and solo. It renders with a separate offline engine so it does not interrupt the live audio engine. WAV samples must be loaded into the pads used by the arrangement. Audio-region clips and LABB MIDI clips are not yet included in this bounce; this is a pattern-pad bounce, not a complete song mix.

Run `python -m unittest discover -s tests -q` from the extracted root. Windows installer and real hardware remain unverified.
