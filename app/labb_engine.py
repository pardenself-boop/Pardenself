"""22 playable LABB patches, one voice mixer and one protective master bus.
Pure Python reference DSP; not a production-quality VST or true stem separator.
"""
from dataclasses import dataclass
import math, random, threading
from street_sample_engine import StreetCrate

@dataclass(frozen=True)
class Labb:
 name: str
 wave: str
 attack: float
 decay: float
 sustain: float
 release: float
 cutoff: float
 color: str

LABBS = (
 Labb('Pad Labb','noise',.002,.12,.0,.08,.62,'#e17a35'),
 Labb('Chop Labb Pro','sine',.003,.22,.45,.12,.70,'#8ce3c9'),
 Labb('Smart Levels Labb','triangle',.015,.22,.65,.25,.68,'#9652ca'),
 Labb('Bass Labb Pro','sine',.005,.25,.72,.16,.48,'#81374f'),
 Labb('Break Labb Pro','noise',.001,.18,.12,.08,.80,'#e17a35'),
 Labb('Synth Labb','saw',.02,.30,.55,.28,.67,'#9652ca'),
 Labb('ARP Labb','square',.002,.09,.18,.08,.72,'#8ce3c9'),
 Labb('Key 88 Labb','triangle',.005,.32,.35,.30,.70,'#f3e5c9'),
 Labb('Stem Instrument Labb','sine',.025,.30,.60,.30,.58,'#8ce3c9'),
 Labb('Warp Labb','saw',.018,.38,.55,.30,.50,'#81374f'),
 Labb('Dice Labb','triangle',.004,.20,.32,.18,.74,'#9652ca'),
 Labb('Vocal Labb','formant',.04,.20,.64,.27,.57,'#e17a35'),
 Labb('Sample Labb','sine',.005,.20,.42,.16,.80,'#8ce3c9'),
 Labb('Brooklyn Iron Labb','saw',.012,.25,.62,.18,.45,'#81374f'),
 Labb('Melody Labb Pro','triangle',.025,.35,.55,.40,.62,'#f3e5c9'),
 Labb('Percussion Labb Pro','noise',.001,.07,.0,.06,.92,'#e17a35'),
 Labb('Texture Labb','noise',.10,.40,.48,.55,.24,'#9652ca'),
 Labb('Grain Labb','pulse',.004,.16,.26,.20,.55,'#8ce3c9'),
 Labb('Tape Labb','triangle',.03,.28,.55,.34,.39,'#81374f'),
 Labb('Vinyl Labb','noise',.002,.09,.02,.08,.20,'#f3e5c9'),
 Labb('Chord Labb','saw',.025,.30,.60,.35,.58,'#9652ca'),
 Labb('808 Labb Pro','sine',.002,.45,.80,.28,.35,'#e17a35'),
)
assert len(LABBS)==22 and len({p.name for p in LABBS})==22

class MasterBus:
 """Shared summing bus with DC blocker, soft clip and peak ceiling.
     It protects digital output; cannot prevent every distortion or dropout.
 """
 def __init__(self,drive=1.0,ceiling=.92):
  self.drive=drive;self.ceiling=ceiling;self.prev_in=0.;self.prev_out=0.;self.peak=0.;self.gain=.8
 def process(self,values):
  out=[];peak=0.
  for x in values:
   hp=x-self.prev_in+.995*self.prev_out;self.prev_in=x;self.prev_out=hp
   y=math.tanh(hp*self.drive)*self.gain
   y=max(-self.ceiling,min(self.ceiling,y))
   peak=max(peak,abs(y));out.append(y)
  self.peak=peak
  return out

class LabbEngine:
 def __init__(self,sample_rate=48000):
  self.sr=sample_rate;self.voices=[];self.lock=threading.RLock();self.selected=0
  self.master=MasterBus();self.crate=StreetCrate(sample_rate);self.orbs={'HISTORY':.5,'SOUL':.5,'JAZZ':.5,'DEEP':.5,'DUST':.5,'SPACE':.5,'TAPE':.5,'VINYL':.5}
  self.parameters=[{'attack':p.attack,'decay':p.decay,'sustain':p.sustain,'release':p.release,'cutoff':p.cutoff,'resonance':0.0,'drive':0.0,'width':0.5} for p in LABBS];self.midi_channels=[0]*22;self.volume=[.55]*22;self.mute=[False]*22;self.solo=[False]*22
 def note_on(self,note=48,velocity=.8,labb=None,duration=.5):
  idx=self.selected if labb is None else labb
  if not 0<=idx<22:raise IndexError(idx)
  if not 0<=note<=127:raise ValueError('MIDI note must be 0..127')
  if not 0<=velocity<=1:raise ValueError('Velocity must be 0..1')
  if duration<=0:raise ValueError('Duration must be positive')
  if self.crate.note_on(idx,note,velocity):return
  with self.lock:self.voices.append({'labb':idx,'freq':440*2**((note-69)/12),'age':0,'gate':int(duration*self.sr),'velocity':velocity,'phase':0.,'filter':0.,'seed':(idx+1)*197+note,'note':note,'release_at':None,'release_level':None})
 def note_off(self,note,labb=None):
  """Release matching notes without cutting the audio stream abruptly."""
  self.crate.note_off(note,labb)
  with self.lock:
   for voice in self.voices:
    if voice['note']==note and (labb is None or voice['labb']==labb) and voice['release_at'] is None:
     voice['release_at']=voice['age']
 def all_notes_off(self,labb=None):
  self.crate.all_notes_off(labb)
  with self.lock:
   for voice in self.voices:
    if labb is None or voice['labb']==labb:
     if voice['release_at'] is None:voice['release_at']=voice['age']
 def render_raw(self,frames):
  if frames<0:raise ValueError('frames must be nonnegative')
  out=[0.]*frames
  with self.lock:
   active=[];solo=any(self.solo)
   for v in self.voices:
    idx=v['labb'];patch=LABBS[idx];params=self.parameters[idx]
    if self.mute[idx] or (solo and not self.solo[idx]):continue
    age=v['age'];phase=v['phase'];filt=v['filter'];freq=v['freq'];gate=v['gate']
    rng=random.Random(v['seed']+age//128)
    for j in range(frames):
     t=(age+j)/self.sr
     position=age+j
     if position<params['attack']*self.sr:
      held_env=position/max(1.,params['attack']*self.sr)
     elif position<(params['attack']+params['decay'])*self.sr:
      held_env=1-(1-params['sustain'])*((position/self.sr-params['attack'])/max(.00001,params['decay']))
     else:held_env=params['sustain']
     release_at=v['release_at'] if v['release_at'] is not None else gate
     if position>=release_at:
      if v['release_level'] is None:
       rt=release_at/self.sr
       if rt<params['attack']:v['release_level']=rt/max(.00001,params['attack'])
       elif rt<params['attack']+params['decay']:v['release_level']=1-(1-params['sustain'])*((rt-params['attack'])/max(.00001,params['decay']))
       else:v['release_level']=params['sustain']
      env=v['release_level']*max(0.,1-(position-release_at)/max(1.,params['release']*self.sr))
     else:env=held_env
     if env<=0:continue
     phase=(phase+freq/self.sr)%1
     if patch.wave=='sine':sample=math.sin(phase*2*math.pi)
     elif patch.wave=='triangle':sample=1-4*abs(phase-.5)
     elif patch.wave=='saw':sample=2*phase-1
     elif patch.wave=='square':sample=1 if phase<.5 else -1
     elif patch.wave=='pulse':sample=1 if phase<.25 else -1
     elif patch.wave=='formant':sample=.7*math.sin(phase*2*math.pi)+.3*math.sin(phase*6*math.pi)
     else:sample=rng.uniform(-1,1)
     cutoff=min(.98,max(.015,params['cutoff']*(.3+self.orbs['SOUL']*.7)))
     filt+=cutoff*(sample-filt);sample=filt;sample=math.tanh(sample*(1+params['drive']*5))
     out[j]+=sample*env*v['velocity']*self.volume[idx]*.30
    v['age']+=frames;v['phase']=phase;v['filter']=filt
    if v['age']<(v['release_at'] if v['release_at'] is not None else gate)+int(params['release']*self.sr):active.append(v)
   self.voices=active
  sampled=self.crate.render(frames,self.volume,self.mute,self.solo)
  return [a+b for a,b in zip(out,sampled)]
 def load_sample(self,labb,path,root_note=60):
  self.crate.load(labb,path,root_note)
 def render(self,frames):return self.master.process(self.render_raw(frames))
 def set_parameter(self,index,key,value):
  if not 0<=index<22:raise IndexError(index)
  limits={'attack':(.001,2.),'decay':(.005,3.),'sustain':(0.,1.),'release':(.005,4.),'cutoff':(.015,.98),'resonance':(0.,1.),'drive':(0.,1.),'width':(0.,1.)}
  if key not in limits:raise KeyError(key)
  lo,hi=limits[key];value=float(value)
  if not math.isfinite(value):raise ValueError('Parameter must be finite')
  with self.lock:self.parameters[index][key]=max(lo,min(hi,value))
 def midi_note(self,channel,note,velocity=100,duration=.5):
  if not 1<=channel<=16:raise ValueError('MIDI channel must be 1..16')
  for i,ch in enumerate(self.midi_channels):
   if ch==channel:self.note_on(note,max(0,min(127,int(velocity)))/127,i,duration)
 def serialize(self):return {'selected':self.selected,'volume':self.volume[:],'mute':self.mute[:],'solo':self.solo[:],'orbs':dict(self.orbs),'parameters':[dict(p) for p in self.parameters],'midi_channels':self.midi_channels[:],'master':{'drive':self.master.drive,'gain':self.master.gain,'ceiling':self.master.ceiling}}
 def deserialize(self,data):
  self.selected=int(data.get('selected',0))%22
  for key in ('volume','mute','solo'):
   values=data.get(key)
   if isinstance(values,list) and len(values)==22:setattr(self,key,[bool(v) if key!='volume' else max(0.,min(1.,float(v))) for v in values])
  for i,params in enumerate(data.get('parameters',[])[:22]):
   for key,value in params.items():
    if key in self.parameters[i]:self.set_parameter(i,key,value)
  channels=data.get('midi_channels')
  if isinstance(channels,list) and len(channels)==22:self.midi_channels=[max(0,min(16,int(c))) for c in channels]
  for key,value in data.get('orbs',{}).items():
   if key in self.orbs:self.orbs[key]=max(0.,min(1.,float(value)))
  for key,value in data.get('master',{}).items():
   if key in ('drive','gain','ceiling'):setattr(self.master,key,max(.05,min(3.,float(value))))
