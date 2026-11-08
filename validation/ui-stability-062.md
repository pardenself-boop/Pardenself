# UI stability checkpoint

The existing Cook Up layout and colors are preserved.

- Text fields retain normal copy, paste, undo and Delete behavior; arranger shortcuts do not edit clips while typing.
- Cook Up supports Ctrl+Y redo. Handled arranger shortcuts stop propagation.
- Escape no longer closes the main workspace or terminates the DAW.
- Customer launch opens Cook Up and hides the underlying workstation; the DAW button can reopen it.
- Closing releases MIDI through the existing panic/disconnect path, stops audio, cancels transport and destroys the root even if audio cleanup fails. Repeated close calls do not repeat cleanup.

Validation: baseline 146 tests passed; current 151 tests passed. Native Tk startup smoke passed for workstation, Cook Up, controller map, sound browser and FX (22 LABBs, 32 pads). An actual Tk keyboard check verified text copy/Delete isolation, one arranger copy command, Escape safety and shutdown on display :99.

These source changes have not yet been packaged or tested on Windows 11. The published Build 061 installer does not include this checkpoint. Actual audio devices and Maschine Studio remain unverified.
