# Build 044 — 32-PAD STREET DECK

Adds a separate 32-pad WAV deck to STREET SOUND CHECK. Load individual 16-bit PCM WAV samples into all 32 pads, trigger by mouse, or enable MIDI PAD MODE for notes 36–67 (C2–G4 in common MIDI note naming; DAWs differ in octave labels). The instrument mode remains available.

Engine fixes: correct interpolation near sample end, reject malformed/unsupported WAV headers and invalid pad indices, bound active pad voices to 64. Computer keyboard note-off now targets the instrument active at note-on even if instrument selection changes.

Run `TEST_AUDIO_DOUBLE_CLICK.cmd` on Windows after installing dependencies from `app/requirements.txt`. The source package is not a Windows Setup.exe. Actual audio hardware/Maschine Studio must be verified on Windows.
