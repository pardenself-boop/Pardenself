"""Persistent, validated user patch vault. No external dependencies."""
import json
import os
from pathlib import Path
import re
import tempfile

PARAMETERS = ('attack','decay','sustain','release','cutoff','resonance','drive','width')

class StreetPatchVault:
    def __init__(self, directory=None):
        self.directory = Path(directory) if directory is not None else Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'BOOM_BAP_TOOLBOXX' / 'Patches'

    def _path(self, labb_index, name):
        if not isinstance(labb_index, int) or not 0 <= labb_index < 22:
            raise ValueError('Invalid LABB')
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 64:
            raise ValueError('Patch name must be 1–64 characters')
        safe = re.sub(r'[^a-zA-Z0-9 _-]', '_', name.strip()).strip(' ._')
        if not safe:
            raise ValueError('Invalid patch name')
        return self.directory / f'labb_{labb_index:02d}' / f'{safe}.tbxi.json'

    def save(self, engine, labb_index, name):
        path = self._path(labb_index, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {'format': 'toolboxx-street-patch', 'version': 1, 'name': name.strip(),
                   'labb_index': labb_index, 'parameters': dict(engine.parameters[labb_index])}
        fd, temp = tempfile.mkstemp(prefix='.patch-', suffix='.tmp', dir=str(path.parent))
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as handle:
                json.dump(payload, handle, indent=2, allow_nan=False)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp, path)
        finally:
            if os.path.exists(temp):
                os.unlink(temp)
        return path

    def load(self, engine, labb_index, name):
        path = self._path(labb_index, name)
        data = json.loads(path.read_text(encoding='utf-8'))
        if data.get('format') != 'toolboxx-street-patch' or data.get('version') != 1 or data.get('labb_index') != labb_index:
            raise ValueError('Incompatible patch file')
        params = data.get('parameters')
        if not isinstance(params, dict) or set(params) != set(PARAMETERS):
            raise ValueError('Patch parameters incomplete')
        # Validate everything before changing any active parameter.
        import math
        limits = {'attack':(.001,2.), 'decay':(.005,3.), 'sustain':(0.,1.), 'release':(.005,4.),
                  'cutoff':(.015,.98), 'resonance':(0.,1.), 'drive':(0.,1.), 'width':(0.,1.)}
        for key, value in params.items():
            if isinstance(value, bool) or not isinstance(value, (int,float)) or not math.isfinite(value) or not limits[key][0] <= value <= limits[key][1]:
                raise ValueError(f'Invalid patch parameter: {key}')
        for key, value in params.items():
            engine.set_parameter(labb_index, key, value)
        return path

    def names(self, labb_index):
        folder = self._path(labb_index, 'placeholder').parent
        return sorted(p.name.removesuffix('.tbxi.json') for p in folder.glob('*.tbxi.json')) if folder.exists() else []
