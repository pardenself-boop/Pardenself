"""Portable 32-pad WAV kit manifests. No audio data is copied or modified."""
import json
from pathlib import Path

KIT_FORMAT = "toolboxx.pad-kit.v1"

def save_kit(destination, pad_paths):
    """Save 32 slots, using relative paths where possible."""
    if len(pad_paths) != 32:
        raise ValueError("A kit must have exactly 32 pad slots")
    dest = Path(destination).expanduser().resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)
    slots = []
    import os
    for path in pad_paths:
        if not path:
            slots.append(None)
        else:
            p = Path(path).expanduser().resolve()
            slots.append(os.path.relpath(str(p), str(dest.parent)))
    payload = {"format": KIT_FORMAT, "pads": slots}
    temp = dest.with_suffix(dest.suffix + ".tmp")
    try:
        temp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        temp.replace(dest)
    finally:
        if temp.exists(): temp.unlink()
    return dest

def load_kit(source):
    """Return 32 resolved paths or None; reject malformed manifests."""
    src = Path(source).expanduser().resolve()
    payload = json.loads(src.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("format") != KIT_FORMAT:
        raise ValueError("Not a TOOLBOXX pad kit")
    slots = payload.get("pads")
    if not isinstance(slots, list) or len(slots) != 32:
        raise ValueError("Pad kit must contain exactly 32 slots")
    result = []
    for slot in slots:
        if slot is None:
            result.append(None)
        elif isinstance(slot, str) and slot.strip() and slot.lower().endswith(".wav"):
            result.append(str((src.parent / slot).resolve()))
        else:
            raise ValueError("Invalid WAV path in pad kit")
    return result
