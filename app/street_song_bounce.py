"""Sample-accurate offline song bounce for scheduled TOOLBOXX pad hits."""
import argparse
import json
import math
from pathlib import Path
from street_bounce import bounce
from pad_patterns import step_velocity


def validate_song(song):
    if not isinstance(song, dict): raise ValueError('Song must be an object')
    bpm = song.get('bpm', 85)
    bars = song.get('bars', 4)
    if isinstance(bpm, bool) or not isinstance(bpm, (int, float)) or not math.isfinite(bpm) or not 30 <= bpm <= 240:
        raise ValueError('BPM must be 30–240')
    if type(bars) is not int or not 1 <= bars <= 256: raise ValueError('Bars must be 1–256')
    samples = song.get('samples', {})
    if not isinstance(samples, dict): raise ValueError('Samples must be a pad-to-WAV object')
    for pad, path in samples.items():
        if not str(pad).isdigit() or not 1 <= int(pad) <= 32 or not isinstance(path, str) or not path:
            raise ValueError('Sample slots must be pads 1–32 and nonempty file paths')
    hits = song.get('hits', [])
    if not isinstance(hits, list) or len(hits) > 20000: raise ValueError('Invalid hit list')
    for hit in hits:
        if not isinstance(hit, dict): raise ValueError('Each hit must be an object')
        pad, beat = hit.get('pad'), hit.get('beat')
        if type(pad) is not int or not 1 <= pad <= 32: raise ValueError('Hit pad must be 1–32')
        if isinstance(beat, bool) or not isinstance(beat, (int, float)) or not math.isfinite(beat) or not 0 <= beat < bars*4:
            raise ValueError('Hit beat outside song')
        step_velocity(hit.get('velocity',1.))
    return bpm, bars



def expand_patterns(song):
    """Turn 16/32/64-step pad patterns into timeline hits (4 steps per beat).

    Pattern events use one-based pad numbers and zero-based step indices. A clip
    places a pattern at a zero-based bar with optional repetitions. Explicit
    song hits and expanded clip hits can coexist.
    """
    bpm, bars = validate_song(song)
    patterns = song.get('patterns', {})
    clips = song.get('clips', [])
    if not isinstance(patterns, dict) or not isinstance(clips, list):
        raise ValueError('Patterns must be an object and clips a list')
    if len(clips) > 1024: raise ValueError('Too many clips')
    result = [dict(hit) for hit in song.get('hits', [])]
    for clip in clips:
        if not isinstance(clip, dict): raise ValueError('Invalid clip')
        name, start, repeats = clip.get('pattern'), clip.get('bar'), clip.get('repeats', 1)
        if not isinstance(name, str) or name not in patterns: raise ValueError('Unknown pattern')
        if type(start) is not int or start < 0 or type(repeats) is not int or not 1 <= repeats <= 256:
            raise ValueError('Invalid clip position or repeats')
        pattern = patterns[name]
        if not isinstance(pattern, dict): raise ValueError('Invalid pattern')
        steps = pattern.get('steps', 16)
        if type(steps) is not int or steps not in (16, 32, 64): raise ValueError('Pattern steps must be 16, 32 or 64')
        events = pattern.get('events', [])
        if not isinstance(events, list) or len(events) > 2048: raise ValueError('Invalid pattern events')
        for repeat in range(repeats):
            for event in events:
                if not isinstance(event, dict): raise ValueError('Invalid pattern event')
                pad, step = event.get('pad'), event.get('step')
                if type(pad) is not int or not 1 <= pad <= 32 or type(step) is not int or not 0 <= step < steps:
                    raise ValueError('Pattern event pad or step outside range')
                beat = (start * 4) + (repeat * steps / 4) + (step / 4)
                if beat >= bars * 4: raise ValueError('Pattern clip extends beyond song')
                result.append({'pad': pad, 'beat': beat, 'velocity':step_velocity(event.get('velocity',1.))})
                if len(result) > 20000: raise ValueError('Too many scheduled hits')
    validate_song({**song, 'hits': result})
    return result

class ScheduledEngine:
    """Wrap existing Engine, splitting render blocks at exact event frames."""
    def __init__(self, engine, hits, bpm):
        self.engine = engine
        self.sr = engine.sr
        self.cursor = 0
        self.events = sorted((round(hit['beat'] * 60 / bpm * self.sr), hit['pad'] - 1, step_velocity(hit.get('velocity',1.))) for hit in hits)
        self.next_event = 0
    def render(self, frames):
        result = []
        target = self.cursor + frames
        while self.cursor < target:
            while self.next_event < len(self.events) and self.events[self.next_event][0] <= self.cursor:
                _, pad, velocity = self.events[self.next_event]
                if velocity==1.:self.engine.trigger(pad)
                elif velocity>0:self.engine.trigger(pad,velocity)
                self.next_event += 1
            boundary = min(target, self.events[self.next_event][0]) if self.next_event < len(self.events) else target
            count = boundary - self.cursor
            if count <= 0: raise RuntimeError('Invalid event schedule')
            result.extend(self.engine.render(count))
            self.cursor += count
        return result


def bounce_song(song, output, base_dir=None, engine=None):
    bpm, bars = validate_song(song)
    hits = expand_patterns(song)
    if engine is None:
        from toolboxx import Engine
        engine = Engine()
    base = Path(base_dir or '.').resolve()
    for pad, filename in song.get('samples', {}).items():
        path = Path(filename)
        if not path.is_absolute(): path = base / path
        if not path.is_file(): raise FileNotFoundError(f'Pad {pad} WAV not found: {path}')
        engine.load(int(pad)-1, str(path))
    for hit in hits:
        if str(hit['pad']) not in song.get('samples', {}):
            raise ValueError(f'Pad {hit["pad"]} has no loaded WAV')
    scheduled = ScheduledEngine(engine, hits, bpm)
    duration = bars * 4 * 60 / bpm
    if duration > 600: raise ValueError('Song bounce limited to 10 minutes')
    return bounce(scheduled, output, duration)


def main():
    parser = argparse.ArgumentParser(description='Render a TOOLBOXX beat grid to stereo WAV')
    parser.add_argument('song', help='Song JSON with bpm, bars, samples and hits')
    parser.add_argument('--output', default='TOOLBOXX_SONG.wav')
    args = parser.parse_args()
    source = Path(args.song).resolve()
    print(bounce_song(json.loads(source.read_text(encoding='utf-8')), args.output, source.parent))

if __name__ == '__main__': main()
