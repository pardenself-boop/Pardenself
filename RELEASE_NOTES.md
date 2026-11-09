# TOOLBOXX Build 067 — MIDI reliability, same UI

Use the existing **MENU → CHECK FOR UPDATES…** or install BOOM_BAP_TOOLBOXX_Setup_067.exe over your current installation. **The locked UI is unchanged.**

- Held instrument notes retain their original MIDI channel and instrument owner. Releasing after changing the selected/armed instrument targets the original sound. Sustain release uses the same ownership. An untracked note-off no longer cuts a mouse/sequencer note simply because its pitch matches.
- Same-pitch notes on different instruments/channels release independently. When channels share the same instrument and pitch, the current synth releases the shared pitch only after its final channel owner releases; individual unison voices are not separately addressed.
- Full input queues request recovery on the GUI thread: discard the stale backlog, release tracked held notes and report overload. The driver callback stays nonblocking and does not call Tk or the synth. Some performance events are intentionally lost during overload; reduce the controller message rate.
- Incoming messages are snapshotted before queueing. Connection generations reject queued or late callbacks from a closed/failed connection after reconnecting or shutting down.
- One bad mapped command cannot abort the remainder of an input batch and swallow a later note-off. Invalid note/CC values are rejected before legacy learn/command execution.
- Standard MIDI channel panic CC120/123 is handled before legacy command mappings, so a mapping cannot swallow an emergency note release.
- Relearning a held note as a mapped button, including a legacy mapping, still allows its original voice to release.
- A port explicitly marked closed by its MIDI backend is disconnected and tracked notes are released. A manual SCAN also closes a connected port missing from the returned input list. Playback/audio are not stopped. Reconnect through the existing controls; this is not automatic USB hot-plug recovery.

230 automated tests pass locally, including simulated overload/disconnect/context-switch cases with the actual synth. Native Tk checks verify a non-silent rendered note and its release after overload while the UI stays unchanged. Windows publication requires upgrade from Build 066, user-file preservation, installed startup, normal launch/close and uninstall checks.

The installer is unsigned. Real Windows 11 audio and physical Maschine Studio behavior remain unverified. Physical Studio screens/LEDs and other documented unfinished features remain separate. Project format remains v3; controller profiles remain compatible.
