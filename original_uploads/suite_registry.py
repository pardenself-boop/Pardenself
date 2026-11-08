"""Shared 22-suite registry. Availability is explicit: no fake DSP claims."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Suite:
    name: str
    family: str
    implementation: str
    purpose: str

SUITES = (
    Suite('Track City','Arrange','working','Audio and pattern clip editing'),
    Suite('Chop Labb Pro','Sample','foundation','Sample slice and waveform navigation'),
    Suite('Smart Levels Pro','Instrument','planned','Multi-articulation playable instruments'),
    Suite('808 Labb Pro','Instrument','planned','Warm boom-bap bass synthesizer'),
    Suite('Rage','Performance','planned','Performance macros and MAX RAGE'),
    Suite('Drums & Breaks','Instrument','working','32-pad WAV sampler and step patterns'),
    Suite('Synth Labb','Instrument','planned','Synthesizer'),
    Suite('ARP & Chord','Instrument','planned','Chord and arpeggio tools'),
    Suite('Key 88 Pro','Instrument','planned','Keyboard instruments'),
    Suite('Stems','Sample','planned','Stem separation and stem instruments'),
    Suite('Warp & Auto-Fit','Sample','planned','Time stretch and pitch'),
    Suite('Dice Labb','Generator','planned','Musical randomization'),
    Suite('Vocals & Resample','Sample','planned','Resampling and vocal tools'),
    Suite('Sample Labb','Sample','foundation','WAV import and audition'),
    Suite('FX Brooklyn Iron','FX','planned','Tape and transformer effects'),
    Suite('Master Mixer','Mix','foundation','Audio output and basic mixing'),
    Suite('MIDI Command Center','Control','foundation','MIDI Learn and virtual Studio'),
    Suite('Quantize & Groove','Arrange','planned','Groove and quantize'),
    Suite('Brainz','Assistant','planned','Contextual command assistant'),
    Suite('Roulette & Store','Library','planned','Preset discovery and packs'),
    Suite('Prefs','System','foundation','Audio and project settings'),
    Suite('Manual & License','System','planned','Interactive help and licensing'),
)
assert len(SUITES)==22

class SuiteRouter:
    def __init__(self):self.focus=0;self.favorite=[]
    @property
    def current(self):return SUITES[self.focus]
    def navigate(self,steps):self.focus=(self.focus+steps)%len(SUITES);return self.current
    def select(self,index):
        if not 0<=index<len(SUITES):raise IndexError(index)
        self.focus=index;return self.current
    def serialize(self):return {'focus':self.focus,'favorite':list(self.favorite)}
    def deserialize(self,data):
        self.focus=int(data.get('focus',0))%len(SUITES)
        self.favorite=[i for i in data.get('favorite',[]) if isinstance(i,int) and 0<=i<len(SUITES)]
