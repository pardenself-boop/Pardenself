# Build 066 — backend timing, same UI

No visual changes are included. Layout, colors, artwork, pads, arranger and existing menus are preserved.

The optional metronome and count-in use existing MIDI learn:

1. Start audio and connect Studio MIDI with the existing setup controls.
2. In MASCHINE SETUP, choose **METRONOME TOGGLE** in the existing COMMAND selector, set button mode, click LEARN NEXT PHYSICAL CONTROL and press a spare Studio button. Do the same for **COUNT IN TOGGLE** with another button. Existing mappings stay intact unless you intentionally relearn their address.
3. Use the learned metronome button for quarter-note clicks during playback. Beat one is accented in 4/4.
4. Enable count-in with its learned button, select your pattern/loop, arm REC and start playback. Hear four beats before the song advances and recording begins. No on-screen controls or countdown display are added.

Both preferences default off and are saved with projects. Closing/reloading never resumes an active count. Count-in is audible even if the ordinary metronome is off. It does not delay playback without REC. Pads/instruments may audition during the lead-in without writing notes. Stop/disarm cancels it.

Clicks reach the existing output after master FX and before master gain/safety. They are excluded from offline WAV export. Audio must already be started. Transport scheduling compensates for redraw work using monotonic deadlines; a long stall cannot create a catch-up callback burst. This is still GUI transport timing, not sample-accurate recording.

214 local tests pass, including clicks, four-beat gating, final-interval recording suppression, stop/reset, project preferences, export isolation and deadline behavior. Native Tk checks exercise the lead-in and recording transition while preserving the UI. Windows release checks verify upgrade from Build 065, user-file preservation, startup, close and uninstall. The installer remains unsigned; physical Studio screens/LEDs and real hardware timing remain unverified. Project format remains v3.
