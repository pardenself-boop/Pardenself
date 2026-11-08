# v0.9 — Studio Jog Click / Hardware-First Editing

This build extends v0.8; it does not replace the audio/arranger engine.

Open **STUDIO HARDWARE MAP**. The simulator now includes JOG LEFT, JOG RIGHT, JOG CLICK, BACK and edit-operation buttons. Use EDIT MOVE/TRIM L/TRIM R/SLIP/MARQUEE/LOOP L/LOOP R, rotate jog, click to commit, BACK to cancel. SHIFT toggles fine 1/16-beat adjustments; regular jog adjusts in 1/4-beat increments. In SELECT mode, jog rotation changes focused clip and click selects it. All edits use the existing Arranger model and undo stack. SHIFT+click toggles multi-selection.

**Hardware status:** virtual simulator only. USB HID integration and physical device verification are still outstanding. The hardware buttons in this screen are schematic, not an exact physical overlay. Audio timing and format limitations from v0.8 remain.
