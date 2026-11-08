# Test audio and Native Instruments Maschine Studio

Use the installed app. Python and source files are not needed.

## Audio first

1. Open Windows Start and search for **STREET SOUND CHECK**. Open **STREET SOUND CHECK (Audio + MIDI)** under BOOM BAP TOOLBOXX.
2. Select your headphones, speakers or audio interface under **Windows output device**. Click **REFRESH DEVICES** if needed, then **START AUDIO**.
3. Click **BASS LABB** or **KEY 88**. You should hear a note and see the output meter move. Start with your speaker/headphone volume low.
4. If silent, use **EXPORT OFFLINE TEST WAV** and play the saved WAV in Windows. Audible exported sound proves the render path; it does not verify live device output. Note any message shown at the bottom of Sound Check.

## MIDI input

1. Connect Maschine Studio and use NI Controller Editor MIDI mode so Windows exposes its MIDI port. Close other software using that port if the driver allows only one client.
2. In Sound Check, click MIDI **SCAN**, select the Studio input and **CONNECT**.
3. Set CHANNEL to **ALL** and leave **MIDI PAD MODE** unchecked. Select BASS LABB or KEY 88 under MIDI → INSTRUMENT.
4. Press/release a pad. The **MIDI IN** indicator should respond, the status should show the incoming event, and the selected instrument should sound when audio is running.
5. To test samples, open **OPEN 32-PAD STREET DECK**, load a mono/stereo 16-bit PCM WAV into pad 1 and enable **MIDI PAD MODE**. This diagnostic uses notes 36–67 → pads 1–32. Your custom Studio template may send other notes; use the DAW's learn function for those addresses. Build 063 preserves pad velocity in this diagnostic; Build 062 uses full-strength sample hits in Sound Check.

## Use the controller in the DAW

Close Sound Check before connecting the same MIDI input in TOOLBOXX. In Cook Up, open **MASCHINE SETUP**, select the Studio input and **CONNECT**. Open **STUDIO MAP → TEACH 16 PADS** and press the requested pads in order. Learned BANK PAD commands follow bank A/B.

Use the map's context selector for ARRANGE, LOOP, SOUND, FX or BROWSE. Learn the eight physical soft keys to SURFACE KEY 1–8 and encoders to SURFACE KNOB 1–8 + with the actual relative mode set in Controller Editor. On LOOP, knobs 1/3/4 change loop position/start/length; soft keys 4/5 set whole-song range and toggle looping. Jog and transport commands can be learned separately. Save the project or controller map afterward.

For the main DAW's output, choose **DAW** in the top bar to open the underlying workstation's AUDIO OUTPUT controls. Scan/select your output and click **START**. Audio does not start automatically.

If something fails, report the selected output, whether the on-screen instrument button makes sound, whether MIDI IN flashes, and the exact status/error text. Studio physical screens and LEDs are not driven yet.
