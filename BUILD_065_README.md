# Build 065 — record pad dynamics

1. Start your audio output and connect Studio MIDI through MENU → AUDIO + MIDI SETUP.
2. Load WAVs into the sample pads, then select a pattern clip in Track City. Clips referencing the same pattern share its steps.
3. Set a loop covering that clip, arm REC and press PLAY. The REC control changes color when armed.
4. Play your pads. New hits are snapped to the nearest sixteenth in the 16-step source pattern, preserving hit strength. Slipped/trimmed clips keep their source phase. Existing steps remain unless you play that same pad/step again.
5. Stop recording or playback. MENU → UNDO LAST PAD TAKE / REDO LAST PAD TAKE handles the recording pass separately from arranger edits. It will not overwrite a step changed since the take.
6. Save a project or bounce Track City to WAV; both preserve velocity.

With no clip selected, the main pattern is recorded. A selected non-pattern clip or a hit outside the selected pattern clip is not written. REC alone arms recording; playback must also be running. This is quantized pattern overdub, not a new scene engine or free-time MIDI recorder. Take undo is kept in memory and cleared on project load. Clicking a grid step still toggles it off or on at full strength.

Older projects remain readable. New saved projects use format v3; older application builds cannot read them. Use Save to create a separate copy before replacing a project you still need in an older build.

200 local tests pass, plus native Tk learned-pad recording/undo/redo/save/load checks. Windows publication verifies upgrade from Build 064 and normal installation, startup, close and uninstall. Use the release page for its exact run and hash. Real Windows 11 audio and physical Studio hardware remain unverified. The installer is unsigned; physical controller screens/LEDs are not added by this release.
