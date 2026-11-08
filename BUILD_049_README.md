# Build 049 — 32-Pad Kit Vault

STREET SOUND CHECK now supports saving/loading 32-slot `.tbkit` manifests. Kits reference external WAV files by relative path; they do not embed audio. Loading validates every WAV in a staging engine before replacing live pad slots. Missing files or invalid WAVs leave the current kit unchanged.

Run `TEST_AUDIO_DOUBLE_CLICK.cmd` and open the 32-pad deck. Windows audio/MIDI and installer remain unverified.
