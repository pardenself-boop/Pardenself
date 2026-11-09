# TOOLBOXX Build 066 — recording timing, UI preserved

Use the existing **MENU → CHECK FOR UPDATES…** or install BOOM_BAP_TOOLBOXX_Setup_066.exe over your current installation.

**The current UI is locked and preserved: no new panels, buttons, menu items, layout, color or artwork changes. The Cook Up UI source is identical to Build 065.**

- Adds optional original synthesized quarter-note monitor clicks and a four-beat recording count-in through the existing MIDI-learn system. Choose METRONOME TOGGLE or COUNT IN TOGGLE from the existing hardware setup command list and teach spare controller buttons. Neither is enabled by default.
- Starting playback with REC armed and count-in enabled holds the song position for one bar. Pads/instruments can audition during the lead-in without writing notes; recording begins after the full bar. Ordinary playback without REC is not delayed. Stop, disarm or disable count-in to cancel it.
- The monitor click is mixed after master FX and before master gain/safety. WAV bounce excludes it and leaves the live click voices alone. Project preferences persist; active countdown/click voices are never restored on load.
- Transport timers use monotonic deadlines so redraw work does not accumulate into each tick interval. A long stall resets the deadline instead of creating a burst of catch-up callbacks. This remains the existing GUI transport, not a new sample-accurate clock.

214 automated tests pass locally. Native Tk checks cover count-in gating, the recording transition and stopping, with UI sources unchanged. Windows publication requires upgrade from Build 065, user-file preservation, installed startup, normal launch/close and uninstall checks.

This is an unsigned development build. Real Windows 11 audio/controller timing still needs testing. Physical Studio screens/LEDs and other documented unfinished features remain separate. Project saves continue to use v3 from Build 065.
