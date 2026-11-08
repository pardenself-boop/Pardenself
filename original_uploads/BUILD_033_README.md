# Build 033 — STREET WIRETAP hardware diagnostic

Run `TEST_MIDI_DOUBLE_CLICK.cmd` on Windows (requires Python and tkinter). This is a **MIDI test utility**, not the final customer installer.

- SCAN discovers available MIDI input ports via mido/python-rtmidi.
- CONNECT monitors actual incoming MIDI messages with channel, note/CC and velocity/value.
- DEMO NOTE verifies the diagnostic UI without hardware.
- LEARN NEXT assigns incoming controls to named TOOLBOXX commands; save/load JSON mapping.
- Status and red activity indicator show incoming messages.
- Audio, Maschine Studio proprietary HID/screens/LEDs, and full DAW integration are **not** verified by this utility.
- If no MIDI ports appear, check NI Controller Editor MIDI mode, USB/power, and installed drivers.

Installation for this diagnostic: `py -m pip install mido python-rtmidi`. The DAW remains in the `app` folder, unchanged by this diagnostic.
