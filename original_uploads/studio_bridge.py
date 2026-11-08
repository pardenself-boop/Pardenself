"""Maschine Studio software-side command adapter. No USB access required."""
from dataclasses import dataclass, field
import json

PAGES = ('TRACK CITY','CHOP LABB','PAD LABB','INSTRUMENT','MIXER','MIDI MAP','STEMS','FX LABB')
PALETTE = {'mint':'#8ce3c9','orange':'#d7773d','burgundy':'#81374f','cream':'#f3e5c9','purple':'#7043ad','bg':'#17151c'}

@dataclass
class StudioBridge:
    dispatch: object
    page: int = 0
    shift: bool = False
    jog_mode: str = 'PLAYHEAD'
    bank: int = 0
    mappings: dict = field(default_factory=dict)
    def __post_init__(self):
        if not self.mappings:
            self.mappings = {
                'PLAY':'PLAY/STOP','REC':'RECORD','UNDO':'UNDO','REDO':'REDO',
                'COPY':'COPY','PASTE':'PASTE','SPLIT':'SPLIT',
                'ARRANGE':'PAGE:TRACK CITY','SAMPLING':'PAGE:CHOP LABB',
                'PAD MODE':'PAGE:PAD LABB','MIX':'PAGE:MIXER',
                'BROWSE':'PAGE:MIDI MAP','GROUP A':'BANK:0','GROUP B':'BANK:1',
                'MRQ':'MODE MRQ','TRK':'MODE TRK','ARR':'MODE ARR',
                'SHIFT+PASTE':'PASTE MERGE','SHIFT+COPY':'DUPLICATE',
                'JOG LEFT':'HW JOG -','JOG RIGHT':'HW JOG +',
                'JOG CLICK':'JOG CLICK','BACK':'JOG BACK','EDIT MOVE':'EDIT:MOVE','EDIT TRACK':'EDIT:TRACK MOVE',
                'EDIT TRIM L':'EDIT:TRIM LEFT','EDIT TRIM R':'EDIT:TRIM RIGHT',
                'EDIT MARQUEE':'EDIT:MARQUEE','EDIT LOOP L':'EDIT:LOOP START',
                'EDIT LOOP R':'EDIT:LOOP END','EDIT LOOP MOVE':'EDIT:LOOP MOVE','EDIT SLIP':'EDIT:SLIP',
                'MUTE TRACK':'TRACK MUTE','SOLO TRACK':'TRACK SOLO','SUITES':'SUITE BROWSER','SUITE NEXT':'SUITE NEXT','SUITE PREV':'SUITE PREV','SUITE CLICK':'SUITE CLICK',
                'SHIFT+JOG LEFT':'HW JOG -','SHIFT+JOG RIGHT':'HW JOG +',
            }
            for i in range(1,17):self.mappings[f'PAD {i}']=f'PAD {i}'
    def event(self,control):
        if control=='SHIFT':
            self.shift=not self.shift
            self.dispatch('JOG SHIFT')
            return 'SHIFT '+('ON' if self.shift else 'OFF')
        key=('SHIFT+' if self.shift else '')+control
        command=self.mappings.get(key,self.mappings.get(control))
        if command:
            self.dispatch(command)
        return command
    def map_control(self,control,command,shift=False):
        self.mappings[('SHIFT+' if shift else '')+control]=command
    def save(self,path):
        with open(path,'w',encoding='utf8') as f:json.dump(self.mappings,f,indent=2)
    def load(self,path):
        with open(path,encoding='utf8') as f:self.mappings.update(json.load(f))

CONTROLS = [
    'ARRANGE','SAMPLING','PAD MODE','MIX','BROWSE','MRQ','TRK','ARR',
    'COPY','PASTE','SPLIT','UNDO','REDO','PLAY','REC','SHIFT',
    'GROUP A','GROUP B','GROUP C','GROUP D','GROUP E','GROUP F','GROUP G','GROUP H',
    'JOG LEFT','JOG RIGHT','JOG CLICK','BACK','MUTE TRACK','SOLO TRACK','SUITES','SUITE NEXT','SUITE PREV','SUITE CLICK','EDIT MOVE','EDIT TRIM L','EDIT TRIM R','EDIT MARQUEE','EDIT LOOP L','EDIT LOOP R','EDIT LOOP MOVE','EDIT TRACK','EDIT SLIP',
] + [f'PAD {i}' for i in range(1,17)]
