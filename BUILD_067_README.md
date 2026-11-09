# Build 067 — MIDI safety behind the same interface

The approved UI, artwork, colors, pads, arranger and menus remain unchanged. This update repairs input/note lifecycle behavior only.

Held instrument notes now release their original instrument even when you switch selection or armed instrument before releasing. Sustain retains that ownership. Two channels playing different instruments at the same pitch are independent. For the current synth's shared pitch on the same instrument, all unison voices wait for the last channel owner to release.

The bounded MIDI callback queue copies each message and tags real device callbacks with their connection generation. Old callbacks are ignored after reconnect/failure/close. Queue overflow discards stale buffered actions and releases tracked instrument notes on the GUI thread. It reports overload through the existing status rather than blocking the driver thread. Reduce controller event rate if this happens; overflow recovery can drop hits.

Errors in one mapped command no longer discard later messages from the same poll. Remapping a currently held key does not swallow its release, and orphan releases do not cut unrelated untracked voices. Existing saved mappings and MIDI-learn workflows remain in place.

If a backend reports its port closed, the app releases tracked notes and clears that connection. A manual MIDI SCAN also catches a connected input that disappeared from the input list. Use the existing CONNECT control to reconnect. No inactivity timeout, automatic USB reconnect or guessed HID protocol is introduced. Samples/transport continue running when MIDI disconnects.

230 tests pass locally. Actual Tk checks exercise the shared MIDI queue, a rendered synth note, a changed armed instrument and recovery from overflow. The Windows pipeline verifies installation over Build 066, preservation of an existing user file, startup, close and uninstall before publishing. Hardware/device timing still needs testing on your Windows 11 PC. The installer is unsigned and native Studio screens/LEDs remain unfinished. Projects continue to use v3; controller profile schema is unchanged.
