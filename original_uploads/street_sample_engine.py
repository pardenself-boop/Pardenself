"""STREET CRATE: dependency-free WAV sample instrument for TOOLBOXX.

Supports PCM 8/16/24/32-bit WAV, mono/stereo downmix, MIDI pitch,
velocity, note-off release, and bounded polyphony. Not a time-stretcher.
"""
import math
import threading
import wave
from pathlib import Path


def load_wav(path, max_seconds=120):
    path = Path(path)
    with wave.open(str(path), 'rb') as wf:
        channels, width, rate, frames = wf.getnchannels(), wf.getsampwidth(), wf.getframerate(), wf.getnframes()
        if channels not in (1, 2) or width not in (1, 2, 3, 4) or not 8000 <= rate <= 192000:
            raise ValueError('Unsupported WAV encoding')
        if frames > rate * max_seconds:
            raise ValueError('Sample exceeds duration limit')
        data = wf.readframes(frames)
    scale = float(1 << (8 * width - 1))
    values = []
    for i in range(frames):
        summed = 0.0
        for ch in range(channels):
            offset = (i * channels + ch) * width
            raw = data[offset:offset + width]
            value = (raw[0] - 128) / 128.0 if width == 1 else int.from_bytes(raw, 'little', signed=True) / scale
            summed += value
        values.append(summed / channels)
    return rate, tuple(values)


class StreetCrate:
    """Per-LABB sample slots and polyphonic voice playback; mono floating-point output."""
    def __init__(self, sample_rate=48000, max_voices=32):
        self.sample_rate = sample_rate
        self.max_voices = max_voices
        self.slots = {}
        self.voices = []
        self.lock = threading.RLock()

    def load(self, labb, path, root_note=60):
        if not 0 <= labb < 22 or not 0 <= root_note <= 127:
            raise ValueError('Invalid LABB or root note')
        rate, samples = load_wav(path)
        if not samples:
            raise ValueError('Empty sample')
        with self.lock:
            self.slots[labb] = (rate, samples, root_note, str(path))

    def note_on(self, labb, note, velocity=1.0):
        if not 0 <= note <= 127 or not 0 <= velocity <= 1 or not math.isfinite(velocity):
            raise ValueError('Invalid MIDI note or velocity')
        with self.lock:
            if labb not in self.slots:
                return False
            rate, samples, root, _ = self.slots[labb]
            step = (rate / self.sample_rate) * 2 ** ((note - root) / 12)
            if len(self.voices) >= self.max_voices:
                self.voices.pop(0)
            self.voices.append({'labb':labb,'note':note,'data':samples,'pos':0.0,'step':step,'gain':velocity,'release':None})
            return True

    def note_off(self, note, labb=None):
        with self.lock:
            for v in self.voices:
                if v['note'] == note and (labb is None or v['labb'] == labb) and v['release'] is None:
                    v['release'] = 0

    def all_notes_off(self, labb=None):
        with self.lock:
            for v in self.voices:
                if labb is None or v['labb'] == labb:
                    v['release'] = 0

    def render(self, frames, volume=None, mute=None, solo=None):
        if frames < 0:
            raise ValueError('Negative frame count')
        output = [0.0] * frames
        with self.lock:
            kept = []
            solo_active = any(solo) if solo is not None else False
            for v in self.voices:
                labb = v['labb']
                if (mute and mute[labb]) or (solo_active and not solo[labb]):
                    kept.append(v)
                    continue
                data = v['data']
                pos = v['pos']
                release = v['release']
                level = (volume[labb] if volume is not None else 1.0) * v['gain']
                for i in range(frames):
                    j = int(pos)
                    if j >= len(data):
                        break
                    fraction = pos - j
                    sample = data[j] * (1 - fraction) + data[min(j + 1, len(data) - 1)] * fraction
                    if release is not None:
                        sample *= max(0.0, 1 - release / (self.sample_rate * .03))
                        release += 1
                    output[i] += sample * level
                    pos += v['step']
                    if release is not None and release >= self.sample_rate * .03:
                        break
                v['pos'], v['release'] = pos, release
                if pos < len(data) and (release is None or release < self.sample_rate * .03):
                    kept.append(v)
            self.voices = kept
        return output
