# Build 037 — STREET WIRETAP callback safety

Added `app/street_midi_queue.py`, a bounded, thread-safe MIDI ingress bridge. It snapshots incoming MIDI events on the device callback thread and processes them on the UI thread through `StreetMidiDispatch`. Queue overflow requests a panic before processing retained events to prevent dropped note-off messages leaving notes sounding indefinitely. Added four regression tests for ordering, snapshots, bounded draining, overflow panic and ignored unsupported messages.

**Integration status:** This is a tested bridge module, not yet wired into the live `toolboxx.py` MIDI callback; the existing DAW still uses its original queue. No Windows hardware or installer validation was performed. This release is not complete.
