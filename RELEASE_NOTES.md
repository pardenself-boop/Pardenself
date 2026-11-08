# TOOLBOXX Build 062 — Studio workflow and smoother startup

Download **BOOM_BAP_TOOLBOXX_Setup_062.exe**, open it and click **Install TOOLBOXX**. One installer includes the application, Python runtime and audio/MIDI libraries. Setup adds a desktop shortcut and opens Cook Up when finished. No separate Python installation or source files are needed.

The existing charcoal, rust, mint and worn-metal TOOLBOXX interface is preserved.

- Opens the main Cook Up workspace directly. The DAW button still opens the underlying workstation.
- Text entry keeps normal copy/paste/Delete behavior; arranger shortcuts do not edit clips while typing. Ctrl+Y redo is available in Cook Up. Escape no longer closes the workspace.
- Shutdown releases MIDI, sends the existing panic cleanup, stops audio and avoids repeated device cleanup.
- Sample pads now preserve incoming note velocity, including learned absolute pads, bank-relative pads and legacy MIDI mappings. Soft hits play quieter; overlapping voices retain independent strength. Mouse/step triggers retain their full-strength default.
- Adds a dedicated Studio-style Loop context: knob 1 moves the loop, knob 3 adjusts its start, knob 4 adjusts length; soft button 4 selects the whole song and button 5 toggles looping. Choose LOOP in STUDIO MAP or MIDI-learn SURFACE LOOP. Contextual keys and knobs follow the active page.
- New map navigation targets our sound banks, instrument editor, FX rack and arranger context. Existing saved user mappings remain intact.
- Preserves 22 LABBs, 32 sample slots, guided sixteen-pad learn, editable controller map, MRQ/TRK/ARR range editing, our original sound bank, real master-bus FX and isolated WAV bounce.

162 automated tests pass in the source checkpoint. Publication requires Windows unit tests, packaged startup, installer compilation, installation, installed startup and uninstall checks. The Windows runner uses Server 2022; actual Windows 11 audio devices and Maschine Studio hardware still need testing.

This is an **unsigned development build**. Windows may show an unknown-publisher warning. The physical Studio screens/LEDs and native HID backend are not implemented; the two display areas are software mirrors. External VST/NKS hosting, full scene hierarchy and velocity recording into the boolean step matrix are not included. Other FX marked planned remain planned. Project audio is referenced rather than embedded. This release does not claim a finished commercial DAW or complete Maschine/MPC parity.
