# Build 035 — STREET WIRETAP LIVE DISPATCH

New shared `street_midi_dispatch.py` routes MIDI events to mapped DAW commands, automation parameters and playable notes, including MIDI note-off and note-on velocity zero. The Tk app uses it on the GUI event polling thread. Mapped note buttons do not accidentally trigger a musical note. Legacy MIDI Learn is preserved.

This is a source release and Windows installer builder, **not** a compiled Setup.exe. Windows audio and physical Maschine Studio/Trackman testing remain necessary. Existing GUI design was not modified.
