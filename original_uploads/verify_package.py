"""Offline package preflight; does not claim Windows or audio hardware validation."""
from pathlib import Path
import ast
import sys
root = Path(__file__).resolve().parent
app = root / 'app'
required = ['toolboxx_launcher.py','launch_reference.py','toolboxx.py','cookup_ui.py','labb_engine.py','midi_automation_engine.py','COOK_UP_REFERENCE.png','AUDIO_TEST.wav']
for name in required:
    path = app / name
    assert path.is_file() and path.stat().st_size > 0, f'Missing/empty: {name}'
for path in app.glob('*.py'):
    ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
sys.path.insert(0, str(app))
import labb_engine, arranger_core, midi_automation_engine
print(f'PASS: {len(list(app.glob("*.py")))} Python modules parsed; engine modules imported; required assets present')
