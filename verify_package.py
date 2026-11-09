"""Offline source preflight. Does not verify Windows or audio hardware."""
from pathlib import Path
import ast
import json
import sys

ROOT = Path(__file__).resolve().parent


def verify(root=ROOT):
    app = root / 'app'
    release = json.loads((root / 'release.json').read_text(encoding='utf-8'))
    if release['installer'] != f"BOOM_BAP_TOOLBOXX_Setup_{release['build']}.exe":
        raise ValueError('Installer name disagrees with release build')
    required = ['toolboxx_launcher.py', 'startup_check.py', 'launch_reference.py',
                'toolboxx.py', 'cookup_ui.py', 'labb_engine.py',
                'midi_automation_engine.py', 'app_version.py', 'app_updates.py',
                'update_window.py', 'audio_midi_window.py', 'midi_activity.py',
                'pad_patterns.py', 'AUDIO_TEST.wav']
    for name in required:
        path = app / name
        if not path.is_file() or not path.stat().st_size:
            raise ValueError(f'Missing/empty: app/{name}')
    paths = list(app.glob('*.py'))
    for path in paths:
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    sys.path.insert(0, str(app))
    import labb_engine, arranger_core, midi_automation_engine
    print(f'PASS: {len(paths)} modules parsed; engines imported; runtime assets present; Build {release["build"]}')
    return release


if __name__ == '__main__':
    verify()
