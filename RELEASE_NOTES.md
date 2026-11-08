# TOOLBOXX Build 063 — in-app updates

Download **BOOM_BAP_TOOLBOXX_Setup_063.exe** and install over Build 062. The same TOOLBOXX app and design remain in place.

- **MENU → CHECK FOR UPDATES…** checks official TOOLBOXX GitHub releases, including development builds.
- Download the next installer in the background, verify its size, Windows executable header and SHA256, then save your project and choose **INSTALL UPDATE**. The file is verified again before launch. Setup opens and the DAW closes only after your confirmation.
- Offline requests, incomplete downloads and failed installer launches leave the current app installed. Checking or downloading does not stop playback. There are no automatic startup checks or forced installations.
- Installed build identity comes from bundled release metadata, so the UI and update checker use the same version.
- The standalone Sound Check sample-pad mode now preserves MIDI hit velocity too.

176 automated tests pass locally. The Windows pipeline tests packaging, installation over Build 062, user-file preservation, installed startup, normal launch/close and uninstall before publishing.

To test audio and MIDI, use the Start Menu **STREET SOUND CHECK (Audio + MIDI)** shortcut. Select your output, choose START AUDIO, and click BASS LABB or KEY 88. Select the Studio MIDI input and CONNECT; use ALL channels and leave MIDI PAD MODE unchecked for instrument testing. Close/disconnect Sound Check before connecting that port in the DAW. See TEST_AUDIO_MIDI_WINDOWS.md.

This is an unsigned development installer. SHA256 checks detect corrupt or mismatched downloads; they do not replace Windows publisher signing. Windows may show an unknown-publisher warning. Physical Studio screens/LEDs, external VST hosting and full scene hierarchy remain unfinished; actual Windows 11 audio/controller performance still needs testing.
