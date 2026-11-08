"""STREET TAP: explicit, user-controlled Windows output loopback recorder.

Requires `soundcard` and `numpy` at runtime; never records until Start is pressed.
Audio capture is limited to the selected output endpoint and may be unavailable
for protected streams. No DRM circumvention or network download support.
"""
from pathlib import Path
import json
import re
import threading
import time
import wave

APP_DIR = Path.home() / '.toolboxx'


def safe_filename(value):
    name = re.sub(r'[^a-zA-Z0-9 _.-]+', '_', str(value)).strip(' ._')
    return (name[:90] or 'Street Capture') + '.wav'


class StreetTap:
    def __init__(self, output_dir=None):
        self.output_dir = Path(output_dir or APP_DIR / 'recordings')
        self._thread = None
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self.status = 'Idle'
        self.last_file = None
        self.error = None
        self.frames = 0

    @staticmethod
    def devices():
        import soundcard as sc
        return [(speaker.id, speaker.name) for speaker in sc.all_speakers()]

    def start(self, device_id=None, name='Street Capture', rate=48000, max_seconds=600):
        if not 8000 <= int(rate) <= 192000 or not 1 <= max_seconds <= 3600:
            raise ValueError('Invalid recording configuration')
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                raise RuntimeError('Recording already active')
            self._stop.clear()
            self.error = None
            self.frames = 0
            self.status = 'Starting'
            self.last_file = None
            self._thread = threading.Thread(target=self._record, args=(device_id, name, int(rate), max_seconds), daemon=True)
            self._thread.start()

    def stop(self, timeout=8):
        self._stop.set()
        thread = self._thread
        if thread and thread.is_alive():
            thread.join(timeout)
        return self.last_file

    def _record(self, device_id, name, rate, max_seconds):
        try:
            import soundcard as sc
            import numpy as np
            speakers = sc.all_speakers()
            speaker = next((s for s in speakers if s.id == device_id), None) if device_id else sc.default_speaker()
            if speaker is None:
                raise RuntimeError('Selected Windows output device unavailable')
            loopback = sc.get_microphone(id=speaker.id, include_loopback=True)
            if loopback is None:
                raise RuntimeError('WASAPI loopback unavailable for selected output')
            self.output_dir.mkdir(parents=True, exist_ok=True)
            dest = self.output_dir / safe_filename(name)
            n = 1
            while dest.exists():
                dest = self.output_dir / (dest.stem.split(' (')[0] + f' ({n}).wav')
                n += 1
            with wave.open(str(dest), 'wb') as wav:
                wav.setnchannels(2)
                wav.setsampwidth(2)
                wav.setframerate(rate)
                self.status = 'Recording'
                with loopback.recorder(samplerate=rate, channels=2, blocksize=1024) as rec:
                    deadline = time.monotonic() + max_seconds
                    while not self._stop.is_set() and time.monotonic() < deadline:
                        block = rec.record(numframes=1024)
                        block = np.asarray(block, dtype=np.float32)
                        if block.ndim != 2 or block.shape[1] != 2:
                            raise RuntimeError('Unexpected loopback channel layout')
                        pcm = (np.clip(block, -1.0, 1.0) * 32767).astype('<i2')
                        wav.writeframes(pcm.tobytes())
                        self.frames += len(block)
            if self.frames == 0:
                dest.unlink(missing_ok=True)
                raise RuntimeError('No audio frames received')
            self.last_file = dest
            self.status = 'Saved'
        except Exception as exc:
            self.error = str(exc)
            self.status = 'Error'


class CrateIndex:
    """Local bookmarks and download directories; no automated site scraping."""
    def __init__(self, path=None):
        self.path = Path(path or APP_DIR / 'crate_index.json')
        self.sites = []
        self.folders = []
        self.load()

    def load(self):
        if self.path.exists():
            data = json.loads(self.path.read_text(encoding='utf-8'))
            self.sites = [x for x in data.get('sites', []) if isinstance(x, dict)]
            self.folders = [x for x in data.get('folders', []) if isinstance(x, str)]

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix('.tmp')
        temp.write_text(json.dumps({'sites': self.sites, 'folders': self.folders}, indent=2), encoding='utf-8')
        temp.replace(self.path)

    def add_site(self, name, url):
        from urllib.parse import urlparse
        parsed = urlparse(url.strip())
        if parsed.scheme not in ('https', 'http') or not parsed.netloc:
            raise ValueError('Enter a valid http(s) URL')
        self.sites.append({'name': name.strip()[:70] or parsed.netloc, 'url': url.strip()})
        self.save()

    def add_folder(self, folder):
        folder = str(Path(folder).expanduser().resolve())
        if not Path(folder).is_dir():
            raise ValueError('Folder does not exist')
        if folder not in self.folders:
            self.folders.append(folder)
            self.save()

    def samples(self):
        allowed = {'.wav', '.aif', '.aiff', '.flac', '.mp3', '.ogg'}
        found = []
        for folder in self.folders:
            p = Path(folder)
            if p.is_dir():
                try:
                    found.extend(x for x in p.iterdir() if x.is_file() and x.suffix.lower() in allowed)
                except OSError:
                    pass
        return sorted(found, key=lambda p: p.name.lower())
