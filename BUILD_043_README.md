# Build 043 — STREET SOUND CHECK: WAV + computer keyboard

Audio test UI now has a WAV loader for the selected LABB and an editable root note (0–127). Loaded WAV files use the existing STREET CRATE sample engine and master output; incoming MIDI triggers the selected LABB. The computer keyboard (A W S E D F T G Y H U J K) plays and releases notes when focus is outside text inputs. This provides a fallback sound test when a MIDI port is unavailable.

The original TOOLBOXX main UI, arranger, and MIDI mappings were not redesigned. Windows audio-device and hardware tests remain necessary; this is source code, not a compiled Windows Setup.exe.
