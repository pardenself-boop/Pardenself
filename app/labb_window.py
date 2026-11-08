"""22 LABBS instrument rack: clickable playable notes and shared master output."""
import tkinter as tk
from labb_engine import LABBS
from street_patch_vault import StreetPatchVault
BG='#100e14';PANEL='#201821';MINT='#8ce3c9';ORANGE='#e17a35';CREAM='#f3e5c9';PURPLE='#9652ca'
class LabbWindow:
 def __init__(self,app):
  self.app=app;self.win=tk.Toplevel(app.root);self.win.title('TOOLBOXX / 22 LABBS / ONE MASTER');self.win.geometry('1150x730');self.win.configure(bg=BG)
  self.list=tk.Listbox(self.win,bg=PANEL,fg=CREAM,selectbackground='#81374f',font=('Segoe UI',11),width=28,exportselection=False)
  self.list.pack(side='left',fill='y',padx=10,pady=10)
  for i,p in enumerate(LABBS):self.list.insert('end',f'{i+1:02}  {p.name}')
  self.list.bind('<<ListboxSelect>>',self.select)
  self.center=tk.Frame(self.win,bg=BG);self.center.pack(side='left',fill='both',expand=True,padx=15,pady=10)
  self.title=tk.Label(self.center,text='',bg=BG,fg=MINT,font=('Segoe UI',23,'bold'));self.title.pack(anchor='w')
  tk.Label(self.center,text='PLAYABLE LABB PATCH  •  22 SHARED VOICE ROUTES  •  MASTER OUTPUT',bg=BG,fg=CREAM).pack(anchor='w',pady=6)
  self.visual=tk.Canvas(self.center,bg=PANEL,height=180,highlightthickness=0);self.visual.pack(fill='x',pady=12)
  self.visual.bind('<Configure>',lambda e:self.draw())
  row=tk.Frame(self.center,bg=BG);row.pack(fill='x')
  for i,n in enumerate((36,38,40,41,43,45,47,48,50,52,53,55,57,59,60,62)):
   tk.Button(row,text=str(n),bg=[PURPLE,ORANGE,MINT][i%3],fg=BG,command=lambda n=n:self.play(n),width=3).grid(row=i//8,column=i%8,padx=4,pady=4)
  self.note=tk.Label(self.center,text='Click any note to audition through the shared engine',bg=BG,fg=CREAM);self.note.pack(anchor='w',pady=10)
  self.level=tk.Scale(self.center,from_=0,to=100,orient='horizontal',label='LABB LEVEL',bg=BG,fg=CREAM,highlightthickness=0,command=self.set_level);self.level.pack(fill='x')
  controls=tk.Frame(self.center,bg=BG);controls.pack(fill='x',pady=6)
  self.mute=tk.Button(controls,text='MUTE',command=self.toggle_mute,bg='#81374f',fg=CREAM);self.mute.pack(side='left',padx=3)
  self.solo=tk.Button(controls,text='SOLO',command=self.toggle_solo,bg=PURPLE,fg=CREAM);self.solo.pack(side='left',padx=3)
  tk.Button(controls,text='START AUDIO',command=self.start_audio,bg=ORANGE,fg=BG).pack(side='left',padx=3)
  tk.Label(self.center,text='MASTER OUTPUT • DC BLOCK • SOFT CLIP • PEAK CEILING',bg=BG,fg=MINT,font=('Segoe UI',12,'bold')).pack(anchor='w',pady=(20,4))
  self.drive=self.slider('DRIVE',50,lambda v:setattr(self.app.labbs.master,'drive',.5+float(v)/50))
  self.gain=self.slider('OUTPUT GAIN',80,lambda v:setattr(self.app.labbs.master,'gain',float(v)/100))
  self.patch_vault=StreetPatchVault()
  preset_row=tk.Frame(self.center,bg=BG);preset_row.pack(fill='x',pady=3)
  tk.Label(preset_row,text='PATCH MEMORY',bg=BG,fg=MINT).pack(side='left')
  self.preset_name=tk.Entry(preset_row,width=18,bg=PANEL,fg=CREAM,insertbackground=CREAM)
  self.preset_name.insert(0,'My Street Patch');self.preset_name.pack(side='left',padx=5)
  tk.Button(preset_row,text='STORE',command=self.store_patch,bg=PURPLE,fg=CREAM).pack(side='left',padx=3)
  tk.Button(preset_row,text='RECALL',command=self.recall_patch,bg=PURPLE,fg=CREAM).pack(side='left',padx=3)
  tk.Button(preset_row,text='ALL NOTES OFF',command=self.panic,bg='#81374f',fg=CREAM).pack(side='left',padx=12)
  self._last_selected=self.app.labbs.selected
  self.peak=tk.Label(self.center,text='MASTER PEAK: 0.000',bg=BG,fg=CREAM);self.peak.pack(anchor='w',pady=8)
  self.advanced=tk.LabelFrame(self.center,text='ADVANCED LABB ENGINE  •  MIDI / ENVELOPE / FILTER / DRIVE',bg=PANEL,fg=MINT,font=('Segoe UI',11,'bold'))
  self.advanced.pack(fill='x',pady=8)
  self.advanced_scales={}
  for col,(name,lo,hi) in enumerate((('attack',.001,2),('decay',.005,3),('sustain',0,1),('release',.005,4),('cutoff',.015,.98),('resonance',0,1),('drive',0,1),('width',0,1))):
   scale=tk.Scale(self.advanced,from_=0,to=100,resolution=1,orient='horizontal',label=name.upper(),bg=PANEL,fg=CREAM,highlightthickness=0,length=150,command=lambda value,k=name,lo=lo,hi=hi:self.param_changed(k,lo+(hi-lo)*float(value)/100))
   scale.grid(row=col//4,column=col%4,padx=4,pady=2,sticky='ew');self.advanced_scales[name]=(scale,lo,hi)
  midirow=tk.Frame(self.advanced,bg=PANEL);midirow.grid(row=2,column=0,columnspan=4,sticky='w')
  tk.Label(midirow,text='MIDI INPUT CHANNEL (0 = OMNI / UNASSIGNED)',bg=PANEL,fg=CREAM).pack(side='left')
  self.channel=tk.Spinbox(midirow,from_=0,to=16,width=4,command=self.set_channel);self.channel.pack(side='left',padx=8)
  self.channel.bind('<Return>',lambda e:self.set_channel());self.channel.bind('<FocusOut>',lambda e:self.set_channel())
  tk.Button(midirow,text='OPEN ADVANCED MIDI NOTE EDITOR',command=self.open_note_editor,bg=PURPLE,fg=CREAM).pack(side='left',padx=10)
  self.list.selection_set(self.app.labbs.selected);self.refresh();self.win.after(150,self.poll)
 def store_patch(self):
  i=self.app.labbs.selected;name=self.preset_name.get().strip()
  try:
   path=self.patch_vault.save(self.app.labbs,i,name)
   self.note.config(text=f'SAVED TO DISK: {path.name} / {LABBS[i].name}')
  except (OSError,ValueError) as exc:self.note.config(text=f'PATCH SAVE ERROR: {exc}')
 def recall_patch(self):
  i=self.app.labbs.selected;name=self.preset_name.get().strip()
  try:
   self.patch_vault.load(self.app.labbs,i,name)
   self.refresh();self.note.config(text=f'RECALLED FROM DISK: {name} / {LABBS[i].name}')
  except (OSError,ValueError) as exc:self.note.config(text=f'PATCH RECALL ERROR: {exc}')
 def panic(self):
  self.app.labbs.all_notes_off();self.note.config(text='ALL NOTES RELEASED')
 def param_changed(self,key,value):
  if getattr(self,'loading_params',False):return
  self.app.labbs.set_parameter(self.app.labbs.selected,key,value)
 def set_channel(self):
  try:self.app.labbs.midi_channels[self.app.labbs.selected]=max(0,min(16,int(self.channel.get())))
  except ValueError:pass
 def open_note_editor(self):
  from advanced_midi_window import AdvancedMidiWindow
  AdvancedMidiWindow(self.app)
 def slider(self,name,initial,callback):
  s=tk.Scale(self.center,from_=0,to=100,orient='horizontal',label=name,bg=BG,fg=CREAM,highlightthickness=0,command=callback);s.set(initial);s.pack(fill='x');return s
 def select(self,e=None):
  sel=self.list.curselection()
  if sel:self.app.labbs.selected=sel[0];self.refresh()
 def play(self,n):
  self.app.labbs.note_on(n);self.note.config(text=f'NOTE {n} → {LABBS[self.app.labbs.selected].name}')
 def set_level(self,v):self.app.labbs.volume[self.app.labbs.selected]=float(v)/100
 def toggle_mute(self):
  i=self.app.labbs.selected;self.app.labbs.mute[i]=not self.app.labbs.mute[i];self.refresh()
 def toggle_solo(self):
  i=self.app.labbs.selected;self.app.labbs.solo[i]=not self.app.labbs.solo[i];self.refresh()
 def start_audio(self):
  try:self.app.start_audio()
  except Exception as e:self.note.config(text=str(e))
 def draw(self):
  import math
  c=self.visual;c.delete('all');w=max(1,c.winfo_width());h=max(1,c.winfo_height());p=LABBS[self.app.labbs.selected]
  for j in range(4):
   x=w*(j+.5)/4;y=h*.49;r=24+j*5
   c.create_oval(x-r,y-r,x+r,y+r,outline=p.color,width=3)
   c.create_text(x,y,text=['OSC','ENV','FILTER','OUT'][j],fill=CREAM,font=('Segoe UI',10,'bold'))
  c.create_text(12,h-17,text=f'{p.wave.upper()}   A {p.attack:.3f}   D {p.decay:.2f}   S {p.sustain:.2f}   R {p.release:.2f}',fill=MINT,anchor='w')
 def refresh(self):
  i=self.app.labbs.selected;p=LABBS[i];self.title.config(text=p.name.upper());self.level.set(round(self.app.labbs.volume[i]*100));self.mute.config(text='UNMUTE' if self.app.labbs.mute[i] else 'MUTE');self.solo.config(text='UNSOLO' if self.app.labbs.solo[i] else 'SOLO');self.draw()
  self.loading_params=True
  for name,(scale,lo,hi) in self.advanced_scales.items():scale.set(round(100*(self.app.labbs.parameters[i][name]-lo)/(hi-lo)))
  self.channel.delete(0,'end');self.channel.insert(0,str(self.app.labbs.midi_channels[i]))
  self.loading_params=False
 def poll(self):
  if not self.win.winfo_exists():return
  if self.app.labbs.selected != self._last_selected:
   self._last_selected=self.app.labbs.selected
   self.list.selection_clear(0,'end');self.list.selection_set(self._last_selected);self.list.see(self._last_selected);self.refresh()
  self.peak.config(text=f'MASTER PEAK: {self.app.labbs.master.peak:.3f}  •  Audio: {self.app.engine.audio_status}')
  self.win.after(150,self.poll)
