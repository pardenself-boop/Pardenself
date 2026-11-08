# BOOM BAP TOOLBOXX — Build 062

Native Windows DAW prototype with Cook Up Matrix, 22 LABBs, a 32-slot sample deck, Track City, our sound banks, real master FX, and Native Instruments Maschine Studio control mapping.

## Windows installer

[Download Build 062](https://github.com/pardenself-boop/Pardenself/releases/tag/build-062). Choose **BOOM_BAP_TOOLBOXX_Setup_062.exe**. This single installer includes the app, Python runtime, audio/MIDI libraries and sound-check shortcut. You do not need to install Python or manage source files to run the installed app.

Build 062 is an unsigned development release. Windows 11 audio playback and physical Maschine Studio operation still need testing on the target PC. Native Studio HID, screens/LEDs, a VST build, and FX explicitly marked as previews are not implemented.

## Current UI

![Running Cook Up Matrix interface](validation/arranger061.png)

## Controller workflow

Open **STUDIO MAP** for the editable physical-control diagram and guided sixteen-pad learn. Arrange/Loop/Sound/Browse/FX contexts keep soft keys and encoders in sync with our instruments and chain. The display areas are software mirrors; physical screen output is not implemented. Use **MASCHINE SETUP** to scan/select the Studio's Controller Editor MIDI input, connect, choose a command/mode, and learn a physical control. Use **BANK PAD 1–16** for one physical pad map that follows the DAW bank; **PAD 1–32** remain absolute assignments. Projects save both controller bindings and audio source references.

The installer opens Cook Up directly, adds a desktop shortcut, and includes the runtime. Escape does not close the workspace; editing shortcuts leave text fields alone. MIDI note velocity reaches learned sample pads. In the Studio map, choose **LOOP** for the manual-based position/start/length controls.

The Start Menu **STREET SOUND CHECK (Audio + MIDI)** shortcut opens the test window. Close other MIDI clients if the Windows driver only permits one client at a time.

## Source and build evidence

- [Build 062 details](BUILD_062_README.md)
- [Workflow references and parity gaps](WORKFLOW_REFERENCE_061.md)
- [Controller guide](CONTROLLER_MASCHINE_STUDIO.md)
- [Windows test guide](TEST_AUDIO_MIDI_WINDOWS.md)
- [Windows CI](https://github.com/pardenself-boop/Pardenself/actions/workflows/windows-installer.yml)

The Windows pipeline runs the unit tests, packages the app, checks packaged startup, compiles Setup.exe, checks installation and installed-app startup, then tests uninstallation. The runner is Windows Server 2022, not a physical Windows 11 workstation. Audio/MIDI events used in automated tests are simulated.

Original uploads are preserved under original_uploads/. Earlier build notes are historical. The detailed decorative artwork in the user's visual reference has not been recreated.
