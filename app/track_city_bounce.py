"""Bridge actual Track City pattern clips to sample-accurate offline WAV bounce."""
import math
from street_bounce import bounce
from street_song_bounce import ScheduledEngine
from audio_regions import AudioRegions


def collect_hits(arranger, patterns, bpm, end_beat):
    """Respect clip trims, slip offsets, mute/solo and 16-step pattern looping."""
    if not isinstance(bpm, (int, float)) or not math.isfinite(bpm) or not 30 <= bpm <= 240:
        raise ValueError('BPM must be 30–240')
    if not isinstance(end_beat, (int, float)) or not math.isfinite(end_beat) or not 0 < end_beat <= 1000:
        raise ValueError('Invalid export length')
    hits=[]
    for clip in arranger.clips:
        if clip.get('kind', 'pattern') != 'pattern' or not arranger.track_audible(clip['track']):
            continue
        pattern=patterns.get(str(clip.get('pattern_id','main')))
        if not pattern: continue
        start=float(clip['start']); length=float(clip['length']); offset=float(clip.get('offset',0))
        if not all(map(math.isfinite,(start,length,offset))) or length<=0: raise ValueError('Invalid clip timing')
        for pad,row in enumerate(pattern[:32]):
            for step,on in enumerate(row[:16]):
                if not on: continue
                phase=step/4
                first=math.ceil((offset-phase-1e-9)/4)
                last=math.floor((offset+length-phase-1e-9)/4)
                for k in range(first,last+1):
                    beat=start+phase+4*k-offset
                    if max(0,start)-1e-8 <= beat < min(end_beat,start+length)-1e-8:
                        hits.append({'pad':pad+1,'beat':max(0,beat)})
                        if len(hits)>20000: raise ValueError('Too many pad hits')
    return sorted(hits,key=lambda h:(h['beat'],h['pad']))


class TrackCityRender(ScheduledEngine):
    """Sample-accurate pad hits plus audio-region starts on the same timeline."""
    def __init__(self, engine, hits, bpm, audio_clips, midi_notes=()):
        super().__init__(engine, hits, bpm)
        self.regions = engine.regions
        self.audio_events = sorted(((round(c['start'] * 60 / bpm * self.sr), c) for c in audio_clips), key=lambda event: event[0])
        self.next_audio = 0
        self.bpm = bpm
        self.midi_events = sorted(((round(n['beat'] * 60 / bpm * self.sr), n) for n in midi_notes), key=lambda event: event[0])
        self.next_midi = 0

    def render(self, frames):
        output = []
        target = self.cursor + frames
        while self.cursor < target:
            while self.next_audio < len(self.audio_events) and self.audio_events[self.next_audio][0] <= self.cursor:
                _, clip = self.audio_events[self.next_audio]
                seek_frames = max(0, self.cursor - round(clip['start'] * 60 / self.bpm * self.sr))
                self.regions.start(clip, self.bpm, seek_beats=seek_frames * self.bpm / (60 * self.sr))
                self.next_audio += 1
            while self.next_midi < len(self.midi_events) and self.midi_events[self.next_midi][0] <= self.cursor:
                _, note = self.midi_events[self.next_midi]
                self.engine.labbs.note_on(note['pitch'], note['velocity'], note['labb'], note['duration'] * 60 / self.bpm)
                self.next_midi += 1
            next_audio_frame = self.audio_events[self.next_audio][0] if self.next_audio < len(self.audio_events) else target
            next_midi_frame = self.midi_events[self.next_midi][0] if self.next_midi < len(self.midi_events) else target
            end = min(target, next_audio_frame, next_midi_frame)
            output.extend(super().render(end - self.cursor))
        return output


def collect_audio_clips(arranger, end_beat):
    """Select audible WAV regions, keeping original files non-destructive."""
    clips = []
    for clip in arranger.clips:
        if clip.get('kind') != 'audio' or not arranger.track_audible(clip['track']):
            continue
        start, length = float(clip['start']), float(clip['length'])
        if not math.isfinite(start) or not math.isfinite(length) or start < 0 or length <= 0:
            raise ValueError('Invalid audio clip timing')
        if start >= end_beat:
            continue
        if not clip.get('path'):
            raise ValueError('Audio clip has no WAV path')
        clips.append(dict(clip, length=min(length, end_beat-start)))
    return clips


def collect_midi_notes(arranger, note_lane, end_beat):
    """Expand four-beat LABB note patterns into sample-accurate song events."""
    notes = []
    for clip in arranger.clips:
        if clip.get('kind') != 'labb' or not arranger.track_audible(clip['track']):
            continue
        start, length, offset = float(clip['start']), float(clip['length']), float(clip.get('offset', 0))
        labb = int(clip.get('labb_index', note_lane.armed_labb))
        if not all(math.isfinite(v) for v in (start, length, offset)) or start < 0 or length <= 0 or not 0 <= labb < 22:
            raise ValueError('Invalid LABB clip timing or instrument')
        pattern = note_lane.patterns.get(clip.get('note_pattern', 'labb-main'), [])
        for note in pattern:
            beat, pitch, velocity, duration = float(note.beat), int(note.pitch), float(note.velocity), float(note.duration)
            if not all(math.isfinite(v) for v in (beat, velocity, duration)) or not 0 <= pitch <= 127 or not 0 <= velocity <= 1 or duration <= 0:
                raise ValueError('Invalid LABB note')
            phase = beat % 4
            first = math.ceil((offset - phase - 1e-9) / 4)
            last = math.floor((offset + length - phase - 1e-9) / 4)
            for repeat in range(first, last + 1):
                at = start + phase + 4 * repeat - offset
                if max(0, start) - 1e-8 <= at < min(end_beat, start + length) - 1e-8:
                    notes.append({'beat': max(0, at), 'pitch': pitch, 'velocity': velocity,
                                  'duration': min(duration, start + length - at, end_beat - at), 'labb': labb})
                    if len(notes) > 20000: raise ValueError('Too many LABB notes')
    return sorted(notes, key=lambda n: (n['beat'], n['labb'], n['pitch']))


def bounce_track_city(engine, arranger, patterns, bpm, output, bars=None, note_lane=None):
    if isinstance(bpm, bool) or not isinstance(bpm, (int, float)) or not math.isfinite(bpm) or not 30 <= bpm <= 240:
        raise ValueError('BPM must be 30–240')
    if bars is None:
        bars=max(1,math.ceil(max((float(c['start'])+float(c['length']) for c in arranger.clips),default=4)/4))
    if type(bars) is not int or not 1<=bars<=256:raise ValueError('Invalid bar count')
    duration=bars*4*60/bpm
    if duration>600:raise ValueError('Bounce limited to ten minutes')
    hits=collect_hits(arranger,patterns,bpm,bars*4)
    missing=sorted({h['pad'] for h in hits if engine.samples[h['pad']-1] is None})
    if missing:raise ValueError('Load WAV samples for pads: '+', '.join(map(str,missing)))
    # A new engine avoids changing currently playing voices in the live workstation.
    from toolboxx import Engine
    offline=Engine()
    offline.samples=list(engine.samples)
    offline.sample_paths=list(engine.sample_paths)
    offline.labbs.deserialize(engine.labbs.serialize())
    offline.labbs.crate.slots=dict(engine.labbs.crate.slots)
    from mix_rack import MixRack
    offline.mix_rack=MixRack.from_json(engine.mix_rack.to_json())
    audio_clips = collect_audio_clips(arranger, bars * 4)
    # Preload and validate every audio source before writing the output file.
    for clip in audio_clips:
        offline.regions.preload(clip['path'])
    midi_notes = collect_midi_notes(arranger, note_lane, bars * 4) if note_lane is not None else []
    return bounce(TrackCityRender(offline, hits, bpm, audio_clips, midi_notes), output, duration)
