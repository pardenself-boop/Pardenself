# Build 062 — Windows installer checkpoint

Open `BOOM_BAP_TOOLBOXX_Setup_062.exe`, click **Install TOOLBOXX**, and the main Cook Up workspace opens after installation. The installer supplies the runtime and libraries and adds desktop and Start Menu shortcuts. Keep projects and source WAVs in your own folders; projects reference those WAV files.

The approved UI design is preserved. This checkpoint adds safer keyboard editing and shutdown, MIDI sample-pad velocity, a manual-based Studio Loop page, and consistent controller navigation into our own sounds and FX.

## First test

1. Install and open TOOLBOXX. The version in the Cook Up title should be Build 062.
2. Use the Start Menu **STREET SOUND CHECK (Audio + MIDI)** shortcut to test your audio output and see incoming MIDI. Close it before opening the same MIDI port in the DAW.
3. In Cook Up, open **MASCHINE SETUP**, select the Studio's Controller Editor MIDI port, connect, and return to **STUDIO MAP**.
4. Use **TEACH 16 PADS** to learn your physical pad addresses. Bank A/B follows the same sixteen learned pads. Load a 16-bit PCM WAV and check soft/hard hit dynamics.
5. Select LOOP in the map's context selector. Knobs 1/3/4 control position/start/length. Soft keys 4/5 control whole-song range and loop on/off. Learn the contextual SURFACE commands to your actual knob/button addresses and encoder modes.
6. Save a project, reopen it, and verify WAV references, mappings and FX state.

The app does not start audio automatically. Choose and start your audio output explicitly. If a MIDI driver permits only one client, close other applications using that port first.

## Validation and limits

162 source tests pass, including audio-render velocity and actual Tk startup checks. Windows CI must also pass before the installer is published. See the release page for its run and SHA256.

The installer is unsigned; Windows can display an unknown-publisher warning. Physical Studio screens/LEDs are not driven yet. Real Windows 11 audio/controller operation remains unverified. These limits cannot be resolved by packaging alone. This is a development testing checkpoint, not a completed commercial DAW.

See [workflow references](WORKFLOW_REFERENCE_061.md), [controller guide](CONTROLLER_MASCHINE_STUDIO.md) and [release notes](RELEASE_NOTES.md).
