# BOOM BAP TOOLBOXX v1.4 — LABB MIDI Arrangement

**New:** + LABB MIDI creates a four-beat repeating instrument clip at the playhead on the focused track. It stores a LABB instrument index and a note-pattern reference. The shared Track City scheduler triggers LABB notes at sixteenth-note boundaries. Clips can be moved, trimmed, split and slipped using the existing arranger and hardware edit commands. Track mute/solo is honored. LABB note clips and note patterns persist in project JSON.

**Hardware/MIDI command additions:** LABB ARM, LABB NOTE +, LABB NOTE -, LABB NOTE PLAY, LABB CLIP. They are available for MIDI Learn and virtual hardware mapping. When a LABB clip is selected, unmapped incoming MIDI notes audition the armed LABB; when Record is on, they append quantized notes to the selected clip’s four-beat pattern. Otherwise, the existing pad mapping is retained. This is a foundation for a dedicated note editor, not yet one.

**Limitations:** New LABB clips get independent copies of the starter note pattern, scheduling uses Tkinter's GUI timer, and recorded notes have fixed half-beat duration. Real Maschine Studio USB screens/buttons and native ASIO/VST integration remain untested/unimplemented. All 22 LABBS still use simple synthesis patches, not finished advanced instruments. Use START_WINDOWS.bat after extracting, with Python 3.11+ and requirements installed.
