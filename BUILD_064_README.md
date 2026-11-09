# Build 064 — shared Audio + MIDI setup

From Cook Up, choose **MENU → AUDIO + MIDI SETUP…**.

1. Select your audio output (SCAN if needed), click START AUDIO and TEST BASS or TEST KEYS.
2. Put Maschine Studio in MIDI mode with SHIFT + CHANNEL. Select its input and CONNECT.
3. Press pads or turn a knob. MIDI IN, the message count and note/CC log show activity. Sound still follows the DAW's actual mappings and loaded instruments/samples; an incoming message does not imply a particular factory mapping.
4. Use LEARN / STUDIO MAP to teach pads, knobs, transport and jog commands. COPY TEST REPORT lets you paste the current status and recent events into chat.

The setup shares the main audio engine and MIDI port, avoiding a second test client. Closing the window leaves them connected. Opening it does not start audio or connect MIDI. Test notes use existing patches/FX without changing those settings, so mute/volume/FX settings still affect what you hear.

Build 063 users can install this through MENU → CHECK FOR UPDATES. Save projects first. Other users can run BOOM_BAP_TOOLBOXX_Setup_064.exe over their current installation. The UI design, updater, Studio map and earlier features remain in place.

Validation: 184 source tests plus native Tk checks. The Windows pipeline verifies upgrade from Build 063, preservation of an existing user file, normal installed launch and uninstall before release. Check the release page for its run and checksum. This does not establish real Windows 11 audio/controller verification. The installer is unsigned; physical Studio screens and LEDs remain unfinished.
