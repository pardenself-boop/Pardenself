# TOOLBOXX Build 061 — Street Control Deck

Download and run BOOM_BAP_TOOLBOXX_Setup_061.exe. This is one Windows x64 installer with the app, embedded Python runtime, audio/MIDI libraries and sound-check shortcut.

- Editable Studio-shaped control diagram with custom NYC boom-bap styling, original skyline/scuff textures, pads, eight soft buttons, eight knobs, jog wheel, groups and transport/edit buttons.
- Select a physical control, assign its MIDI address or learn its actual message, and save/load the editable map. Hotspot positions persist in profiles and projects. Optional photo backgrounds can be loaded locally for the current window.
- Guided sixteen-pad learn captures real incoming addresses, rejects duplicates and stages the map until all pads are learned. Cancellation preserves the existing map. Both banks use the same physical pads.
- Two synchronized software display mirrors show the real selected pad waveform and Track City state.
- Loop brace above the arranger with hover cursors, grid snapping, a single undo step per drag, and loop on/off/all/focus commands.
- MRQ ranges span dragged tracks, TRK ranges stay on the focused track, and ARR ranges cover all tracks. Range copy, cut, paste, clear, duplicate and duplicate-with-insert preserve audio/pattern/note references and source offsets. Audio fades are preserved when ranges split regions.

144 automated tests pass locally; real Tk checks exercise the physical map, pad learn/dispatch, loop undo and track-range copying. This release is published only after Windows packaging, installer, installed-startup and removal checks pass.

This is an unsigned development build, not a complete Maschine/MPC feature clone. The physical Maschine Studio screens, LEDs and native HID are not driven by this software. The two screen areas in the map are software mirrors. Actual Windows 11 audio and controller hardware remain unverified. Existing FX marked as previews remain planned. Sample audio is referenced, not embedded into projects.

## Integrated sound and FX workflow

The shared surface context now has Arrange, Sound, Browse and FX pages. Learned SURFACE KEY and SURFACE KNOB commands follow that context. The sound editor browses all 22 LABBs plus eight original NYC starting points and user patch memory. BLOCK EQ, BROWNSTONE COMP, DUST DRIVE and IRON CEILING process real master-bus audio. Chain ordering, bypass, parameters and project recall reach both live rendering and isolated Track City bounce. Per-sound/group insert routing and external VST/NKS hosting remain separate work; other explicitly planned slots still have no DSP.
