"""Hardware-neutral MIDI note pattern editor for LABB instruments."""
import tkinter as tk
from tkinter import ttk
from note_lane import Note

class AdvancedMidiWindow:
 def __init__(self,app):
  self.app=app;self.win=tk.Toplevel(app.root);self.win.title('TOOLBOXX / ADVANCED MIDI LABB');self.win.geometry('950x670');self.win.configure(bg='#17151c')
  self.pattern=tk.StringVar(value='labb-main');self.pitch=tk.IntVar(value=48);self.beat=tk.DoubleVar(value=0);self.length=tk.DoubleVar(value=.5);self.velocity=tk.IntVar(value=100)
  top=tk.Frame(self.win,bg='#28212d');top.pack(fill='x',padx=10,pady=10)
  tk.Label(top,text='MIDI LABB • NOTE MATRIX',bg='#28212d',fg='#8ce3c9',font=('Segoe UI',18,'bold')).pack(side='left',padx=12)
  tk.Label(top,text='PATTERN',bg='#28212d',fg='#f3e5c9').pack(side='left')
  self.patterns=ttk.Combobox(top,textvariable=self.pattern,values=list(app.notes.patterns),width=22);self.patterns.pack(side='left',padx=8);self.patterns.bind('<<ComboboxSelected>>',lambda e:self.refresh())
  tk.Button(top,text='NEW PATTERN',command=self.new_pattern,bg='#9652ca',fg='white').pack(side='left')
  editor=tk.Frame(self.win,bg='#17151c');editor.pack(fill='both',expand=True,padx=12)
  self.canvas=tk.Canvas(editor,bg='#201821',highlightthickness=0,height=320);self.canvas.pack(fill='both',expand=True)
  self.canvas.bind('<Button-1>',self.canvas_click)
  fields=tk.Frame(self.win,bg='#28212d');fields.pack(fill='x',padx=12,pady=8)
  for i,(label,var,lo,hi,inc) in enumerate((('BEAT',self.beat,0,4,.25),('PITCH',self.pitch,0,127,1),('LENGTH',self.length,.125,4,.125),('VELOCITY',self.velocity,1,127,1))):
   tk.Label(fields,text=label,bg='#28212d',fg='#f3e5c9').grid(row=0,column=i,padx=12)
   tk.Spinbox(fields,from_=lo,to=hi,increment=inc,textvariable=var,width=10).grid(row=1,column=i,padx=12)
  buttons=tk.Frame(self.win,bg='#17151c');buttons.pack(fill='x',padx=12,pady=8)
  for name,action in (('ADD NOTE',self.add),('DELETE SELECTED',self.delete),('AUDITION',self.audition),('QUANTIZE 1/16',lambda:self.quantize(.25)),('QUANTIZE 1/32',lambda:self.quantize(.125)),('HUMANIZE VELOCITY',self.humanize)):
   tk.Button(buttons,text=name,command=action,bg='#81374f',fg='white').pack(side='left',padx=4)
  self.info=tk.Label(self.win,text='Click a note to select. MIDI patterns are shared with Track City.',bg='#17151c',fg='#8ce3c9');self.info.pack(anchor='w',padx=12,pady=8)
  self.selected=None;self.refresh()
 def notes(self):return self.app.notes.patterns.setdefault(self.pattern.get(),[])
 def refresh(self):
  c=self.canvas;c.delete('all');w=max(700,c.winfo_width());h=max(300,c.winfo_height());self.bounds=(w,h)
  for i in range(17):
   x=60+i*(w-75)/16;c.create_line(x,20,x,h-15,fill='#534353' if i%4==0 else '#302832');c.create_text(x+3,10,text=str(i/4),anchor='w',fill='#f3e5c9')
  for n in range(24):
   pitch=48+n;y=h-15-n*(h-40)/24;c.create_line(60,y,w-15,y,fill='#302832');c.create_text(48,y,text=str(pitch),fill='#8ce3c9')
  for i,n in enumerate(self.notes()):
   x=60+(n.beat%4)*(w-75)/4;y=h-15-(n.pitch-48)*(h-40)/24
   if 20<=y<=h-15:c.create_rectangle(x,y-5,x+max(4,n.duration*(w-75)/4),y+5,fill='#e17a35' if i==self.selected else '#9652ca',outline='#f3e5c9')
  self.info.config(text=f'{len(self.notes())} notes • Pattern: {self.pattern.get()} • Select notes with click • Pitch display 48–71')
 def canvas_click(self,e):
  w,h=self.bounds;beat=max(0,min(3.99,(e.x-60)/(w-75)*4));pitch=max(0,min(127,round(48+(h-15-e.y)*24/(h-40))))
  found=None
  for i,n in enumerate(self.notes()):
   if abs(n.beat-beat)<max(.15,n.duration) and abs(n.pitch-pitch)<=1:found=i;break
  self.selected=found
  if found is not None:
   n=self.notes()[found];self.pitch.set(n.pitch);self.beat.set(n.beat);self.length.set(n.duration);self.velocity.set(round(n.velocity*127))
  else:self.pitch.set(pitch);self.beat.set(round(beat*4)/4)
  self.refresh()
 def add(self):
  self.app.notes.add(self.pattern.get(),float(self.beat.get()),int(self.pitch.get()),int(self.velocity.get())/127,float(self.length.get()));self.selected=len(self.notes())-1;self.refresh()
 def delete(self):
  if self.selected is not None and self.selected<len(self.notes()):self.notes().pop(self.selected);self.selected=None;self.refresh()
 def audition(self):self.app.labbs.note_on(int(self.pitch.get()),int(self.velocity.get())/127,duration=float(self.length.get()))
 def quantize(self,step):
  for n in self.notes():n.beat=round(n.beat/step)*step
  self.refresh()
 def humanize(self):
  import random
  for n in self.notes():n.velocity=max(.05,min(1.,n.velocity+random.uniform(-.07,.07)))
  self.refresh()
 def new_pattern(self):
  import uuid
  name='midi-'+uuid.uuid4().hex[:6];self.app.notes.patterns[name]=[];self.pattern.set(name);self.patterns.configure(values=list(self.app.notes.patterns));self.selected=None;self.refresh()
