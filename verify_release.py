"""Validate output files; installation and hardware require separate testing."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent


def verify(root=ROOT):
    release = json.loads((root / 'release.json').read_text(encoding='utf-8'))
    exe = root / 'build' / release['executable'] / (release['executable'] + '.exe')
    setup = root / 'dist' / release['installer']
    for path in (exe, setup):
        if not path.is_file() or path.stat().st_size < 1024:
            raise ValueError(f'Missing or suspiciously small: {path}')
        with path.open('rb') as stream:
            if stream.read(2) != b'MZ':
                raise ValueError(f'Missing Windows executable signature: {path}')
        print(f'OK {path.name}: {path.stat().st_size:,} bytes')
    digest = hashlib.sha256(setup.read_bytes()).hexdigest()
    print('SHA256', digest)
    print('File checks only; installation, live audio and MIDI remain unverified.')
    return digest


if __name__ == '__main__':
    verify()
