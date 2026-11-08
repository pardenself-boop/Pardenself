# Build 056 — Track City LABB MIDI Song Bounce

Adds LABB MIDI note clips to Track City's offline WAV bounce alongside pad-pattern hits and audio regions. The main workstation passes its NoteLane to the exporter. Note clips honor start, length, slip offset, mute/solo, and repeat on a four-beat cycle. MIDI note durations are interpreted in beats and converted to seconds for the existing synthesizer. Validates notes and limits event counts.

Verification: 87 Python unittest tests passed, including a rendered LABB instrument WAV. Python compileall passed. Live Windows audio, Maschine Studio, and compiled installer have NOT been verified. The DAW is not yet a production release.
