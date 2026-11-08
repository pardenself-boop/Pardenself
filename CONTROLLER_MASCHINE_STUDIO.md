# Primary controller: Native Instruments Maschine Studio

Maschine Studio is the primary physical controller for TOOLBOXX. Preserve its 4x4 pad orientation (1–4 along the bottom), jog workflow and transport access. The DAW has 32 sample slots in two banks of 16. Its screen is a companion to the controller workflow.

Use MASCHINE SETUP in Cook Up for MIDI assignments and save/load Controller Editor profiles. Pad 1–32 commands and bank navigation are available alongside jog/transport commands. Map the messages actually emitted by the user's Controller Editor configuration; do not invent or claim a verified factory mapping. The current default unassigned note path maps notes 36–67 to absolute pad slots 1–32. Changing the on-screen bank does not transpose these default incoming notes. For the same 16 physical pads to follow the active DAW bank, learn BANK PAD 1–16 commands instead. Configure bank-specific messages or assign explicit pad commands as appropriate.

Use the workstation MIDI MAP page to scan/connect the device's MIDI port. Maschine Studio needs its NI drivers and Controller Editor MIDI mode configured on Windows. Current integration is MIDI; native HID, screen and LED feedback are not implemented or verified. Hardware tests require the real Maschine Studio.

Build 060 adds scan/connect/disconnect and mode-aware physical MIDI learn directly in MASCHINE SETUP. The first learn event is consumed; use the next event to test the mapping. Selecting a non-jog command chooses button mode. Project save/load now includes the Studio router mappings; loading a legacy project retains the current hardware profile. No MIDI port is opened automatically.
