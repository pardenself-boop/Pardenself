"""Hardware-first MIDI transport for Maschine Studio in Controller Editor MIDI mode.
Native USB HID/display/LED support is a separate future backend.
Pure Python, no device needed for tests.
"""
from dataclasses import dataclass, field
import json
import copy

VALID_MODES = ('relative_twos_complement', 'relative_binary_offset', 'relative_sign_magnitude', 'absolute')

@dataclass
class MidiControlRouter:
    """Translate raw MIDI events into the existing TOOLBOXX command vocabulary."""
    bindings: dict = field(default_factory=dict)
    shift: bool = False
    def bind(self, kind, channel, number, command, mode='button'):
        if kind not in ('note','cc'): raise ValueError('Unsupported event kind')
        if type(channel) is not int or type(number) is not int or not 0 <= channel <= 15 or not 0 <= number <= 127: raise ValueError('Invalid MIDI address')
        if not isinstance(command, str) or not command.strip(): raise ValueError('Invalid MIDI command')
        if mode not in ('button',) + VALID_MODES: raise ValueError('Unsupported mode')
        self.bindings[f'{kind}:{channel}:{number}']={'command':command,'mode':mode}
    def translate(self, message):
        typ=getattr(message,'type',None)
        if typ not in ('note_on','note_off','control_change'):return []
        kind='cc' if typ=='control_change' else 'note'
        number=getattr(message,'control',None) if kind=='cc' else getattr(message,'note',None)
        channel=getattr(message,'channel',None)
        if number is None or channel is None:return []
        binding=self.bindings.get(f'{kind}:{channel}:{number}')
        if binding is None:return []
        value=getattr(message,'value',0) if kind=='cc' else getattr(message,'velocity',0)
        mode=binding['mode']; command=binding['command']
        if mode=='button':
            if typ=='note_off' or (typ=='note_on' and value==0) or (typ=='control_change' and value==0):return []
            if command=='SHIFT':self.shift=not self.shift;return ['JOG SHIFT']
            return [command]
        if typ!='control_change':return []
        if mode=='relative_twos_complement': delta=value if value<=63 else value-128
        elif mode=='relative_binary_offset':delta=value-64
        elif mode=='relative_sign_magnitude':delta=-(value-64) if value>=64 else value
        else:delta=value-64
        if delta==0:return []
        if command=='HW JOG':return ['HW JOG +' if delta>0 else 'HW JOG -']*min(abs(delta),16)
        if command=='JOG':return ['JOG +' if delta>0 else 'JOG -']*min(abs(delta),16)
        return [command]*min(abs(delta),16)
    def serialize(self):
        return {'schema':1, 'bindings':copy.deepcopy(self.bindings)}
    def deserialize(self, data):
        if not isinstance(data, dict) or data.get('schema') != 1 or not isinstance(data.get('bindings'), dict):
            raise ValueError('Invalid MIDI profile')
        validated = MidiControlRouter()
        for key, info in data['bindings'].items():
            if not isinstance(key, str) or not isinstance(info, dict):
                raise ValueError('Invalid MIDI binding')
            try:
                kind, channel, number = key.split(':')
                validated.bind(kind, int(channel), int(number), info['command'], info['mode'])
            except (ValueError, KeyError, TypeError) as exc:
                raise ValueError(f'Invalid MIDI binding: {key}') from exc
        self.bindings = validated.bindings
        self.shift = False
    def save(self,path):
        with open(path,'w',encoding='utf-8') as f:json.dump(self.serialize(),f,indent=2)
    def load(self,path):
        with open(path,encoding='utf-8') as f:data=json.load(f)
        self.deserialize(data)
