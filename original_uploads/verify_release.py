"""Checks distributable layout without claiming Windows runtime verification."""
from pathlib import Path
import hashlib, sys
root=Path(__file__).resolve().parent
exe=root/'build'/'BOOM_BAP_TOOLBOXX'/'BOOM_BAP_TOOLBOXX.exe'
setup=root/'dist'/'BOOM_BAP_TOOLBOXX_Setup_050.exe'
for path in (exe,setup):
    if not path.is_file() or path.stat().st_size < 1024:
        raise SystemExit(f'FAIL: missing or suspiciously small {path}')
    print(f'OK {path.name}: {path.stat().st_size:,} bytes')
print('SHA256',hashlib.sha256(setup.read_bytes()).hexdigest())
print('NOTE: this verifies files only; Windows installation, MIDI and audio must be tested separately.')
