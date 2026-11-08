# Build 057 — Track City event scheduling repair

Fixed simultaneous audio-region and LABB MIDI note events at identical frame positions. Event sorting now compares sample positions only rather than trying to order clip/note dictionaries. Invalid tempo values (zero, negative, NaN, infinity, boolean) are rejected before duration calculation.

Three new regression tests added. 90 Python unittest tests passed on Linux; Python compilation and archive integrity verified. This remains source/development code. Live Windows audio, Maschine Studio and Setup.exe compilation are not verified.
