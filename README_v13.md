# BOOM BAP TOOLBOXX v1.3 — 22 LABBS / Shared Master

Run `START_WINDOWS.bat` on Windows with Python 3.11+ installed. Open **22 LABBS** from the top bar. Select a LABB and click a note to audition its synthesized patch. Press **START AUDIO** and choose a working audio device in the main interface first if needed. All instrument voices, sample pads, and audio regions mix through the **same output bus**, with DC blocking, soft clipping, a ceiling and a peak readout.

### What is real
- 22 distinct **playable synthesis patch definitions** with independent envelopes, filter settings, volume, mute/solo, and note triggering. These are basic synthesized voices, not 22 fully advanced sample/stem instruments.
- One shared engine, master output processing, master gain/drive controls, project persistence for LABB parameters, and a 22-LABB selector.
- The existing Track City audio/pattern arranger and virtual Studio control remain available.

### Not implemented yet
- Native Maschine Studio USB HID integration or physical screen output; full MIDI note routing to all LABBS; production-grade DSP, oversampling, lookahead limiter, PDC, VST hosting, advanced synthesis, genuine stems/warp, or automated full end-to-end Windows validation.
- Some COOK UP MATRIX controls are still visual placeholders. The SOUL orb currently changes the simple low-pass filter on instrument voices; other orb values are stored but do not process audio.

The shared bus ceiling prevents output samples from exceeding its configured threshold, but it cannot guarantee distortion-free sound or eliminate underruns.
