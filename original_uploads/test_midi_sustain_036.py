import sys
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app'))
from street_midi_dispatch import StreetMidiDispatch

class Router:
    bindings = {}
    def translate(self, message): return []
class Automation:
    def process(self, *args, **kwargs): return []

def msg(kind, **kwargs): return SimpleNamespace(type=kind, channel=0, **kwargs)

def test_sustain_releases_after_pedal_up():
    events=[]
    d=StreetMidiDispatch(Router(), Automation(), lambda x: None, lambda n,v:events.append(('on',n)), lambda n:events.append(('off',n)))
    d.receive('keyboard',msg('note_on',note=60,velocity=100))
    d.receive('keyboard',msg('control_change',control=64,value=127))
    d.receive('keyboard',msg('note_off',note=60,velocity=0))
    assert events==[('on',60)]
    d.receive('keyboard',msg('control_change',control=64,value=0))
    assert events==[('on',60),('off',60)]

def test_panic_releases_sustained_notes():
    events=[]
    d=StreetMidiDispatch(Router(), Automation(), lambda x: None, lambda n,v:events.append(('on',n)), lambda n:events.append(('off',n)))
    d.receive('keyboard',msg('note_on',note=48,velocity=127))
    d.receive('keyboard',msg('control_change',control=64,value=127))
    d.receive('keyboard',msg('note_off',note=48,velocity=0))
    d.receive('keyboard',msg('control_change',control=123,value=0))
    assert events==[('on',48),('off',48)]
    assert not d.deferred and not d.sustain

def test_mapped_note_does_not_play():
    events=[]
    r=Router();r.bindings={'note:0:36':{'command':'PLAY'}}
    d=StreetMidiDispatch(r,Automation(),lambda x:None,lambda n,v:events.append('on'),lambda n:events.append('off'))
    d.receive('pad',msg('note_on',note=36,velocity=100))
    d.receive('pad',msg('note_off',note=36,velocity=0))
    assert events==[]

def test_invalid_midi_values_ignored():
    events=[]
    d=StreetMidiDispatch(Router(),Automation(),lambda x:None,lambda n,v:events.append('on'),lambda n:events.append('off'))
    d.receive('x',msg('note_on',note=200,velocity=100))
    d.receive('x',msg('control_change',control=64,value=999))
    assert events==[] and not d.sustain
