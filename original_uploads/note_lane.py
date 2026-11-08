"""Track City LABB MIDI-note containers. Beat-based, UI/hardware neutral."""
from dataclasses import dataclass, asdict

@dataclass
class Note:
    beat: float
    pitch: int
    velocity: float = .8
    duration: float = .5

class NoteLane:
    def __init__(self):
        self.patterns = {'labb-main': [Note(0,48), Note(1,51), Note(2,55), Note(3,58)]}
        self.armed_labb = 3
        self.quantize = .25

    def add(self, pattern, beat, pitch, velocity=.8, duration=.5):
        if not 0 <= pitch <= 127 or not 0 <= velocity <= 1 or duration <= 0:
            raise ValueError('Invalid MIDI note')
        beat = max(0., round(beat / self.quantize) * self.quantize) if self.quantize else max(0.,beat)
        note = Note(beat, pitch, velocity, duration)
        self.patterns.setdefault(pattern, []).append(note)
        return note

    def events_at(self, clips, beat, audible=lambda track: True):
        result=[]
        for clip in clips:
            if clip.get('kind') != 'labb' or not audible(clip['track']):
                continue
            start=float(clip['start']); length=float(clip['length'])
            if not start <= beat < start+length:continue
            source=beat-start+float(clip.get('offset',0))
            pattern=self.patterns.get(clip.get('note_pattern','labb-main'),[])
            # Four-beat repeating pattern, including split/slip source offsets.
            phase=source%4
            for n in pattern:
                if abs((n.beat%4)-phase)<1e-6:
                    result.append((int(clip.get('labb_index',self.armed_labb)),n.pitch,n.velocity,n.duration))
        return result

    def serialize(self):
        return {'patterns':{k:[asdict(n) for n in notes] for k,notes in self.patterns.items()},'armed_labb':self.armed_labb,'quantize':self.quantize}

    def deserialize(self,data):
        self.armed_labb=max(0,min(21,int(data.get('armed_labb',3))))
        self.quantize=float(data.get('quantize',.25))
        patterns=data.get('patterns')
        if isinstance(patterns,dict):
            self.patterns={str(k):[Note(**n) for n in values] for k,values in patterns.items()}
