# BOOM BAP TOOLBOXX v1.7 — Advanced MIDI LABB / Audio Test

Launch START_WINDOWS.bat, choose 22 LABBS to access eight parameter sliders per instrument, MIDI channel assignment and the ADVANCED MIDI NOTE EDITOR. Or click MIDI LABB in the main toolbar.

New: per-instrument ADSR, filter cutoff, drive (DSP-connected), MIDI channel routing foundation, note matrix with note addition/deletion, velocity, duration, quantize and humanize. Resonance and width controls are stored but **not yet wired into DSP**. MIDI channel routing is an engine API; the live MIDI input path is not yet automatically routed through this API. The note matrix uses the existing shared NoteLane; clip assignment remains the existing Track City workflow.

Audio test: generated offline WAV by rendering all 22 instruments individually and a 4-instrument mix, checked finite output, nonzero RMS and master ceiling. The included WAV is the 4-instrument mix. No hardware speakers, ASIO interface or Maschine Studio device were tested.

This is a Python prototype, not a production DAW. The real hardware and UI require testing on Windows.
