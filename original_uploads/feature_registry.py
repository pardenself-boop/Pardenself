"""Single source of truth for TOOLBOXX feature availability and display settings.
Feature visibility NEVER changes DSP, MIDI mappings, project data or transport.
"""
import json
from pathlib import Path

FEATURES = {
 "WORKSPACE": ["Instrument browser", "Instrument header", "Performance macros", "Waveform / sample view", "32-pad step matrix", "Track City arranger", "Device chain", "Right-side FX and meters", "Brand header / Rage banner"],
 "ARRANGE & EDIT": ["Tempo and signature tracks", "Tempo curves / beat-linear and time-linear", "Insert time / delete time", "Track visibility / groups / scenes", "Clip launch / song scenes", "Video track and frame sync"],
 "INSTRUMENTS & FX": ["Advanced instrument editor", "LABB engine / patch memory / note release", "Keyboard instrument / arpeggiator", "STREET CURVE EQ / STEREO SCOPE", "BLOCK METERS / TRUE PEAK", "IRON CHAIN FX / BYPASS"],
 "MIDI & AUTOMATION": ["MIDI COMMAND CENTER", "STREET LINK / KNOB JACK", "CITYWIDE / LOCK-ON / HYBRID", "CREW LINK / IRON HANDSHAKE", "MIDI WIRETAP", "MOTION TRACKS / PART MOTION"],
 "DELIVERY & HELP": ["FINAL PRESS / DIGITAL RELEASE", "PUBLISHING CONNECTIONS", "TOOLBOXX Advanced Manual"],
}
AVAILABLE = frozenset(FEATURES["WORKSPACE"] + ["Advanced instrument editor"])

def normalize_visibility(raw):
 """Missing/invalid entries default to visible; no settings control the audio engine."""
 if not isinstance(raw, dict):
  return {k: True for k in FEATURES["WORKSPACE"]}
 return {k: raw.get(k) if isinstance(raw.get(k), bool) else True for k in FEATURES["WORKSPACE"]}

def read_visibility(path):
 try:
  return normalize_visibility(json.loads(Path(path).read_text(encoding="utf-8")))
 except (OSError, ValueError, TypeError):
  return normalize_visibility(None)

def write_visibility(path, values):
 target=Path(path); target.parent.mkdir(parents=True, exist_ok=True)
 temp=target.with_suffix(target.suffix+".tmp")
 temp.write_text(json.dumps(normalize_visibility(values), indent=2), encoding="utf-8")
 temp.replace(target)
