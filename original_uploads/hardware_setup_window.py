"""Map MIDI mode messages to shared TOOLBOXX commands, no USB assumptions."""
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from studio_midi_adapter import VALID_MODES

class HardwareSetupWindow:
 def __init__(self,app):
  self.app=app;self.win=tk.Toplevel(app.root);self.win.title('TOOLBOXX / STUDIO MIDI HARDWARE SETUP');self.win.geometry('760x480');self.win.configure(bg='#17151c')
  self.kind=tk.StringVar(value='cc');self.channel=tk.IntVar(value=0);self.number=tk.IntVar(value=1)
  self.mode=tk.StringVar(value='relative_twos_complement');self.command=tk.StringVar(value='HW JOG')
  title=tk.Label(self.win,text='MASCHINE STUDIO / MIDI MODE BRIDGE',bg='#17151c',fg='#8ce3c9',font=('Segoe UI',16,'bold'));title.pack(pady=14)
  tk.Label(self.win,text='Map messages reported by Controller Editor. Test physical messages later.\nThis does not yet drive Studio screens or LEDs.',bg='#17151c',fg='#f3e5c9').pack(pady=4)
  row=tk.Frame(self.win,bg='#17151c');row.pack(pady=12)
  for name,var,options in [('TYPE',self.kind,['note','cc']),('CHANNEL (0-15)',self.channel,list(range(16))),('NOTE / CC',self.number,list(range(128))),('MODE',self.mode,['button']+list(VALID_MODES)),('COMMAND',self.command,['HW JOG','JOG','JOG CLICK','JOG BACK','JOG SHIFT','PLAY/STOP','RECORD','PAGE NEXT','PAGE PREV','LABB NEXT','LABB PREV','LABB PLAY','EDIT:MOVE','EDIT:MARQUEE','EDIT:TRIM LEFT','EDIT:TRIM RIGHT','EDIT:LOOP START','EDIT:LOOP END','EDIT:LOOP MOVE','UNDO','REDO','SHIFT'])]:
   frame=tk.Frame(row,bg='#17151c');frame.pack(side='left',padx=3)
   tk.Label(frame,text=name,bg='#17151c',fg='#f3e5c9',font=('Segoe UI',8)).pack()
   ttk.Combobox(frame,textvariable=var,values=options,width=14 if name=='COMMAND' else 12).pack()
  tk.Button(self.win,text='ASSIGN CONTROL',command=self.assign,bg='#d7773d',fg='white').pack(pady=6)
  tk.Button(self.win,text='SAVE PROFILE JSON',command=self.save).pack(pady=3)
  tk.Button(self.win,text='LOAD PROFILE JSON',command=self.load).pack(pady=3)
  tk.Button(self.win,text='TEST ROTATE RIGHT (VIRTUAL)',command=lambda:self.test(65)).pack(pady=3)
  tk.Button(self.win,text='TEST ROTATE LEFT (VIRTUAL)',command=lambda:self.test(127)).pack(pady=3)
  self.status=tk.Label(self.win,text='No hardware is connected automatically. Use MIDI MAP > SCAN / CONNECT.',bg='#17151c',fg='#8ce3c9',wraplength=700);self.status.pack(pady=12)
 def assign(self):
  try:self.app.hardware_midi.bind(self.kind.get(),int(self.channel.get()),int(self.number.get()),self.command.get(),self.mode.get());self.status.config(text='Assigned '+self.command.get())
  except (ValueError,TypeError) as e:messagebox.showerror('Invalid mapping',str(e))
 def save(self):
  path=filedialog.asksaveasfilename(defaultextension='.json',filetypes=[('JSON','*.json')]);
  if path:self.app.hardware_midi.save(path)
 def load(self):
  path=filedialog.askopenfilename(filetypes=[('JSON','*.json')]);
  if path:
   try:self.app.hardware_midi.load(path);self.status.config(text='Loaded '+path)
   except (OSError,ValueError,KeyError) as e:messagebox.showerror('Profile',str(e))
 def test(self,value):
  class Message:
   type='control_change';channel=0;control=1
   def __init__(self,v):self.value=v
  commands=self.app.hardware_midi.translate(Message(value))
  for command in commands:self.app.command(command)
  self.status.config(text='Test commands: '+str(commands)+' (requires CC channel 0 / number 1 mapping)')
