# BOOM BAP TOOLBOXX — Windows + Studio Hardware Map v0.6

## Start
On Windows with Python 3.11+, extract the ZIP, open `toolboxx_v05`, and double-click `START_WINDOWS.bat`.

Click **STUDIO HARDWARE MAP** in the top toolbar to open the new controller simulator. Press the named hardware buttons to dispatch commands into the existing Track City DAW, or right-click a button to choose it for mapping. Select a command, optionally enable SHIFT LAYER, then click ASSIGN MAPPING. SAVE PROFILE and LOAD PROFILE use portable JSON files.

The two 480×272 **simulated** display canvases show Chop Labb and Track City, using the shared application state. The waveform is synthetic placeholder data, **not** a decoded audio waveform. Page tabs for STEMS and FX LABB are placeholders until implemented.

## Tested
`python -m unittest discover -v` — 12 tests passed in the development environment. Python modules compile. This does not verify Windows launch, ASIO, physical Maschine Studio HID/USB, or hardware screen output.

## Current limitations
- The native USB hardware driver and screen blit transport are not connected. The Studio layout is a functional software control simulator, not a precise photograph or physical button-position replica.
- The audio engine remains the v0.5 WAV sampler with sounddevice output; native ASIO selection is not yet implemented.
- Track City arrangement clips are editable containers but are not yet connected to a timeline playback scheduler.
- Existing arranger edit model, MIDI Learn and project features are retained from v0.5.
- MPC Key 61 has no MIDI control mappings; use as an audio device only if available to the application.

## Engineering next
Native Encdr Studio adapter, exact hardware-layout map and LEDs; page-aware encoder mappings; arranger pattern playback and stems routing.
