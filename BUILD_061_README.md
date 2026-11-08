# TOOLBOXX Build 061 — Street Control Deck and range editing

Build 061 adds an original scuffed-metal NYC boom-bap skin, an editable physical-control diagram based on Maschine Studio's layout, synchronized software screen mirrors, individual/16-pad MIDI learning, and loop-brace range editing. It continues the existing native Tkinter DAW.

The primary controller is Maschine Studio, including the user's intended two-display hardware workflow. Actual display/LED/HID output is not implemented: the map's screens mirror software state only. MIDI hardware is not attached in the cloud, so all device-event checks remain simulated. See WORKFLOW_REFERENCE_061.md for the manual/release-note references and remaining parity work. This is not a complete clone of Maschine or MPC software.

## Use

The installed app's STUDIO MAP button opens the physical map. Select a hotspot, choose a command and mode, then learn a real MIDI event or enter its address. TEACH 16 PADS captures one unique physical input per pad; mappings commit after the sixteenth input. Cancel leaves the old map untouched. Save Map saves control metadata, MIDI addresses/modes and edited hotspot positions. Photo backgrounds are optional per-window visuals; hotspot edits persist, photographs are not embedded into map profiles.

In Cook Up, drag the loop brace edges or body above Track City. One complete drag is one undo step. In MRQ, drag across time and tracks to scope the range; TRK uses the focused track; ARR uses all tracks. RANGE opens copy/cut/paste/clear/duplicate/duplicate+insert tools; right-click/double-click the brace also opens them. Keyboard shortcuts are Ctrl+C/X/V/D and Delete. Clear leaves a gap and paste overlays at the playhead. Range edits preserve media references, pattern/note metadata, source offsets and audio fades; they do not create destructive audio files.

## Validation and distribution

Local baseline: 111 tests. Current suite: 129 passing tests, covering range scope, region splitting and fades, insertion/undo, editable hotspot bounds, profile persistence, two-direction encoder routing, and staged pad learning with duplicate/cancel handling. Actual Tk checks passed for all three windows and the new mapping/range interactions.

The Windows workflow packages the executable, checks startup including the controller map, compiles Setup.exe, silently installs it, checks installed startup, uninstalls it, and uploads only the single installer. After those gates pass, a release job publishes the verified development installer. Expected artifact: BOOM_BAP_TOOLBOXX_Setup_061.exe. The release is unsigned; local Windows 11 audio and physical controller testing remain necessary.
