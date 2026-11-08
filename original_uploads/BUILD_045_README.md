# BOOM BAP TOOLBOXX Build 045 — Main Workstation Pad Repair

## Code changes
- Main workstation MIDI Learn command list now exposes PAD 1 through PAD 32.
- Main workstation absolute pad trigger selects correct bank (A/B) and triggers the requested slot without wrapping.
- Visible 16-pad controls still follow their selected bank.
- Incoming unmapped MIDI notes 36–67 now trigger absolute pad slots 1–32 in main workstation when a LABB clip is not selected.
- Invalid absolute pad indices are rejected.
- Five regression tests added at tests/test_main_pad_mapping_045.py.

## Validation
47 Python unittest tests passed in this environment. Live Windows MIDI and sound output have not been verified. No compiled Windows installer is included.
