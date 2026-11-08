"""Original, editable top-down Maschine Studio control diagram (no USB protocol)."""
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Control:
    key: str
    label: str
    rect: tuple
    command: str
    encoder: bool = False


def controls():
    result = []
    def add(key,label,x,y,w,h,command,encoder=False):
        result.append(Control(key,label,(x,y,x+w,y+h),command,encoder))
    soft = [('MRQ','MODE MRQ'),('TRK','MODE TRK'),('ARR','MODE ARR'),('LOOP','LOOP TOGGLE'),
            ('COPY','RANGE COPY'),('CUT','RANGE CUT'),('DUP','RANGE DUPLICATE'),('INSERT','RANGE INSERT')]
    for i,(label,cmd) in enumerate(soft):add(f'SOFT {i+1}',str(i+1),.245+i*.069,.08,.052,.025,f'SURFACE KEY {i+1}')
    knob = [('LOOP POSITION','LOOP MOVE +'),('FOCUS LOOP','LOOP FOCUS'),('LOOP START','LOOP START +'),('LOOP LENGTH','LOOP END +'),
            ('JOG','HW JOG'),('SELECT','JOG CLICK'),('BACK','JOG BACK'),('PAGE','PAGE NEXT')]
    for i,(label,cmd) in enumerate(knob):add(f'KNOB {i+1}',str(i+1),.25+i*.069,.36,.04,.055,f'SURFACE KNOB {i+1} +',True)
    left=[('CHANNEL','TRACK CITY','MODE TRK'),('PLUGIN','INSTRUMENT','EDIT SOUND'),('ARRANGE','ARRANGE','SURFACE ARRANGE'),('MIX','MIX','EDIT FX'),
          ('BROWSE','BROWSE','BROWSE SOUNDS'),('SAMPLING','SAMPLING','PAGE PREV'),('NAV LEFT','◀','PAGE PREV'),('NAV RIGHT','▶','PAGE NEXT'),
          ('ALL','ALL','LOOP ALL'),('AUTO','AUTO','LOOP FOCUS')]
    for i,(key,label,cmd) in enumerate(left):add(key,label,.065+(i%2)*.075,.09+(i//2)*.065,.061,.036,cmd)
    for i,(key,cmd) in enumerate([('TAP','JOG CLICK'),('STEP MODE','MODE MRQ'),('MACRO','SUITE BROWSER'),('NOTE REPEAT','RECORD')]):
        add(key,key,.055+i*.067,.49,.058,.035,cmd)
    for i in range(8):add(f'GROUP {chr(65+i)}',chr(65+i),.055+(i%4)*.067,.61+(i//4)*.063,.056,.041,'BANK PREV' if i==0 else 'BANK NEXT' if i==1 else 'SUITE NEXT')
    for i in range(16):
        add(f'PAD {i+1}',str(i+1),.38+(i%4)*.086,.515+(3-i//4)*.105,.072,.088,f'BANK PAD {i+1}')
    for i,(key,cmd) in enumerate([('RESTART','RESTART'),('GRID','MODE MRQ'),('SYNC','LOOP FOCUS'),('REC MODE','RECORD'),
                                  ('PLAY','PLAY/STOP'),('REC','RECORD'),('ERASE','RANGE DELETE'),('SHIFT','JOG SHIFT')]):
        add(key,key,.055+(i%4)*.067,.81+(i//4)*.065,.057,.037,cmd)
    edits=[('COPY','RANGE COPY'),('PASTE','RANGE PASTE'),('NOTE','LABB NOTE PLAY'),('NUDGE','EDIT:MOVE'),
           ('UNDO','UNDO'),('REDO','REDO'),('QUANTIZE','LOOP FOCUS'),('CLEAR','RANGE DELETE'),
           ('SELECT','EDIT:SELECT'),('EVENTS','MODE TRK'),('BACK','JOG BACK'),('ENTER','JOG CLICK')]
    for i,(key,cmd) in enumerate(edits):add('EDIT '+key,key,.77+(i%4)*.052,.515+(i//4)*.05,.045,.032,cmd)
    add('JOG ROTATE','JOG',.79,.70,.16,.21,'HW JOG',True)
    add('JOG PRESS','PRESS',.837,.762,.066,.085,'JOG CLICK')
    for i,(key,cmd) in enumerate([('JOG BACK','JOG BACK'),('JOG LEFT','HW JOG -'),('JOG RIGHT','HW JOG +'),('JOG ENTER','JOG CLICK')]):
        add(key,key.replace('JOG ',''),.77+i*.052,.935,.045,.03,cmd)
    for i in range(4):add(f'MONITOR {i+1}',str(i+1),.87,.14+i*.047,.035,.031,'TRACK MUTE')
    add('MONITOR LEVEL','LEVEL',.845,.36,.07,.055,'JOG',True)
    return tuple(result)

CONTROLS = controls()
BY_KEY = {control.key:control for control in CONTROLS}


def validate_rect(rect):
    if not isinstance(rect,(list,tuple)) or len(rect)!=4:
        raise ValueError('A hotspot needs four normalized coordinates')
    if any(type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=1 for v in rect):
        raise ValueError('Hotspot coordinates must be between zero and one')
    if rect[2]<=rect[0] or rect[3]<=rect[1]:
        raise ValueError('Hotspot must have positive size')
    return tuple(rect)


def hit_test(x,y,layout=None):
    if not 0<=x<=1 or not 0<=y<=1:return None
    layout=layout or {}
    # The jog press is inside the jog ring: last defined control wins.
    for control in reversed(CONTROLS):
        x0,y0,x1,y1=layout.get(control.key,control.rect)
        if x0<=x<=x1 and y0<=y<=y1:return control.key
    return None


def move_rect(rect,dx,dy):
    x0,y0,x1,y1=validate_rect(rect)
    dx=max(-x0,min(dx,1-x1));dy=max(-y0,min(dy,1-y1))
    return (x0+dx,y0+dy,x1+dx,y1+dy)
