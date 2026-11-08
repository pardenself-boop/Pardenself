"""One release identity for source and the bundled Windows application."""
import json
from pathlib import Path
import sys

_root = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else Path(__file__).resolve().parents[1]
RELEASE = json.loads((_root / 'release.json').read_text(encoding='utf-8'))
BUILD = RELEASE['build']
VERSION = RELEASE['version']
