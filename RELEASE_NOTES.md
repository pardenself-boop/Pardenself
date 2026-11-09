# TOOLBOXX Build 065 — expressive pad recording

Use **MENU → CHECK FOR UPDATES…** or install BOOM_BAP_TOOLBOXX_Setup_065.exe over your current version. The main interface design is preserved.

- Arm REC, start playback and play sample pads to overdub sixteenth-note pattern steps with incoming MIDI velocity. Bank-relative learned pads, absolute pad commands and unmapped pad notes all use the same recording path. Mouse pad hits can also record at their default strength. Sequencer playback does not record itself.
- Selected pattern clips record into their referenced pattern, with trim/slip source phase respected. With no clip selected, recording targets the main pattern. Selected non-pattern clips and hits outside the selected clip are not written. Each pattern repeats every 16 steps; repeated hits in the same step replace that step's velocity.
- Live playback and Track City WAV bounce preserve soft/hard hit dynamics. Simultaneous clips sharing a pad hit use the strongest velocity in both paths, matching the existing live deduplication behavior.
- **MENU → UNDO LAST PAD TAKE / REDO LAST PAD TAKE** restores one pad recording pass, separately from arranger undo. Stop recording or playback first. Take undo refuses to overwrite cells edited afterward. History is session-only; new project loading clears it.
- REC shows its armed state. Stopping playback cancels its scheduled timer, preventing duplicate playback chains after a quick restart. Recording uses a monotonic transport clock and nearest-sixteenth quantization; this is not sample-accurate/free-time MIDI capture.
- Existing boolean patterns and older projects still load. **New saves use project format v3 to preserve velocity; older app builds cannot open these new files. Save a separate copy if you need the original project for an older build.**

200 automated tests pass locally. Native Tk checks exercise a learned pad through the main MIDI queue, recording, take undo/redo, project save/load and step-grid rendering. The Windows release pipeline requires upgrade from Build 064, user-file preservation, installed startup, normal launch/close and uninstall checks before publication.

This is an unsigned development build. Actual Windows 11 audio/controller verification, physical Studio screens/LEDs, external plug-in hosting and other documented unfinished work remain separate.
