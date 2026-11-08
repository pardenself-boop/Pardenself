"""Non-destructive audio regions for Track City. Beat-based clip positions; WAV sources remain untouched."""
import wave
from array import array
from pathlib import Path


def read_wav(path):
    with wave.open(str(path), 'rb') as w:
        channels, width, rate = w.getnchannels(), w.getsampwidth(), w.getframerate()
        if width != 2 or channels not in (1, 2):
            raise ValueError('Track City currently supports mono/stereo 16-bit PCM WAV.')
        raw = w.readframes(w.getnframes())
    values = array('h'); values.frombytes(raw)
    if channels == 1:
        return [v / 32768.0 for v in values], rate
    return [(values[i] + values[i+1]) / 65536.0 for i in range(0, len(values), 2)], rate


def region_sample(data, source_rate, output_rate, clip, elapsed_frames, bpm):
    """Read one audio region sample at a local output frame, respecting slip, trim, fades and gain."""
    beats_per_frame = bpm / (60.0 * output_rate)
    local_beat = elapsed_frames * beats_per_frame
    duration = max(0.0, float(clip['length']))
    if local_beat < 0 or local_beat >= duration: return 0.0
    source_beat = float(clip.get('offset', 0.0)) + local_beat
    source_frame = source_beat * 60.0 / bpm * source_rate
    if source_frame < 0 or source_frame >= len(data): return 0.0
    k = int(source_frame); t = source_frame - k
    value = data[k] * (1-t) + (data[k+1] if k+1 < len(data) else 0.0) * t
    fade_in = max(0.0, float(clip.get('fade_in', 0.0)))
    fade_out = max(0.0, float(clip.get('fade_out', 0.0)))
    envelope = 1.0
    if fade_in: envelope = min(envelope, local_beat / fade_in)
    if fade_out: envelope = min(envelope, (duration - local_beat) / fade_out)
    return value * max(0.0, envelope) * float(clip.get('gain', 1.0))


class AudioRegions:
    def __init__(self, output_rate=48000):
        self.output_rate = output_rate
        self.sources = {}  # absolute path -> (mono float samples, source rate)
        self.voices = []

    def preload(self, path):
        path = str(Path(path).resolve())
        if path not in self.sources: self.sources[path] = read_wav(path)
        return path

    def start(self, clip, bpm, seek_beats=0.0):
        path = str(Path(clip['path']).resolve())
        if path not in self.sources: self.preload(path)
        self.voices.append({'clip': dict(clip), 'bpm': float(bpm),
                            'frame': int(seek_beats * 60.0 / bpm * self.output_rate), 'path': path})

    def render(self, frames):
        out = [0.0] * frames; remaining = []
        for voice in self.voices:
            data, rate = self.sources[voice['path']]
            for i in range(frames):
                sample = region_sample(data, rate, self.output_rate, voice['clip'], voice['frame'] + i, voice['bpm'])
                out[i] += sample
            voice['frame'] += frames
            if voice['frame'] * voice['bpm'] / (60.0*self.output_rate) < voice['clip']['length']:
                remaining.append(voice)
        self.voices = remaining
        return out

    def stop(self): self.voices.clear()


def regions_starting(clips, beat, step_beats=0.25):
    return [c for c in clips if c.get('kind') == 'audio' and c['start'] <= beat < c['start']+step_beats and beat < c['start']+c['length']]
