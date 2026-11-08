"""Map MIDI mode messages to shared TOOLBOXX commands, no USB assumptions."""
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from studio_midi_adapter import VALID_MODES

class HardwareSetupWindow:
 def __init__(self,app):
  self.app=app;self.win=tk.Toplevel(app.root);self.win.title('TOOLBOXX / STUDIO MIDI HARDWARE SETUP');self.win.geometry('980x650');self.win.configure(bg='#17151c')
  self.kind=tk.StringVar(value='cc');self.channel=tk.IntVar(value=0);self.number=tk.IntVar(value=1)
  self.mode=tk.StringVar(value='relative_twos_complement');self.command=tk.StringVar(value='HW JOG')
  title=tk.Label(self.win,text='MASCHINE STUDIO / MIDI MODE BRIDGE',bg='#17151c',fg='#8ce3c9',font=('Segoe UI',16,'bold'));title.pack(pady=14)
  tk.Label(self.win,text='Map messages reported by Controller Editor. Test physical messages later.\nThis does not yet drive Studio screens or LEDs.',bg='#17151c',fg='#f3e5c9').pack(pady=4)
  ports=tk.Frame(self.win,bg='#17151c');ports.pack(fill='x',padx=22,pady=8)
  self.device=ttk.Combobox(ports,width=52,state='readonly');self.device.pack(side='left',padx=4)
  for label,fn in [('SCAN',self.scan),('CONNECT',self.connect),('DISCONNECT',self.app.close_midi)]:tk.Button(ports,text=label,command=fn).pack(side='left',padx=3)
  self.connection=tk.Label(self.win,bg='#17151c',fg='#8ce3c9');self.connection.pack()
  from toolboxx import COMMANDS
  row=tk.Frame(self.win,bg='#17151c');row.pack(pady=12)
  for index,(name,var,options) in enumerate([('TYPE',self.kind,['note','cc']),('CHANNEL (0-15)',self.channel,list(range(16))),('NOTE / CC',self.number,list(range(128))),('MODE',self.mode,['button']+list(VALID_MODES)),('COMMAND',self.command,list(dict.fromkeys(['HW JOG','JOG','SHIFT']+COMMANDS))) ]):
   frame=tk.Frame(row,bg='#17151c');frame.grid(row=index//3,column=index%3,padx=12,pady=5,sticky='ew')
   tk.Label(frame,text=name,bg='#17151c',fg='#f3e5c9',font=('Segoe UI',8)).pack()
   combo=ttk.Combobox(frame,textvariable=var,values=options,width=29,state='readonly');combo.pack()
   if name=='COMMAND':combo.bind('<<ComboboxSelected>>',self.command_changed)
  tk.Button(self.win,text='LEARN NEXT PHYSICAL CONTROL',command=self.learn,bg='#81374f',fg='white').pack(pady=5)
  tk.Button(self.win,text='CANCEL LEARN',command=self.cancel_learn).pack(pady=3)
  tk.Button(self.win,text='ASSIGN CONTROL',command=self.assign,bg='#d7773d',fg='white').pack(pady=6)
  tk.Button(self.win,text='SAVE PROFILE JSON',command=self.save).pack(pady=3)
  tk.Button(self.win,text='LOAD PROFILE JSON',command=self.load).pack(pady=3)
  tk.Button(self.win,text='TEST ROTATE RIGHT (VIRTUAL)',command=lambda:self.test_direction(1)).pack(pady=3)
  tk.Button(self.win,text='TEST ROTATE LEFT (VIRTUAL)',command=lambda:self.test_direction(-1)).pack(pady=3)
  self.status=tk.Label(self.win,text='No hardware is connected automatically. Use MIDI MAP > SCAN / CONNECT.',bg='#17151c',fg='#8ce3c9',wraplength=700);self.status.pack(pady=12)
  self.win.protocol('WM_DELETE_WINDOW',self.close);self.scan();self.poll()
 def command_changed(self,event=None):
  if self.command.get() not in ('HW JOG','JOG') and not self.command.get().endswith((' +',' -')):self.mode.set('button')
  elif self.mode.get()=='button':self.mode.set('relative_twos_complement')
 def scan(self):
  selected=self.device.get();names=self.app.scan_midi();self.device['values']=names
  self.device.set(selected if selected in names else self.app.midi_device.get())
 def connect(self):
  self.app.midi_device.set(self.device.get());self.app.open_midi()
 def learn(self):
  try:self.app.arm_hardware_learn(self.command.get(),self.mode.get());self.status.config(text=self.app.hardware_status)
  except (ValueError,TypeError) as exc:messagebox.showerror('MIDI learn',str(exc),parent=self.win)
 def cancel_learn(self):
  self.app.hardware_learn=None;self.app.hardware_status='MIDI learn cancelled';self.status.config(text=self.app.hardware_status)
 def close(self):
  self.app.hardware_learn=None
  if hasattr(self,'_poll_id'):self.win.after_cancel(self._poll_id)
  self.win.destroy()
 def poll(self):
  if not self.win.winfo_exists():return
  learned=getattr(self.app,'last_hardware_learn',None)
  if learned is not None and learned is not getattr(self,'_last_learned',None):
   self._last_learned=learned;self.kind.set(learned['kind']);self.channel.set(learned['channel']);self.number.set(learned['number']);self.mode.set(learned['mode']);self.command.set(learned['command'])
  name=getattr(self.app,'midi_connected_name',None)
  self.connection.config(text=('CONNECTED: '+name) if name else 'No MIDI input connected — select Maschine Studio in Controller Editor MIDI mode')
  self.status.config(text=self.app.hardware_status+f'  |  {len(self.app.hardware_midi.bindings)} mapped controls')
  self._poll_id=self.win.after(150,self.poll)
 def test_direction(self,direction):
  mode=self.mode.get()
  values={'relative_twos_complement':(1,127),'relative_binary_offset':(65,63),'relative_sign_magnitude':(1,65),'absolute':(65,63)}
  right,left=values.get(mode,(127,0));self.test(right if direction>0 else left)
 def assign(self):
  try:self.app.hardware_midi.bind(self.kind.get(),int(self.channel.get()),int(self.number.get()),self.command.get(),self.mode.get());self.app.hardware_status='Assigned '+self.command.get();self.status.config(text=self.app.hardware_status)
  except (ValueError,TypeError) as e:messagebox.showerror('Invalid mapping',str(e))
 def save(self):
  path=filedialog.asksaveasfilename(defaultextension='.json',filetypes=[('JSON','*.json')]);
  if path:self.app.hardware_midi.save(path)
 def load(self):
  path=filedialog.askopenfilename(filetypes=[('JSON','*.json')]);
  if path:
   try:self.app.hardware_midi.load(path);self.app.hardware_status='Loaded controller profile: '+path;self.status.config(text=self.app.hardware_status)
   except (OSError,ValueError,KeyError) as e:messagebox.showerror('Profile',str(e))
 def test(self,value):
  class Message:
   type='control_change';channel=0;control=1
   def __init__(self,v):self.value=v
  commands=self.app.hardware_midi.translate(Message(value))
  for command in commands:self.app.command(command)
  self.app.hardware_status='Virtual commands: '+str(commands)+' (CC 0:1 mapping required)';self.status.config(text=self.app.hardware_status)
