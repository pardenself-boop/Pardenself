# Test audio and Native Instruments Maschine Studio

Use the full extracted Build 060 source folder on Windows with Python 3.11+ installed. No verified installer is included.

1. Connect your audio interface/headphones and Maschine Studio. Configure NI drivers and Controller Editor MIDI mode so Windows exposes the controller's MIDI input.
2. Double-click TEST_AUDIO_MIDI_DOUBLE_CLICK.cmd. This creates a local .test-venv, installs the runtime dependencies, and opens STREET SOUND CHECK.
3. Select your Windows output device, choose START AUDIO, then click BASS LABB or KEY 88. Check that sound is audible and note releases stop normally.
4. Select the Maschine Studio MIDI input and CONNECT. With MIDI PAD MODE unchecked, play pads to test instrument note-on/off. The MIDI IN indicator should respond. Choose ALL channels initially.
5. For sample pads, open the 32-pad deck, load a 16-bit PCM WAV into a pad, enable MIDI PAD MODE, and send its note (36 maps to pad 1; 67 maps to pad 32). This diagnostic uses absolute notes, not the workstation's bank-aware command mappings.
6. For transport and jog, open START_EXACT_LAYOUT.bat and MASCHINE SETUP. Scan/select the Studio input and CONNECT. Choose a command and mode, click LEARN NEXT PHYSICAL CONTROL, and operate that control once. The learn event is consumed; operate it again to test the command.
7. For sixteen pads shared across DAW banks, learn BANK PAD 1–16 in button mode and map BANK NEXT/BANK PREV to controller buttons. PAD 1–32 remain absolute assignments. Choose the encoder mode reported by Controller Editor for the jog wheel; do not assume the factory map.
8. Save the project and reopen it. Both legacy MIDI learn mappings and the Studio router's mappings should return. SAVE PROFILE JSON also supports a reusable controller profile.

Close/disconnect the standalone sound/MIDI test before opening that MIDI input in the workstation; some Windows MIDI drivers allow only one client at a time.

If live sound is silent, use EXPORT OFFLINE TEST WAV and play the WAV in Windows. Audible exported audio proves the render path, not live sound-device output. TEST_MIDI_DOUBLE_CLICK.cmd provides the detailed raw MIDI event log for checking note/CC numbers and encoder values. Record the selected device, incoming event, command, and observed result when reporting an issue.

Cloud verification: 111 automated tests plus actual Tk window checks passed. The audio engine renders non-silent stereo WAV offline. This does not verify Windows device playback, NI HID integration, Studio screens or LEDs, or the physical hardware.
