"""Non-destructive TOOLBOXX modular mix-rack state, independent of the UI.

BLOCK EQ, BROWNSTONE COMP, DUST DRIVE and IRON CEILING have live DSP; other slots remain planned.
"""
from dataclasses import dataclass, field
from typing import Dict, List
import json

MODULES = {
    'eq': {'low_gain_db': (-18., 18., 0.), 'mid_gain_db': (-18., 18., 0.), 'high_gain_db': (-18., 18., 0.)},
    'compressor': {'threshold_db': (-60., 0., -18.), 'ratio': (1., 20., 3.), 'attack_ms': (0.1, 200., 20.), 'release_ms': (5., 2000., 120.)},
    'density': {'amount': (0., 1., 0.25), 'mix': (0., 1., 0.5)},
    'transient': {'attack': (-1., 1., 0.), 'sustain': (-1., 1., 0.)},
    'phase': {'polarity': (0., 1., 0.), 'delay_ms': (-20., 20., 0.)},
    'clipper': {'ceiling_db': (-12., 0., -1.), 'drive_db': (0., 24., 0.), 'mix': (0., 1., 1.)},
}

@dataclass
class Module:
    kind: str
    enabled: bool = True
    visible: bool = True
    params: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        if self.kind not in MODULES:
            raise ValueError('Unknown processor: ' + self.kind)
        defaults = {k: v[2] for k, v in MODULES[self.kind].items()}
        defaults.update(self.params)
        for name, value in defaults.items():
            if name not in MODULES[self.kind]:
                raise ValueError('Unknown parameter: ' + name)
            low, high, _ = MODULES[self.kind][name]
            if not low <= float(value) <= high:
                raise ValueError('Parameter out of range: ' + name)
        self.params = defaults

class MixRack:
    def __init__(self, modules=None):
        self.modules: List[Module] = list(modules or [])
        from street_fx import StreetFX
        self.processor=StreetFX()

    def process(self,samples,sample_rate=48000):
        return self.processor.process(samples,self.modules,sample_rate)

    def add(self, kind):
        module = Module(kind)
        self.modules.append(module)
        return module

    def move(self, old_index, new_index):
        if not (0 <= old_index < len(self.modules) and 0 <= new_index < len(self.modules)):
            raise IndexError('Rack index out of bounds')
        self.modules.insert(new_index, self.modules.pop(old_index))

    def bypass(self, index, bypass=True):
        self.modules[index].enabled = not bypass

    def hide(self, index, hidden=True):
        # Visibility never changes processing state.
        self.modules[index].visible = not hidden

    def set_parameter(self, index, name, value):
        module = self.modules[index]
        if name not in MODULES[module.kind]:
            raise KeyError(name)
        low, high, _ = MODULES[module.kind][name]
        if not low <= float(value) <= high:
            raise ValueError('Parameter out of range')
        module.params[name] = float(value)

    def to_json(self):
        return json.dumps([{'kind': m.kind, 'enabled': m.enabled, 'visible': m.visible,
                            'params': m.params} for m in self.modules], indent=2)

    @classmethod
    def from_json(cls, payload):
        data = json.loads(payload)
        if not isinstance(data, list):
            raise ValueError('Rack preset must be a list')
        return cls([Module(**entry) for entry in data])


def suggest_mix_settings(peak_dbfs, rms_dbfs, crest_db, low_energy_ratio=None):
    """Transparent, deterministic starting-point suggestions; never auto-applies.

    These are heuristics, not audio analysis or machine learning.
    """
    notes = []
    if peak_dbfs > -1.0:
        notes.append({'module': 'clipper', 'reason': 'Peak is close to full scale; check headroom',
                      'proposal': {'ceiling_db': -1.0}})
    if crest_db > 15:
        notes.append({'module': 'compressor', 'reason': 'High crest factor; audition gentle compression',
                      'proposal': {'ratio': 2.0}})
    if crest_db < 5:
        notes.append({'module': 'transient', 'reason': 'Low crest factor; check whether transients need recovery',
                      'proposal': {'attack': 0.2}})
    if low_energy_ratio is not None and low_energy_ratio > 0.65:
        notes.append({'module': 'eq', 'reason': 'Low-frequency energy dominates; inspect bass balance',
                      'proposal': {'low_gain_db': -1.5}})
    return notes
