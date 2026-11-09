"""BOOM BAP TOOLBOXX v0.4 - Windows prototype, virtual Maschine Studio + sampler."""
import json, math, queue, threading, time, wave, tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from array import array
from arranger_core import Arranger
from arranger_ranges import RangeEditor
from surface_context import SurfaceContext
from arrangement_playback import velocity_hits_at, advance
from pad_patterns import PadTakes, pattern_step, performance_beat
from audio_regions import AudioRegions, regions_starting
from suite_registry import SUITES, SuiteRouter
from labb_engine import LabbEngine, LABBS
from note_lane import NoteLane
from studio_midi_adapter import MidiControlRouter
from street_midi_dispatch import StreetMidiDispatch
from midi_automation_engine import MidiAutomationEngine
from mix_rack import MixRack, MODULES
from ui_shortcuts import dispatch_shortcut
from midi_activity import MidiActivity
from metronome import Metronome

C={'bg':'#17151c','panel':'#28212d','cream':'#f3e5c9','mint':'#8ce3c9','orange':'#d7773d','burgundy':'#81374f','purple':'#7043ad','dim':'#a9a0ad'}
PAGES=['TRACK CITY','CHOP LABB','PAD LABB','INSTRUMENT','MIXER','MIDI MAP']
COMMANDS=['PLAY/STOP','RECORD','PAGE NEXT','PAGE PREV','BANK NEXT','BANK PREV','JOG +','JOG -','JOG MODE','UNDO','REDO','MODE MRQ','MODE TRK','MODE ARR','LOOP START -','LOOP START +','LOOP END -','LOOP END +','LOOP MOVE -','LOOP MOVE +','COPY','PASTE','PASTE MERGE','SPLIT','JOG CLICK','JOG BACK','JOG SHIFT','HW JOG +','HW JOG -','SUITE NEXT','SUITE PREV','SUITE CLICK','SUITE BROWSER','TRACK MUTE','TRACK SOLO','LABB NEXT','LABB PREV','LABB PLAY','LABB BROWSER','LABB ARM','LABB NOTE +','LABB NOTE -','LABB NOTE PLAY','LABB CLIP']+[f'EDIT:{op}' for op in ('SELECT','MOVE','TRACK MOVE','TRIM LEFT','TRIM RIGHT','SLIP','MARQUEE','LOOP START','LOOP END','LOOP MOVE')]+[f'PAD {i+1}' for i in range(32)]+[f'BANK PAD {i+1}' for i in range(16)]+['RANGE COPY','RANGE CUT','RANGE PASTE','RANGE DELETE','RANGE DUPLICATE','RANGE INSERT','LOOP TOGGLE','LOOP ALL','LOOP FOCUS','RESTART','BROWSE SOUNDS','EDIT SOUND','EDIT FX','SOUND PREV','SOUND NEXT','FX PREV','FX NEXT','FX BYPASS']+[f'SURFACE {page}' for page in SurfaceContext.PAGES]+[f'SURFACE KEY {i}' for i in range(1,9)]+[f'SURFACE KNOB {i} +' for i in range(1,9)]

COMMANDS += ['TAKE UNDO','TAKE REDO','METRONOME TOGGLE','COUNT IN TOGGLE']

class Engine:
 def __init__(self):
  self.labbs=LabbEngine();self.mix_rack=MixRack();self.samples=[None]*32;self.sample_paths=[None]*32;self.regions=AudioRegions();self.voices=[];self.lock=threading.RLock();self.sr=48000;self.stream=None;self.audio_status='Audio stopped';self.on_message=lambda m:None
  self.metronome=Metronome()
 def click(self,accent=False):
  with self.lock:self.metronome.trigger(accent)
 def clear_clicks(self):
  with self.lock:self.metronome.clear()
 def load(self,index,path):
  if not 0 <= index < len(self.samples):raise ValueError("Pad index must be 0–31")
  with wave.open(path,'rb') as w:
   nch,sw,rate,n=w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes()
   if nch not in (1,2) or sw != 2 or rate < 8000 or rate > 192000 or n > rate*120:raise ValueError("Use mono/stereo 16-bit PCM WAV, max 120 seconds")
   if w.getcomptype() != "NONE":raise ValueError("Compressed WAV is unsupported")
   raw=w.readframes(n)
  if sw!=2:raise ValueError('Load a 16-bit PCM WAV file (mono or stereo).')
  vals=array('h');vals.frombytes(raw)
  if nch>1: mono=[sum(vals[i:i+nch])/nch/32768 for i in range(0,len(vals),nch)]
  else:mono=[v/32768 for v in vals]
  with self.lock:
   self.samples[index]=(mono,rate,Path(path).stem)
   self.sample_paths[index]=str(Path(path).expanduser().resolve())
 def trigger(self,index,velocity=1.0):
  if not 0 <= index < len(self.samples):raise ValueError("Pad index must be 0–31")
  if type(velocity) not in (int,float) or not math.isfinite(velocity) or not 0<=velocity<=1:raise ValueError('Pad velocity must be between zero and one')
  if velocity==0:return
  with self.lock:
   if self.samples[index]:
    if len(self.voices)>=64:self.voices.pop(0)
    self.voices.append([index,0.0,float(velocity)])
 def render(self,frames):
  out=[0.0]*frames
  with self.lock:
   active=[]
   for idx,pos,velocity in self.voices:
    data,rate,_=self.samples[idx];step=rate/self.sr
    for j in range(frames):
     k=int(pos)
     if k>=len(data):break
     fraction=pos-k
     sample=data[k]*(1-fraction)+(data[k+1] if k+1<len(data) else data[k])*fraction
     out[j]+=sample*.55*velocity;pos+=step
    if pos<len(data):active.append([idx,pos,velocity])
   self.voices=active
   regions=self.regions.render(frames)
   out=[a+b for a,b in zip(out,regions)]
   instruments=self.labbs.render_raw(frames)
   out=[a+b for a,b in zip(out,instruments)]
   out=self.mix_rack.process(out,self.sr)
   if self.metronome.voices:
    click=self.metronome.render(frames,self.sr)
    out=[sample+beat for sample,beat in zip(out,click)]
  return self.labbs.master.process(out)
 def start(self,device=None):
  """Start a stream, releasing partially opened devices after failures."""
  try:import sounddevice as sd
  except ImportError:raise RuntimeError('Install sounddevice: pip install sounddevice')
  self.stop()
  self.audio_error=None
  def callback(outdata,frames,time_info,status):
   # Never allow a DSP exception to leave stale output in the sound card buffer.
   outdata.fill(0)
   if status:self.audio_status='Audio warning: '+str(status)
   try:
    samples=self.render(frames)
    for i,v in enumerate(samples[:frames]):
     if math.isfinite(v):outdata[i,0]=v;outdata[i,1]=v
   except Exception as exc:
    self.audio_error=str(exc)
    self.audio_status='Audio DSP error: '+str(exc)
  stream=None
  try:
   stream=sd.OutputStream(device=device,samplerate=self.sr,channels=2,blocksize=256,callback=callback)
   stream.start()
  except Exception as exc:
   if stream is not None:
    try:stream.close()
    except Exception:pass
   self.stream=None
   self.audio_status='Audio start failed: '+str(exc)
   raise RuntimeError(self.audio_status) from exc
  self.stream=stream
  self.audio_status='Audio running'
 def stop(self):
  stream=self.stream
  self.stream=None
  if stream is not None:
   try:stream.stop()
   finally:stream.close()
  self.audio_status='Audio stopped'
  self.clear_clicks()

from hardware_edit import HardwareEdit

class App:
 def __init__(self,root):
  self.root=root;root.title('BOOM BAP TOOLBOXX | COOK UP v1.4');root.geometry('1250x830');root.configure(bg=C['bg'])
  self.suites=SuiteRouter();self.engine=Engine();self.labbs=self.engine.labbs;self.notes=NoteLane();self.note_pitch=48;self.page=0;self.bank=0;self.selected_pad=0;self.playing=False;self.recording=False;self.bpm=84;self.step=0;self.jog_mode=0;self.jog_modes=['PLAYHEAD','SCROLL','ZOOM','CLIP MOVE','CLIP LENGTH','SLICE','LOOP START','LOOP END','LOOP MOVE'];self.playhead=0;self.zoom=1;self.clips=[{'track':0,'start':0,'length':4,'name':'DRUM A'},{'track':1,'start':4,'length':4,'name':'CHOP B'},{'track':2,'start':0,'length':8,'name':'BASS A'}];self.selected_clip=0;self.arr=Arranger();self.range_editor=RangeEditor(self.arr);self.hardware_edit=HardwareEdit(self);self.surface_context=SurfaceContext(self);self.clips=self.arr.clips;self.drag=None;self.marquee_start=None
  self.pattern=[[False]*16 for _ in range(32)];self.patterns={'main':self.pattern};self.mapping={};self.hardware_midi=MidiControlRouter();self.midi_automation=MidiAutomationEngine();self.mix_rack=self.engine.mix_rack;self.learn=None;self.hardware_learn=None;self.last_hardware_learn=None;self.hardware_status='No MIDI input connected';self.midi_connected_name=None;self.midi_port=None;self.midi_thread=None;self.events=queue.Queue(maxsize=2048);self.midi_dropped=0;self.tick_id=None
  self.midi_activity=MidiActivity()
  self.pad_takes=PadTakes();self._tick_started=None;self._tick_beat=0.;self._pad_skip_once={}
  self.metronome_enabled=False;self.count_in_enabled=False;self._count_in_remaining=0;self._count_in_active=False
  self.street_dispatch=StreetMidiDispatch(self.hardware_midi,self.midi_automation,self.command,self._midi_note_on,self._midi_note_off,self.apply_midi_mix_changes,pad_command=self._midi_pad_command)
  self._style();self._layout();self._refresh();self.root.after(40,self._poll)
  root.protocol('WM_DELETE_WINDOW',self.close)
 def open_hardware_setup(self):
  from hardware_setup_window import HardwareSetupWindow
  if hasattr(self,'hardware_setup_window') and self.hardware_setup_window.win.winfo_exists():self.hardware_setup_window.win.lift()
  else:self.hardware_setup_window=HardwareSetupWindow(self)
 def open_advanced_midi(self):
  from advanced_midi_window import AdvancedMidiWindow
  AdvancedMidiWindow(self)
 def _style(self):
  st=ttk.Style();st.theme_use('clam');st.configure('TCombobox',fieldbackground=C['cream'],background=C['purple'])
 def label(self,parent,text,fg='cream',size=10,bold=False):return tk.Label(parent,text=text,bg=parent.cget('bg'),fg=C.get(fg,fg),font=('Segoe UI',size,'bold' if bold else 'normal'))
 def btn(self,parent,text,command,color='panel',width=None):return tk.Button(parent,text=text,command=command,bg=C[color],fg=C['cream'],activebackground=C['orange'],activeforeground=C['cream'],relief='flat',padx=9,pady=6,width=width,cursor='hand2')
 def _layout(self):
  top=tk.Frame(self.root,bg=C['burgundy'],height=56);top.pack(fill='x');top.pack_propagate(False)
  self.label(top,'◈  BOOM BAP TOOLBOXX  /  SOUND LABB DIVISION',size=16,bold=True).pack(side='left',padx=15)
  self.btn(top,'◀ PAGE',lambda:self.set_page(self.page-1),'purple').pack(side='right',padx=3,pady=8)
  self.btn(top,'PAGE ▶',lambda:self.set_page(self.page+1),'purple').pack(side='right',padx=3,pady=8)
  self.btn(top,'STUDIO HARDWARE MAP',self.open_studio,'orange').pack(side='right',padx=3)
  self.btn(top,'MIDI HARDWARE SETUP',self.open_hardware_setup,'purple').pack(side='right',padx=3)
  self.btn(top,'22 LABBS',self.open_labbs,'mint').pack(side='right',padx=3)
  self.btn(top,'MIDI LABB',self.open_advanced_midi,'purple').pack(side='right',padx=3)
  self.btn(top,'COOK UP MATRIX',self.open_cookup,'orange').pack(side='right',padx=3)
  self.btn(top,'SAVE PROJECT',self.save).pack(side='right',padx=3)
  self.btn(top,'LOAD PROJECT',self.load).pack(side='right',padx=3)
  nav=tk.Frame(self.root,bg=C['bg']);nav.pack(fill='x',pady=5)
  for i,p in enumerate(PAGES):self.btn(nav,p,lambda i=i:self.set_page(i),'purple' if i==0 else 'panel').pack(side='left',padx=4)
  self.main=tk.Frame(self.root,bg=C['bg']);self.main.pack(fill='both',expand=True)
  self.left=tk.Frame(self.main,bg=C['panel'],width=780);self.left.pack(side='left',fill='both',expand=True,padx=8,pady=6)
  self.right=tk.Frame(self.main,bg=C['bg'],width=420);self.right.pack(side='right',fill='y',padx=8,pady=6)
  self.label(self.left,'TRACK CITY  •  ARRANGER',size=13,bold=True).pack(anchor='w',padx=12,pady=8)
  self.arranger=tk.Canvas(self.left,height=235,bg='#1e1b24',highlightthickness=0);self.arranger.pack(fill='x',padx=10)
  self.arranger.bind('<Button-1>',self.select_clip);self.arranger.bind('<B1-Motion>',self.drag_clip);self.arranger.bind('<ButtonRelease-1>',self.release_clip);self.arranger.bind('<Button-3>',self.right_click)
  for key,cmd in [('<Control-z>','UNDO'),('<Control-y>','REDO'),('<Control-c>','COPY'),('<Control-v>','PASTE')]:self.root.bind(key,lambda e,c=cmd:dispatch_shortcut(e,lambda:self.command(c)))
  self.root.bind('<Delete>',lambda e:dispatch_shortcut(e,self.delete_clip))
  transport=tk.Frame(self.left,bg=C['panel']);transport.pack(fill='x',pady=8)
  self.btn(transport,'▶ PLAY / STOP',self.toggle_play,'orange').pack(side='left',padx=5)
  self.btn(transport,'● REC',self.toggle_rec,'burgundy').pack(side='left',padx=5)
  self.btn(transport,'BOUNCE WAV',self.export_track_city,'mint').pack(side='left',padx=5)
  self.btn(transport,'+ CLIP',self.add_clip,'purple').pack(side='left',padx=5)
  self.btn(transport,'+ LABB MIDI',self.add_labb_clip,'mint').pack(side='left',padx=5)
  self.btn(transport,'+ AUDIO WAV',self.add_audio_clip,'mint').pack(side='left',padx=5)
  self.btn(transport,'DUPLICATE',self.duplicate).pack(side='left',padx=5)
  self.btn(transport,'SPLIT',self.split).pack(side='left',padx=5)
  self.btn(transport,'DELETE',self.delete_clip).pack(side='left',padx=5)
  modebar=tk.Frame(self.left,bg=C['panel']);modebar.pack(fill='x',padx=8,pady=3)
  for mode in ('MRQ','TRK','ARR'):self.btn(modebar,mode,lambda m=mode:self.set_edit_mode(m),'purple').pack(side='left',padx=2)
  self.btn(modebar,'COPY',lambda:self.command('COPY')).pack(side='left',padx=2)
  self.btn(modebar,'PASTE',lambda:self.command('PASTE')).pack(side='left',padx=2)
  self.btn(modebar,'PASTE MERGE',lambda:self.command('PASTE MERGE')).pack(side='left',padx=2)
  self.btn(modebar,'LOOP ◀',lambda:self.arr_loop('start',-.25),'burgundy').pack(side='left',padx=2)
  self.btn(modebar,'LOOP ▶',lambda:self.arr_loop('end',.25),'orange').pack(side='left',padx=2)
  self.btn(modebar,'LOOP SHIFT',lambda:self.arr_loop('body',1),'purple').pack(side='left',padx=2)
  self.btn(modebar,'SNAP',self.toggle_snap).pack(side='left',padx=2)
  self.btn(modebar,'MUTE TRACK',lambda:self.command('TRACK MUTE'),'burgundy').pack(side='left',padx=2)
  self.btn(modebar,'SOLO TRACK',lambda:self.command('TRACK SOLO'),'orange').pack(side='left',padx=2)
  self.label(self.left,'PAD LABB  •  32 SLOTS  /  16 PER BANK',size=12,bold=True).pack(anchor='w',padx=12,pady=7)
  ptop=tk.Frame(self.left,bg=C['panel']);ptop.pack(fill='x')
  self.btn(ptop,'BANK A',lambda:self.set_bank(0),'orange').pack(side='left',padx=8)
  self.btn(ptop,'BANK B',lambda:self.set_bank(1),'purple').pack(side='left',padx=8)
  self.btn(ptop,'LOAD WAV INTO SELECTED PAD',self.load_sample).pack(side='right',padx=8)
  pads=tk.Frame(self.left,bg=C['panel']);pads.pack(pady=9)
  self.pad_buttons=[]
  for i in range(16):
   b=self.btn(pads,f'{i+1:02}',lambda i=i:self.pad(i),'purple',width=12);b.grid(row=i//4,column=i%4,padx=5,pady=5,ipady=8);self.pad_buttons.append(b)
  self.label(self.left,'16-STEP PATTERN  •  SELECT CLIP + PAD, CLICK STEPS',size=11,bold=True).pack(anchor='w',padx=12)
  steps=tk.Frame(self.left,bg=C['panel']);steps.pack(pady=8)
  self.step_buttons=[]
  for i in range(16):
   b=self.btn(steps,str(i+1),lambda i=i:self.toggle_step(i),'panel',width=2);b.pack(side='left',padx=2);self.step_buttons.append(b)
  self.label(self.right,'MASCHINE STUDIO  /  VIRTUAL HARDWARE',size=12,bold=True).pack(anchor='w',pady=7)
  self.screens=tk.Frame(self.right,bg=C['bg']);self.screens.pack()
  self.screen1=tk.Canvas(self.screens,width=204,height=145,bg='#17141c',highlightbackground=C['mint']);self.screen1.pack(side='left',padx=3)
  self.screen2=tk.Canvas(self.screens,width=204,height=145,bg='#17141c',highlightbackground=C['orange']);self.screen2.pack(side='left',padx=3)
  self.label(self.right,'PAGE / SCREEN CONTROL',size=10,bold=True).pack(anchor='w',pady=9)
  pagegrid=tk.Frame(self.right,bg=C['bg']);pagegrid.pack(fill='x')
  for i,p in enumerate(PAGES):self.btn(pagegrid,p,lambda i=i:self.set_page(i),'burgundy',width=14).grid(row=i//3,column=i%3,padx=2,pady=2)
  jog=tk.Frame(self.right,bg=C['panel']);jog.pack(fill='x',pady=8)
  self.jog_label=self.label(jog,'JOG: PLAYHEAD','mint',11,True);self.jog_label.pack(pady=5)
  jr=tk.Frame(jog,bg=C['panel']);jr.pack(pady=5)
  self.btn(jr,'◀ TURN',lambda:self.jog(-1),'purple').pack(side='left',padx=6)
  self.btn(jr,'PRESS / MODE',self.next_jog,'orange').pack(side='left',padx=6)
  self.btn(jr,'TURN ▶',lambda:self.jog(1),'purple').pack(side='left',padx=6)
  hw=tk.Frame(self.right,bg=C['bg']);hw.pack(fill='x',pady=5)
  for i,name in enumerate(['PLAY/STOP','RECORD','UNDO','REDO','BANK PREV','BANK NEXT']):self.btn(hw,name,lambda name=name:self.command(name),'panel',width=12).grid(row=i//3,column=i%3,padx=3,pady=3)
  self.label(self.right,'MIDI COMMAND CENTER  •  LEARN',size=11,bold=True).pack(anchor='w',pady=7)
  midi=tk.Frame(self.right,bg=C['bg']);midi.pack(fill='x')
  self.midi_device=ttk.Combobox(midi,width=29,state='readonly');self.midi_device.pack(side='left')
  self.btn(midi,'SCAN',self.scan_midi,'purple').pack(side='left',padx=3)
  self.btn(midi,'OPEN',self.open_midi,'orange').pack(side='left')
  self.midi_cmd=ttk.Combobox(self.right,values=COMMANDS,state='readonly');self.midi_cmd.set('PAD 1');self.midi_cmd.pack(fill='x',pady=5)
  self.btn(self.right,'LEARN SELECTED COMMAND',self.arm_learn,'burgundy').pack(fill='x')
  self.label(self.right,'AUDIO OUTPUT  •  NO MPC CONTROL MAPPING',size=10,bold=True).pack(anchor='w',pady=7)
  audio=tk.Frame(self.right,bg=C['bg']);audio.pack(fill='x')
  self.audio_device=ttk.Combobox(audio,width=30,state='readonly');self.audio_device.pack(side='left')
  self.btn(audio,'SCAN',self.scan_audio,'purple').pack(side='left',padx=2)
  self.btn(audio,'START',self.start_audio,'orange').pack(side='left')
  self.btn(self.right,'STOP AUDIO',self.engine.stop).pack(fill='x',pady=5)
  self.status=self.label(self.right,'Ready. Virtual Studio works without hardware.','mint',9);self.status.pack(anchor='w',pady=6)
  self.scan_audio();self.scan_midi()
 def show_workstation(self):
  self.root.deiconify();self.root.lift()
 def open_audio_midi(self):
  from audio_midi_window import AudioMidiWindow
  if hasattr(self,'audio_midi_window') and self.audio_midi_window.win.winfo_exists():self.audio_midi_window.win.lift()
  else:self.audio_midi_window=AudioMidiWindow(self)
 def open_updates(self):
  from update_window import UpdateWindow
  if hasattr(self,'update_window') and self.update_window.win.winfo_exists():self.update_window.win.lift()
  else:self.update_window=UpdateWindow(self)
 def open_cookup(self):
  from cookup_ui import CookUpWindow
  if hasattr(self,'cookup_window') and self.cookup_window.win.winfo_exists():self.cookup_window.win.lift();self.cookup_window.refresh()
  else:self.cookup_window=CookUpWindow(self)
 def open_dual_screen(self):
  from controller_map_window import ControllerMapWindow
  if hasattr(self,'controller_map_window') and self.controller_map_window.win.winfo_exists():self.controller_map_window.win.lift()
  else:self.controller_map_window=ControllerMapWindow(self)
 def open_mix_rack(self):
  self.surface_context.set_page('FX')
  from mix_rack_window import MixRackWindow
  if hasattr(self,'mix_rack_window') and self.mix_rack_window.win.winfo_exists():self.mix_rack_window.win.lift()
  else:self.mix_rack_window=MixRackWindow(self)
 def open_sound_browser(self,page='SOUND'):
  from sound_browser_window import SoundBrowserWindow
  self.surface_context.set_page(page)
  if hasattr(self,'sound_browser_window') and self.sound_browser_window.win.winfo_exists():self.sound_browser_window.win.lift();self.sound_browser_window.refresh()
  else:self.sound_browser_window=SoundBrowserWindow(self)
 def sync_fx_window(self):
  if hasattr(self,'mix_rack_window') and self.mix_rack_window.win.winfo_exists():self.mix_rack_window.refresh()
 def set_mix_rack(self,rack):
  with self.engine.lock:self.engine.mix_rack=rack;self.mix_rack=rack
 def apply_midi_mix_changes(self, changes):
  """Normalized MIDI targets use mix.<index>.<parameter>; ignore unrelated targets."""
  for parameter,value,_ in changes:
   parts=parameter.split('.')
   if len(parts)!=3 or parts[0]!='mix' or not parts[1].isdigit():continue
   index=int(parts[1]);name=parts[2]
   if index>=len(self.mix_rack.modules):continue
   module=self.mix_rack.modules[index]
   if name not in MODULES[module.kind]:continue
   lo,hi,_=MODULES[module.kind][name]
   self.mix_rack.set_parameter(index,name,lo+(hi-lo)*value)
 def open_labbs(self):
  from labb_window import LabbWindow
  if hasattr(self,'labb_window') and self.labb_window.win.winfo_exists():self.labb_window.win.lift()
  else:self.labb_window=LabbWindow(self)
 def open_suites(self):
  from suite_window import SuiteWindow
  if hasattr(self,'suite_window') and self.suite_window.win.winfo_exists():self.suite_window.win.lift();self.suite_window.refresh()
  else:self.suite_window=SuiteWindow(self)
 def open_studio(self):
  from studio_window import StudioWindow
  self.studio_window=StudioWindow(self)
 def set_page(self,i):self.page=i%len(PAGES);self._refresh()
 def set_bank(self,i):self.bank=i%2;self.selected_pad=self.bank*16+self.selected_pad%16;self._refresh()
 def pad(self,i,velocity=1.0):
  if not 0 <= i < 16:raise ValueError('Visible pad index must be 0–15')
  self.trigger_absolute_pad(self.bank*16+i,velocity)
 def trigger_absolute_pad(self,index,velocity=1.0):
  if not 0 <= index < 32:raise ValueError('Pad index must be 0–31')
  self.bank=index//16
  self.selected_pad=index
  self.engine.trigger(index,velocity)
  if getattr(self,'recording',False) and getattr(self,'playing',False) and not getattr(self,'_count_in_active',False) and velocity>0:self.record_pad(index,velocity)
  self._refresh()
 def record_pad(self,index,velocity):
  arr=self.arr
  beat=performance_beat(self.playhead,self.bpm,arr.loop_start,arr.loop_end,arr.loop_enabled,time.monotonic(),getattr(self,'_tick_beat',None),getattr(self,'_tick_started',None))
  selected=[c for c in arr.clips if c['id'] in arr.selected]
  clip=next((c for c in selected if c.get('kind','pattern')=='pattern'),None)
  if selected and clip is None:return
  if clip is not None and not clip['start']<=beat<clip['start']+clip['length']:return
  name=str(clip.get('pattern_id','main')) if clip else 'main'
  self.patterns.setdefault(name,[[False]*16 for _ in range(32)])
  step=pattern_step(beat,clip)
  self.pad_takes.record(self.patterns,name,index,step,velocity)
  if getattr(self,'_tick_started',None) is not None and step==pattern_step(self.playhead,clip):
   if not hasattr(self,'_pad_skip_once'):self._pad_skip_once={}
   self._pad_skip_once[(name,index,step)]=self.playhead
 def pad_take_history(self,redo=False):
  if self.recording and self.playing:
   self.status.config(text='Stop recording or playback before undoing a pad take.');return False
  changed=(self.pad_takes.redo if redo else self.pad_takes.undo)(self.patterns)
  if changed:self._pad_skip_once={}
  self.status.config(text=('Pad take '+('redone' if redo else 'undone')) if changed else 'No matching pad take to restore; later pattern edits are preserved.')
  self._refresh();return changed
 def toggle_step(self,i):
  p=self.active_pattern()[self.selected_pad];p[i]=not p[i];self._refresh()
 def active_pattern(self):
  clip=next((c for c in self.arr.clips if c['id'] in self.arr.selected and c.get('kind')=='pattern'),None)
  return self.patterns.setdefault(str(clip.get('pattern_id','main')) if clip else 'main',[[False]*16 for _ in range(32)])
 def toggle_play(self):
  self.playing=not self.playing
  if self.playing:
   self._next_tick_time=time.monotonic()
   self._count_in_remaining=16 if self.recording and getattr(self,'count_in_enabled',False) else 0
   self._count_in_active=self._count_in_remaining>0
   self.tick()
  else:
   if self.tick_id:self.root.after_cancel(self.tick_id);self.tick_id=None
   self.pad_takes.finish()
   self._pad_skip_once={}
   self._count_in_remaining=0;self._count_in_active=False;self._tick_started=None;self.engine.clear_clicks()
   self._next_tick_time=None
  self._refresh()
 def toggle_rec(self):
  self.recording=not self.recording
  if not self.recording:
   self.pad_takes.finish()
   if getattr(self,'_count_in_active',False):
    self._count_in_remaining=0;self._count_in_active=False
    if not getattr(self,'metronome_enabled',False):self.engine.clear_clicks()
  self._refresh()
 def add_labb_clip(self):
  clip=self.arr.create(self.arr.focus_track,self.playhead,4.,LABBS[self.labbs.selected].name,'labb')
  clip['labb_index']=self.labbs.selected
  clip['note_pattern']='labb-'+clip['id']
  self.notes.patterns[clip['note_pattern']]=[__import__('copy').copy(n) for n in self.notes.patterns['labb-main']]
  self.notes.armed_labb=self.labbs.selected
  self._refresh()

 def tick(self):
  self.tick_id=None
  if not self.playing:return
  remaining=getattr(self,'_count_in_remaining',0)
  if remaining:
   self._tick_started=None
   if remaining%4==0:self.engine.click(accent=remaining==16)
   self._count_in_remaining-=1
   self._refresh();self.schedule_tick()
   return
  self._count_in_active=False
  self._tick_beat=self.playhead;self._tick_started=time.monotonic()
  if getattr(self,'metronome_enabled',False) and abs(self.playhead-round(self.playhead))<1e-8:self.engine.click(accent=round(self.playhead)%4==0)
  skip={key for key,beat in getattr(self,'_pad_skip_once',{}).items() if abs(beat-self.playhead)<1e-8}
  self._pad_skip_once={}
  for p,velocity in velocity_hits_at([c for c in self.arr.clips if self.arr.track_audible(c['track'])],self.patterns,self.playhead,excluded_steps=skip):self.engine.trigger(p,velocity)
  for labb,note,vel,duration in self.notes.events_at(self.arr.clips,self.playhead,self.arr.track_audible):self.labbs.note_on(note,vel,labb,duration)
  for clip in regions_starting([c for c in self.arr.clips if self.arr.track_audible(c['track'])],self.playhead):
   try:
    with self.engine.lock:self.engine.regions.start(clip,self.bpm,seek_beats=max(0.,self.playhead-clip['start']))
   except (OSError,ValueError) as e:self.status.config(text='Audio clip error: '+str(e))
  self.playhead=advance(self.playhead,self.arr.loop_start,self.arr.loop_end,self.arr.loop_enabled)
  self.step=int(round(self.playhead*4))%16
  self._refresh()
  self.schedule_tick()
 def schedule_tick(self):
  now=time.monotonic();interval=60./self.bpm/4
  deadline=getattr(self,'_next_tick_time',None)
  deadline=now+interval if deadline is None else deadline+interval
  if deadline<now-interval:deadline=now+interval
  self._next_tick_time=deadline
  self.tick_id=self.root.after(max(1,round((deadline-now)*1000)),self.tick)
 def next_jog(self):self.jog_mode=(self.jog_mode+1)%len(self.jog_modes);self._refresh()
 def jog(self,d):
  m=self.jog_modes[self.jog_mode]
  if m=='PLAYHEAD':self.playhead=max(0,min(16,self.playhead+d*.25));self._tick_started=None
  elif m=='ZOOM':self.zoom=max(.5,min(4,self.zoom+d*.25))
  elif m=='CLIP MOVE' and self.clips:self.arr.move(d*.25)
  elif m=='CLIP LENGTH' and self.clips:self.arr.resize(self.clips[self.selected_clip]['id'],'right',d*.25)
  elif m=='SCROLL':self.playhead=max(0,min(16,self.playhead+d))
  elif m=='SLICE':self.playhead=max(0,min(16,self.playhead+d*.125))
  elif m=='LOOP START':self.arr_loop('start',d*.25)
  elif m=='LOOP END':self.arr_loop('end',d*.25)
  elif m=='LOOP MOVE':self.arr_loop('body',d*.25)
  self._refresh()
 def command(self,name,velocity=1.0):
  if name.startswith('BANK PAD '):self.pad(int(name[9:])-1,velocity)
  elif name.startswith('PAD '):self.trigger_absolute_pad(int(name[4:])-1,velocity)
  elif name in ('TAKE UNDO','TAKE REDO'):self.pad_take_history(redo=name=='TAKE REDO')
  elif name=='METRONOME TOGGLE':
   self.metronome_enabled=not self.metronome_enabled
   if not self.metronome_enabled and not self._count_in_remaining:self.engine.clear_clicks()
   self._refresh()
  elif name=='COUNT IN TOGGLE':
   self.count_in_enabled=not self.count_in_enabled
   if not self.count_in_enabled:
    self._count_in_remaining=0;self._count_in_active=False
    if not self.metronome_enabled:self.engine.clear_clicks()
   self._refresh()
  elif name.startswith('SURFACE KEY '):self.surface_context.key(int(name.split()[-1])-1)
  elif name.startswith('SURFACE KNOB '):
   parts=name.split();self.surface_context.knob(int(parts[2])-1,1 if parts[3]=='+' else -1)
  elif name.startswith('SURFACE '):self.surface_context.set_page(name[8:]);self._refresh()
  elif name in ('BROWSE SOUNDS','EDIT SOUND'):self.open_sound_browser('BROWSE' if name=='BROWSE SOUNDS' else 'SOUND')
  elif name=='EDIT FX':self.open_mix_rack()
  elif name in ('SOUND PREV','SOUND NEXT'):self.surface_context.choose_sound(-1 if name.endswith('PREV') else 1)
  elif name.startswith('FX ADD '):self.mix_rack.add(name[7:]);self.surface_context.fx_index=len(self.mix_rack.modules)-1;self.sync_fx_window();self._refresh()
  elif name in ('FX PREV','FX NEXT'):
   if self.mix_rack.modules:self.surface_context.fx_index=(self.surface_context.fx_index+(-1 if name.endswith('PREV') else 1))%len(self.mix_rack.modules)
  elif name=='FX BYPASS':
   if self.mix_rack.modules:
    i=self.surface_context.fx_index%len(self.mix_rack.modules);self.mix_rack.bypass(i,self.mix_rack.modules[i].enabled);self.sync_fx_window()
  elif name.startswith('RANGE '):self.range_command(name[6:])
  elif name=='RESTART':self.playhead=0.;self.step=0;self._tick_started=None;self._refresh()
  elif name=='LOOP TOGGLE':self.arr.loop_enabled=not self.arr.loop_enabled;self._refresh()
  elif name=='LOOP ALL':
   self.arr.checkpoint();self.arr.loop_start=0.;self.arr.loop_end=max(.25,max((c['start']+c['length'] for c in self.arr.clips),default=16.));self._refresh()
  elif name=='LOOP FOCUS':self.hardware_edit.set_operation('LOOP MOVE');self.status.config(text=self.hardware_edit.describe());self._refresh()
  elif name=='PLAY/STOP':self.toggle_play()
  elif name=='RECORD':self.toggle_rec()
  elif name=='TRACK MUTE':self.arr.toggle_track_mute(self.arr.focus_track);self._refresh()
  elif name=='TRACK SOLO':self.arr.toggle_track_solo(self.arr.focus_track);self._refresh()
  elif name=='SUITE NEXT':self.labbs.selected=(self.labbs.selected+1)%22
  elif name=='SUITE PREV':self.labbs.selected=(self.labbs.selected-1)%22
  elif name=='SUITE CLICK':self.open_labbs()
  elif name=='SUITE BROWSER':self.open_labbs()
  elif name=='LABB NEXT':self.labbs.selected=(self.labbs.selected+1)%22
  elif name=='LABB PREV':self.labbs.selected=(self.labbs.selected-1)%22
  elif name=='LABB PLAY':self.labbs.note_on(48)
  elif name=='LABB BROWSER':self.open_labbs()
  elif name=='LABB ARM':self.notes.armed_labb=self.labbs.selected;self.status.config(text='Armed '+LABBS[self.labbs.selected].name)
  elif name=='LABB NOTE +':self.note_pitch=min(127,self.note_pitch+1);self.status.config(text=f'LABB note {self.note_pitch}')
  elif name=='LABB NOTE -':self.note_pitch=max(0,self.note_pitch-1);self.status.config(text=f'LABB note {self.note_pitch}')
  elif name=='LABB NOTE PLAY':self.labbs.note_on(self.note_pitch,labb=self.notes.armed_labb)
  elif name=='LABB CLIP':self.add_labb_clip()
  elif name.startswith('SUITE OPEN'):
   parts=name.split()
   if len(parts)==3:self.suites.select(int(parts[2])-1)
   self._suite_open()
  elif name=='PAGE NEXT':self.set_page(self.page+1)
  elif name=='PAGE PREV':self.set_page(self.page-1)
  elif name=='BANK NEXT':self.set_bank(self.bank+1)
  elif name=='BANK PREV':self.set_bank(self.bank-1)
  elif name=='JOG CLICK':self.status.config(text=self.hardware_edit.click());self._refresh()
  elif name=='JOG BACK':self.status.config(text=self.hardware_edit.cancel());self._refresh()
  elif name=='JOG SHIFT':self.hardware_edit.shift=not self.hardware_edit.shift;self.status.config(text=self.hardware_edit.describe())
  elif name.startswith('EDIT:'):self.status.config(text=self.hardware_edit.set_operation(name[5:]));self._refresh()
  elif name=='HW JOG +':self.status.config(text=self.hardware_edit.rotate(1));self._refresh()
  elif name=='HW JOG -':self.status.config(text=self.hardware_edit.rotate(-1));self._refresh()
  elif name=='JOG +':self.jog(1)
  elif name=='JOG -':self.jog(-1)
  elif name=='JOG MODE':self.next_jog()
  elif name=='UNDO':self.arr.undo();self.clips=self.arr.clips;self._refresh()
  elif name=='REDO':self.arr.redo();self.clips=self.arr.clips;self._refresh()
  elif name.startswith('MODE '):self.set_edit_mode(name[5:])
  elif name=='COPY':self.arr.copy();self.status.config(text='Copied selected containers')
  elif name in ('PASTE','PASTE MERGE'):self.arr.paste(self.playhead,name=='PASTE MERGE');self._refresh()
  elif name=='SPLIT':self.split()
  elif name.startswith('LOOP '):
   _,edge,sign=name.split();self.arr_loop({'START':'start','END':'end','MOVE':'body'}[edge],-.25 if sign=='-' else .25)
 def range_command(self,operation):
  editor=self.range_editor
  if operation=='COPY':result=editor.copy()
  elif operation=='CUT':result=editor.delete(cut=True)
  elif operation=='DELETE':result=editor.delete()
  elif operation=='PASTE':result=editor.paste(self.playhead)
  elif operation=='DUPLICATE':result=editor.duplicate()
  elif operation=='INSERT':result=editor.duplicate(insert=True)
  else:raise ValueError('Unknown range operation')
  self.clips=self.arr.clips;self._refresh();self.status.config(text=f'{self.arr.mode} RANGE {operation}: '+str(len(result) if isinstance(result,list) else result)+' region(s)')
 def _suite_update(self):
  self.status.config(text='SUITE '+str(self.suites.focus+1)+'/22: '+self.suites.current.name+' ['+self.suites.current.implementation+']')
  if hasattr(self,'suite_window') and self.suite_window.win.winfo_exists():self.suite_window.refresh()
 def _suite_open(self):
  name=self.suites.current.name
  page={'Track City':0,'Chop Labb Pro':1,'Drums & Breaks':2,'Sample Labb':1,'Master Mixer':4,'MIDI Command Center':5,'Prefs':5}.get(name)
  if page is not None:self.set_page(page)
  self._suite_update()
 def set_edit_mode(self,mode):
  self.arr.set_mode(mode);self.status.config(text='TRACK CITY / '+mode);self._refresh()
 def arr_loop(self,edge,delta):self.arr.loop_edit(edge,delta);self._refresh()
 def toggle_snap(self):self.arr.snap=0 if self.arr.snap else .25;self.status.config(text='Snap '+('OFF' if not self.arr.snap else '1/16'));self._refresh()
 def add_clip(self):
  import uuid, copy
  source=self.active_pattern()
  c=self.arr.create(self.arr.focus_track,self.playhead)
  pid=uuid.uuid4().hex[:10];c['pattern_id']=pid;self.patterns[pid]=copy.deepcopy(source)
  self._refresh()
 def add_audio_clip(self):
  path=filedialog.askopenfilename(title='Import audio region',filetypes=[('PCM WAV','*.wav')])
  if not path:return
  try:
   with self.engine.lock:
    absolute=self.engine.regions.preload(path)
    samples,rate=self.engine.regions.sources[absolute]
   beats=max(.25,len(samples)/rate*self.bpm/60.)
   clip=self.arr.create(self.arr.focus_track,self.playhead,beats,Path(path).stem,'audio')
   clip.update(path=absolute,gain=1.,fade_in=0.,fade_out=0.)
   self._refresh()
  except Exception as e:messagebox.showerror('Audio import',str(e))
 def duplicate(self):self.arr.duplicate();self._refresh()
 def split(self):self.arr.split(self.playhead);self._refresh()
 def delete_clip(self):self.arr.delete();self._refresh()
 def right_click(self,event):
  self.playhead=max(0,(event.x-90)/(36*self.zoom));self.split()
 def select_clip(self,event):
  x,y=event.x,event.y;scale=36*self.zoom
  if 16<=y<=29:
   a=90+self.arr.loop_start*scale;b=90+self.arr.loop_end*scale
   edge='start' if abs(x-a)<9 else 'end' if abs(x-b)<9 else 'body' if a<x<b else None
   if edge:self.drag={'type':'loop','edge':edge,'x':x,'initial':self.arr.snapshot(),'checkpoint':False};return
  hit=None;edge='body'
  for i,c in reversed(list(enumerate(self.clips))):
   a=90+c['start']*scale;b=a+c['length']*scale;top=31+c['track']*43
   if a<=x<=b and top<=y<=top+31:
    hit=i;edge='left' if x-a<8 else 'right' if b-x<8 else 'body';break
  if hit is not None:
   self.selected_clip=hit;c=self.clips[hit]
   if self.arr.mode=='TRK':self.arr.select([z['id'] for z in self.clips if z['track']==c['track']])
   elif c['id'] not in self.arr.selected:self.arr.select([c['id']],add=bool(event.state&0x0001))
   self.drag={'type':'clip','edge':edge,'id':c['id'],'x':x,'y':y,'initial':self.arr.snapshot(),'checkpoint':False}
  else:
   self.drag={'type':'marquee','x':x,'y':y};self.marquee_start=(x,y)
   if self.arr.mode!='MRQ':self.arr.select([])
  self._refresh()
 def drag_clip(self,event):
  if not self.drag:return
  d=self.drag;scale=36*self.zoom
  if d['type']=='marquee':
   x0,y0=d['x'],d['y'];t0=max(0,(x0-90)/scale);t1=max(0,(event.x-90)/scale)
   tr0=max(0,min(3,int((y0-28)//43)));tr1=max(0,min(3,int((event.y-28)//43)))
   self.arr.marquee(t0,t1,tr0,tr1);self.marquee_start=(x0,y0,event.x,event.y)
  else:
   delta=self.arr.quant((event.x-d['x'])/scale)
   if d['type']=='loop':
    if not d['checkpoint'] and delta:self.arr.checkpoint();d['checkpoint']=True
    if d['checkpoint']:
     before=d['initial'];self.arr.loop_start=before[3];self.arr.loop_end=before[4]
     if d['edge']=='start':self.arr.loop_start=max(0,min(before[3]+delta,before[4]-.25))
     elif d['edge']=='end':self.arr.loop_end=max(before[3]+.25,before[4]+delta)
     else:delta=max(-before[3],delta);self.arr.loop_start+=delta;self.arr.loop_end+=delta
   elif d['type']=='clip':
    track_delta=round((event.y-d['y'])/43)
    if (delta or track_delta) and not d['checkpoint']:self.arr.checkpoint();d['checkpoint']=True
    if d['checkpoint']:
     before=d['initial'];self.arr.clips=__import__('copy').deepcopy(before[0]);self.clips=self.arr.clips
     c=next(z for z in self.clips if z['id']==d['id'])
     if d['edge']=='body':
      targets=[z for z in self.clips if z['id'] in self.arr.selected]
      delta=max(delta,-min(z['start'] for z in targets));track_delta=max(track_delta,-min(z['track'] for z in targets))
      for z in targets:z['start']+=delta;z['track']+=track_delta
     elif d['edge']=='left':
      delta=max(-c['start'],min(delta,c['length']-.25));c['start']+=delta;c['length']-=delta;c['offset']+=delta
     else:c['length']=max(.25,c['length']+delta)
  self._refresh()
 def release_clip(self,event):self.drag=None;self.marquee_start=None;self._refresh()
 def load_sample(self):
  p=filedialog.askopenfilename(filetypes=[('16-bit PCM WAV','*.wav')]);
  if p:
   try:self.engine.load(self.selected_pad,p);self.status.config(text=f'Loaded {Path(p).name} to pad {self.selected_pad+1}')
   except Exception as e:messagebox.showerror('WAV load',str(e))
   self._refresh()
 def scan_audio(self):
  selected=self.audio_device.get()
  try:
   import sounddevice as sd
   devices=sd.query_devices();self.audio_choices=[('System default',None)]+[(str(i)+'  '+d['name'],i) for i,d in enumerate(devices) if d['max_output_channels']>=2]
   names=[v[0] for v in self.audio_choices];self.audio_device['values']=names
   if selected in names:self.audio_device.set(selected)
   else:self.audio_device.current(0)
   return self.audio_choices
  except Exception as e:
   self.audio_choices=[];self.audio_device['values']=[];self.audio_device.set('');self.status.config(text='Audio scan: '+str(e));return []
 def start_audio(self):
  try:
   i=self.audio_device.current();device=self.audio_choices[i][1] if i>=0 else None;self.engine.start(device);self.status.config(text='Audio started; '+self.audio_device.get())
   return True
  except Exception as e:messagebox.showerror('Audio',str(e));return False
 def scan_midi(self):
  selected=self.midi_device.get()
  try:
   import mido
   names=list(mido.get_input_names());self.midi_device['values']=names
   if selected in names:self.midi_device.set(selected)
   elif names:
    preferred=next((name for name in names if 'maschine' in name.casefold() and 'studio' in name.casefold()),names[0]);self.midi_device.set(preferred)
   else:self.midi_device.set('')
   self.hardware_status=f'{len(names)} MIDI input(s) found' if not self.midi_port else self.hardware_status
   if not names:self.status.config(text='No MIDI inputs found. Check Maschine Studio drivers and Controller Editor MIDI mode.')
   return names
  except Exception as exc:
   self.midi_device['values']=[];self.midi_device.set('');self.hardware_status='MIDI backend unavailable: '+str(exc);self.status.config(text=self.hardware_status)
   return []
 def close_midi(self):
  port=self.midi_port;self.midi_port=None;self.midi_connected_name=None
  try:
   if port is not None:port.close()
  finally:
   self.street_dispatch.panic();self._drain_midi(2048)
   self.hardware_learn=None;self.hardware_status='MIDI disconnected';self.status.config(text=self.hardware_status)
 def open_midi(self):
  name=self.midi_device.get()
  if not name:
   self.hardware_status='Select a MIDI input first';self.status.config(text=self.hardware_status);return False
  try:
   import mido
   self.close_midi()
   self.midi_port=mido.open_input(name,callback=self._enqueue_midi);self.midi_connected_name=name
   self.hardware_status='MIDI connected: '+name;self.status.config(text=self.hardware_status)
   return True
  except Exception as exc:
   self.midi_port=None;self.hardware_status='MIDI connection failed: '+str(exc);self.status.config(text=self.hardware_status)
   messagebox.showerror('MIDI',self.hardware_status);return False
 def arm_hardware_learn(self,command,mode,control=None):
  # Validate mode before arming; addresses come from the real incoming message.
  MidiControlRouter().bind('cc',0,0,command,mode)
  self.learn=None;self.last_hardware_learn=None;self.hardware_learn={'command':command,'mode':mode}
  if control is not None:self.hardware_learn['control']=control
  self.hardware_status='LEARN ARMED: '+command;self.status.config(text=self.hardware_status)
 def arm_pad_learn(self):
  staged=MidiControlRouter();staged.deserialize(self.hardware_midi.serialize())
  self.learn=None;self.last_hardware_learn=None
  self.hardware_learn={'command':'BANK PAD 1','mode':'button','control':'PAD 1','batch':True,'index':0,'staged':staged,'seen':set(),'legacy':[]}
  self.hardware_status='PAD LEARN 1/16 — press physical pad 1 (existing map is preserved until complete)';self.status.config(text=self.hardware_status)
 def _learn_hardware_message(self,message):
  pending=getattr(self,'hardware_learn',None)
  if not pending:return False
  typ=getattr(message,'type',None)
  if typ not in ('note_on','control_change'):return False
  value=getattr(message,'value',None) if typ=='control_change' else getattr(message,'velocity',None)
  if not isinstance(value,int) or not 0<=value<=127:return False
  if typ=='note_on' and value==0:return False
  if pending['mode']=='button' and value==0:return False
  if pending['mode']!='button' and typ!='control_change':return False
  kind='cc' if typ=='control_change' else 'note';number=getattr(message,'control',None) if kind=='cc' else getattr(message,'note',None)
  channel=getattr(message,'channel',None)
  if pending.get('batch'):
   address=f'{kind}:{channel}:{number}'
   if address in pending['seen']:
    self.hardware_status=f"Already captured {address} — press physical pad {pending['index']+1}";self.status.config(text=self.hardware_status);return True
   pending['staged'].bind(kind,channel,number,pending['command'],pending['mode'],pending['control'])
   pending['seen'].add(address);pending['legacy'].append(f'{typ}:{channel}:{number}');pending['index']+=1
   if pending['index']==16:
    self.hardware_midi.deserialize(pending['staged'].serialize())
    for key in pending['legacy']:self.mapping.pop(key,None)
    self.hardware_learn=None;self.last_hardware_learn={'kind':kind,'channel':channel,'number':number,'command':'BANK PAD 16','mode':'button','control':'PAD 16'}
    self.hardware_status='PAD LEARN COMPLETE — all 16 physical pads mapped across banks A/B'
   else:
    n=pending['index']+1;pending['command']=f'BANK PAD {n}';pending['control']=f'PAD {n}'
    self.hardware_status=f'PAD LEARN {n}/16 — press physical pad {n}'
   self.status.config(text=self.hardware_status);return True
  self.hardware_midi.bind(kind,channel,number,pending['command'],pending['mode'],pending.get('control'))
  # A newly learned address supersedes legacy learn at that address.
  self.mapping.pop(f'{typ}:{channel}:{number}',None)
  self.last_hardware_learn={'kind':kind,'channel':channel,'number':number,**pending}
  self.hardware_learn=None
  self.hardware_status=f"LEARNED {kind}:{channel}:{number} → {pending['command']} ({pending['mode']})"
  self.status.config(text=self.hardware_status)
  return True
 def _enqueue_midi(self,message):
  """Nonblocking hardware callback: never stall the MIDI driver thread."""
  try:self.events.put_nowait(message)
  except queue.Full:self.midi_dropped+=1
 def _drain_midi(self,limit=256):
  """Bound main-thread work so a MIDI flood cannot freeze Tk's event loop."""
  messages=[]
  for _ in range(limit):
   try:messages.append(self.events.get_nowait())
   except queue.Empty:break
  return messages
 def arm_learn(self):self.hardware_learn=None;self.learn=self.midi_cmd.get();self.status.config(text='MIDI LEARN armed for '+self.learn)
 def _midi_note_on(self,note,velocity):
  if any(c['id'] in self.arr.selected and c.get('kind')=='labb' for c in self.arr.clips):
   self.labbs.note_on(note,velocity,self.notes.armed_labb)
   if self.recording and not getattr(self,'_count_in_active',False):
    focused=next((c for c in self.arr.clips if c['id'] in self.arr.selected and c.get('kind')=='labb'),None)
    if focused:self.notes.add(focused.get('note_pattern','labb-main'),(self.playhead-focused['start']+focused.get('offset',0))%4,note,velocity)
  elif 36 <= note <= 67:self.trigger_absolute_pad(note-36,velocity)
 def _midi_pad_command(self,command,velocity):
  self.command(command,velocity=velocity)
 def _midi_note_off(self,note):
  self.labbs.note_off(note,self.notes.armed_labb)
 def _poll(self):
  try:
   for m in self._drain_midi():
    if hasattr(self,'midi_activity'):self.midi_activity.record(m)
    if self._learn_hardware_message(m):continue
    # Legacy MIDI Learn is deliberately processed before dispatch.
    kind='note' if m.type in ('note_on','note_off') else 'cc' if m.type=='control_change' else None
    number=getattr(m,'note',None) if kind=='note' else getattr(m,'control',None)
    key=f'{m.type}:{getattr(m,"channel",0)}:{number}'
    if self.learn and m.type in ('note_on','control_change') and getattr(m,'velocity',getattr(m,'value',0))>0:
     self.mapping[key]=self.learn;self.status.config(text=f'Learned {key} → {self.learn}');self.learn=None
     continue
    if key in self.mapping and m.type in ('note_on','control_change'):
     if getattr(m,'velocity',getattr(m,'value',0))>0:
      action=self.mapping[key]
      if m.type=='note_on' and action.startswith(('PAD ','BANK PAD ')):self._midi_pad_command(action,m.velocity/127.)
      else:self.command(action)
     continue
    if m.type=='note_off' and f'note_on:{getattr(m,"channel",0)}:{number}' in self.mapping:continue
    self.street_dispatch.receive(self.midi_device.get() or 'unknown',m,position=self.playhead,playing=self.playing)
  except Exception as exc:
   self.status.config(text='MIDI processing error: '+str(exc))
  if self.midi_dropped:
   self.status.config(text=f'MIDI overload: {self.midi_dropped} messages dropped; check controller rate')
   self.midi_dropped=0
  self.root.after(40,self._poll)
 def _refresh(self):
  for i,b in enumerate(self.pad_buttons):
   idx=self.bank*16+i;sample=self.engine.samples[idx];name=sample[2][:10] if sample else 'EMPTY'
   b.config(text=f'{idx+1:02}  {name}',bg=C['orange'] if idx==self.selected_pad else C['purple'] if sample else C['burgundy'])
  for i,b in enumerate(self.step_buttons):b.config(bg=C['mint'] if self.active_pattern()[self.selected_pad][i] else C['orange'] if i==self.step else C['bg'],fg=C['bg'] if self.active_pattern()[self.selected_pad][i] else C['cream'])
  self.clips=self.arr.clips
  self.jog_label.config(text=f'{self.arr.mode}  |  JOG: {self.jog_modes[self.jog_mode]}')
  self.draw_arranger();self.draw_screens()
 def draw_arranger(self):
  c=self.arranger;c.delete('all');scale=36*self.zoom
  for i,name in enumerate(['DRUMS','CHOPS','BASS','KEYS']):
   y=28+i*43;c.create_rectangle(4,y,88,y+38,fill=C['burgundy'],outline='');c.create_text(45,y+18,text=name,fill=C['cream'],font=('Segoe UI',10,'bold'))
   c.create_rectangle(90,y,770,y+38,fill='#302a36',outline='#45394b')
  for i in range(33):
   x=90+i*scale;c.create_line(x,29,x,205,fill='#56465a');c.create_text(x+3,12,text=str(i+1),anchor='w',fill=C['dim'])
  ls=90+self.arr.loop_start*scale;le=90+self.arr.loop_end*scale
  c.create_rectangle(ls,18,le,27,fill=C['mint'],outline=C['cream']);c.create_polygon(ls,17,ls+10,17,ls,29,fill=C['orange']);c.create_polygon(le,17,le-10,17,le,29,fill=C['orange'])
  for i,clip in enumerate(self.clips):
   x=90+clip['start']*scale;y=31+clip['track']*43;w=clip['length']*scale
   c.create_rectangle(x,y,x+w,y+31,fill=[C['orange'],C['mint'],C['purple'],C['burgundy']][clip['track']%4],outline=C['cream'] if clip['id'] in self.arr.selected else '',width=2)
   c.create_text(x+6,y+15,anchor='w',text=('♪ ' if clip.get('kind')=='audio' else '♫ ' if clip.get('kind')=='labb' else '')+clip['name'][:16],fill=C['bg'] if clip['track']==1 else C['cream'])
  if self.marquee_start and len(self.marquee_start)==4:
   x0,y0,x1,y1=self.marquee_start;c.create_rectangle(x0,y0,x1,y1,outline=C['mint'],dash=(3,3))
  c.create_line(90+self.playhead*scale,28,90+self.playhead*scale,205,fill=C['cream'],width=2)
 def draw_screens(self):
  for s in (self.screen1,self.screen2):s.delete('all');s.create_rectangle(0,0,204,145,fill='#1d1923',outline='')
  a,b=self.screen1,self.screen2;page=PAGES[self.page]
  a.create_text(9,12,anchor='w',text='TOOLBOXX  /  '+page,fill=C['mint'],font=('Segoe UI',9,'bold'))
  b.create_text(9,12,anchor='w',text='STUDIO  /  '+page,fill=C['orange'],font=('Segoe UI',9,'bold'))
  if page=='TRACK CITY':
   for i,name in enumerate(['DRUM','CHOP','BASS','KEYS']):
    y=28+i*25;a.create_text(8,y+8,anchor='w',text=name,fill=C['cream'],font=('Segoe UI',8));a.create_rectangle(50,y,195,y+19,fill='#302737',outline='')
   for i,c in enumerate(self.clips):
    y=28+c['track']*25;a.create_rectangle(51+c['start']*8,y+2,51+(c['start']+c['length'])*8,y+17,fill=C['orange'] if i==self.selected_clip else C['purple'],outline='')
   b.create_text(15,36,anchor='w',text=f'CLIPS  {len(self.clips)}',fill=C['cream']);b.create_text(15,61,anchor='w',text=f'PLAYHEAD  {self.playhead:.2f}',fill=C['mint']);b.create_text(15,85,anchor='w',text=f'ZOOM  {self.zoom:.2f}x',fill=C['cream']);b.create_text(15,109,anchor='w',text=self.arr.mode+'  JOG '+self.jog_modes[self.jog_mode],fill=C['orange'],font=('Segoe UI',8))
  elif page=='CHOP LABB':
   for i in range(120):
    x=8+i*1.55;h=abs(math.sin(i*.27)*math.cos(i*.061))*38+3;a.create_line(x,81-h,x,81+h,fill=C['orange'])
   for x in (36,78,122,165):a.create_line(x,37,x,121,fill=C['mint'])
   b.create_text(12,48,anchor='w',text='SLICE EDIT  /  16',fill=C['cream']);b.create_text(12,80,anchor='w',text='JOG = SLICE / ZOOM',fill=C['mint'],font=('Segoe UI',8))
  elif page=='MIDI MAP':
   a.create_text(10,38,anchor='w',text='STUDIO CONTROL MAP',fill=C['cream']);a.create_text(10,63,anchor='w',text=f'MAPPED INPUTS  {len(self.mapping)}',fill=C['mint']);a.create_text(10,90,anchor='w',text='SELECT + LEARN',fill=C['orange'])
   b.create_text(10,40,anchor='w',text='JOG / PADS / KEYS',fill=C['cream']);b.create_text(10,70,anchor='w',text='HARDWARE IMAGE: NEXT',fill=C['mint'],font=('Segoe UI',8))
  else:
   a.create_text(12,50,anchor='w',text=page,fill=C['cream']);a.create_text(12,78,anchor='w',text='PAGE NAV ACTIVE',fill=C['mint']);b.create_text(12,50,anchor='w',text=f'BANK {"AB"[self.bank]}  /  PAD {self.selected_pad+1}',fill=C['cream']);b.create_text(12,78,anchor='w',text='CONTEXT CONTROLS',fill=C['orange'])
 def export_track_city(self):
  path=filedialog.asksaveasfilename(title='Bounce Track City to WAV',defaultextension='.wav',filetypes=[('Stereo WAV','*.wav')])
  if not path:return
  try:
   from track_city_bounce import bounce_track_city
   result=bounce_track_city(self.engine,self.arr,self.patterns,self.bpm,path,note_lane=self.notes)
   self.status.config(text='TRACK CITY WAV bounced: '+str(path))
  except Exception as exc:messagebox.showerror('Track City bounce',str(exc))
 def save(self):
  path=filedialog.asksaveasfilename(defaultextension='.tbx.json',filetypes=[('TOOLBOXX Project','*.json')])
  if not path:return
  try:
   from project_io import save_project
   save_project(self,path);self.status.config(text='Saved '+path)
  except Exception as exc:messagebox.showerror('Project save',str(exc))
 def load(self):
  path=filedialog.askopenfilename(filetypes=[('TOOLBOXX Project','*.json')])
  if not path:return
  try:
   from project_io import load_project
   legacy=load_project(self,path);self._refresh();self.sync_fx_window()
   if hasattr(self,'sound_browser_window') and self.sound_browser_window.win.winfo_exists():self.sound_browser_window.refresh()
   if hasattr(self,'cookup_window') and self.cookup_window.win.winfo_exists():self.cookup_window.refresh()
   self.status.config(text='Loaded project'+('; legacy file has no saved pad audio paths' if legacy else ' and audio sources'))
  except Exception as exc:messagebox.showerror('Project load',str(exc))
 def close(self):
  if getattr(self,'_closing',False):return
  self._closing=True
  self.playing=False
  if self.tick_id:
   try:self.root.after_cancel(self.tick_id)
   except tk.TclError:pass
   self.tick_id=None
  try:self.close_midi()
  except Exception:pass
  try:self.engine.stop()
  finally:self.root.destroy()

if __name__=='__main__':root=tk.Tk();App(root);root.mainloop()
