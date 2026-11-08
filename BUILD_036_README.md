# Build 036 — MIDI sustain and panic reliability

Added channel-aware CC64 sustain-pedal handling, CC120 All Sound Off and CC123 All Notes Off handling, invalid MIDI event guards, and regression tests to the existing STREET WIRETAP DAW dispatcher. Existing MIDI bindings and visual design are preserved.

This is source code, not a compiled Windows installer. Tests run in this environment do not verify Windows drivers, audio interfaces, Maschine HID, or hardware MIDI ports. No claim of full DAW completion is made.
