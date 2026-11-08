"""Shared MIDI linking and timestamped automation core. No GUI or audio dependencies.
Device-qualified controls, focus lock, track-level lanes, and non-destructive routing.
"""
from dataclasses import dataclass, field
from collections import deque
from time import monotonic
import json

MODES = ('off','read','touch','latch','write')
SCOPES = ('global','focus','hybrid')

@dataclass
class AutomationLane:
    parameter: str
    mode: str = 'read'
    points: list = field(default_factory=list)
    latched: bool = False
    last_touch: float = -1.0
    def set_mode(self, mode):
        if mode not in MODES: raise ValueError('Unknown automation mode')
        self.mode=mode; self.latched=False
    def write(self, position, value, playing, now=None, touched=True):
        if not playing or self.mode not in ('touch','latch','write'):return False
        now=monotonic() if now is None else now
        if touched:self.last_touch=now
        active=self.mode=='write' or self.mode=='latch' and (self.latched or touched) or self.mode=='touch' and (touched or 0<=now-self.last_touch<.35)
        if not active:return False
        if self.mode=='latch':self.latched=True
        self.points.append((float(position),float(value)))
        return True
    def stop(self):self.latched=False;self.last_touch=-1
    def value_at(self, position):
        if not self.points:return None
        pts=sorted(self.points)
        if position<=pts[0][0]:return pts[0][1]
        for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
            if x0<=position<=x1:return y1 if x1==x0 else y0+(y1-y0)*(position-x0)/(x1-x0)
        return pts[-1][1]

@dataclass
class Link:
    parameter: str
    scope: str = 'focus'
    target: str = ''
    mode: str = 'absolute'
    def __post_init__(self):
        if self.scope not in SCOPES:raise ValueError('Invalid scope')
        if self.mode not in ('absolute','relative_twos_complement','relative_binary_offset','relative_sign_magnitude'):raise ValueError('Invalid encoder mode')

class MidiAutomationEngine:
    def __init__(self):
        self.links={};self.focus={};self.focus_locks=set();self.groups={};self.lanes={};self.values={};self.monitor=deque(maxlen=512)
    def set_focus(self,device,target):
        if device not in self.focus_locks:self.focus[device]=target
    def lock_focus(self,device,locked=True):
        (self.focus_locks.add if locked else self.focus_locks.discard)(device)
    def group(self,name,devices):
        self.groups[name]=list(dict.fromkeys(devices))
    def bind(self,device,kind,channel,number,parameter,scope='focus',target='',mode='absolute'):
        if kind not in ('cc','note') or not 0<=channel<=15 or not 0<=number<=127:raise ValueError('Invalid MIDI address')
        self.links[(device,kind,channel,number,scope,target)]=Link(parameter,scope,target,mode)
    def process(self,device,message,position=0,playing=False,now=None):
        typ=getattr(message,'type',None)
        if typ not in ('control_change','note_on'):return []
        kind='cc' if typ=='control_change' else 'note'
        channel=getattr(message,'channel',None);number=getattr(message,'control',None) if kind=='cc' else getattr(message,'note',None)
        raw=getattr(message,'value',None) if kind=='cc' else getattr(message,'velocity',None)
        if not isinstance(channel,int) or not isinstance(number,int) or not isinstance(raw,int):return []
        self.monitor.append((device,typ,channel,number,raw))
        if kind=='note' and raw==0:return []
        focus=self.focus.get(device,'')
        matches=[]
        for (dev,k,ch,num,scope,target),link in self.links.items():
            if (dev,k,ch,num)!=(device,kind,channel,number):continue
            if scope=='global' or scope in ('focus','hybrid') and target==focus:matches.append((scope,link))
        # Context-specific links win; never double-trigger a parameter.
        matches.sort(key=lambda x: x[0]=='global')
        output=[];seen=set()
        for scope,link in matches:
            if link.parameter in seen:continue
            seen.add(link.parameter)
            old=self.values.get(link.parameter,0.)
            if link.mode=='absolute':value=raw/127
            else:
                if link.mode=='relative_twos_complement':delta=raw if raw<64 else raw-128
                elif link.mode=='relative_binary_offset':delta=raw-64
                else:delta=raw if raw<64 else -(raw-64)
                value=max(0.,min(1.,old+delta/127))
            self.values[link.parameter]=value
            lane=self.lanes.setdefault(link.parameter,AutomationLane(link.parameter))
            recorded=lane.write(position,value,playing,now)
            output.append((link.parameter,value,recorded))
        return output
    def stop(self):
        for lane in self.lanes.values():lane.stop()
    def save(self,path):
        data={'schema':1,'links':[dict(device=k[0],kind=k[1],channel=k[2],number=k[3],scope=k[4],target=k[5],parameter=v.parameter,mode=v.mode) for k,v in self.links.items()], 'groups':self.groups}
        with open(path,'w',encoding='utf-8') as f:json.dump(data,f,indent=2)
    def load(self,path):
        with open(path,encoding='utf-8') as f:data=json.load(f)
        if data.get('schema')!=1 or not isinstance(data.get('links'),list):raise ValueError('Invalid profile')
        staged=MidiAutomationEngine()
        for entry in data['links']:staged.bind(**entry)
        if not isinstance(data.get('groups',{}),dict):raise ValueError('Invalid groups')
        staged.groups=data.get('groups',{})
        self.links=staged.links;self.groups=staged.groups
