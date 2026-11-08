# BOOM BAP TOOLBOXX v1.8 — Hardware-first MIDI bridge

This is the v1.7 DAW plus a MIDI-mode hardware bridge and profile editor. It preserves the existing 22 LABBS, arranger, Cook Up interface and master bus.

## Windows startup without a BAT file

Open Command Prompt inside this folder (File Explorer address bar: `cmd`), then run:

    py -m pip install -r requirements.txt
    py toolboxx.py

Do not disable Smart App Control. If Windows blocks Python or flags a threat, stop and investigate.

## Mapping Studio hardware

1. Install the official Native Instruments driver / Controller Editor as needed. Enable MIDI mode for the Maschine Studio and configure its MIDI messages.
2. In TOOLBOXX, go to MIDI MAP, scan inputs, and connect the Studio MIDI port if one is exposed.
3. Click **MIDI HARDWARE SETUP**. Enter the MIDI channel (zero-based), note or CC number, choose `button` for click/button, or a relative CC mode for jog rotation, then assign a TOOLBOXX command.
4. Save the JSON profile. For jog rotation choose `HW JOG`, and for jog push choose `JOG CLICK`. Use BACK as `JOG BACK`.
5. MIDI modes differ across controller templates. Use the MIDI event details from your hardware/Controller Editor to choose the correct CC and encoder mode. Do not assume the default numbers in the setup test are actual Studio assignments.

**Limitations:** MIDI mode may not expose all controls. The Studio displays, LEDs and native HID protocol are NOT implemented or tested. This release adds an actual software MIDI event routing layer but cannot guarantee hardware operation until the physical unit is connected. All LABB audio and arranger commands remain in one engine.

Run `py -m unittest discover -p "test_*.py"` for offline tests.
