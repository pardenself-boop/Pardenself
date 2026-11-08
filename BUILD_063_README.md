# Build 063 — in-app updates

Install BOOM_BAP_TOOLBOXX_Setup_063.exe over the existing app. No manual uninstall or separate runtime is needed. Save projects first and keep project WAV sources in their existing locations.

Open **MENU → CHECK FOR UPDATES…**. Click **CHECK FOR UPDATES**, then **DOWNLOAD** when a newer build exists. After the download is verified, save your project and click **INSTALL UPDATE**. Confirm to close TOOLBOXX and open Setup, then click **Install TOOLBOXX**. Setup opens Cook Up when finished.

The checker includes our published development releases and compares numeric build numbers. It never installs automatically. Offline failures leave the session usable. Downloaded installers are staged under the user's local application data, checked by size/MZ header/SHA256, and rechecked before launching. This does not provide Windows publisher signing; builds remain unsigned.

176 local tests pass. The Windows release pipeline checks installation over the published Build 062 and preservation of an existing user file, plus packaged/installed startup, normal Cook Up launch/close and uninstall. See release evidence for the exact run and checksum.

For audio and MIDI testing, see [the installed-app test guide](TEST_AUDIO_MIDI_WINDOWS.md). The existing design and all Build 062 features are preserved. Physical Studio screen/LED output and other documented feature gaps remain unfinished.
