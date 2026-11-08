"""STREET WIRETAP: standalone, non-destructive MIDI diagnostic for Windows.
Run with python street_midi_test.py. No device required for demo mode.
"""
import json
import queue
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from pathlib import Path
from studio_midi_adapter import MidiControlRouter

class Wiretap(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('BOOM BAP TOOLBOXX | STREET WIRETAP - MIDI TEST')
        self.geometry('940x620')
        self.configure(bg='#17191c')
        self.events=queue.Queue(); self.port=None; self.last=None; self.learn=False
        self.bindings={}; self.count=0; self.router=MidiControlRouter()
        top=ttk.Frame(self,padding=12);top.pack(fill='x')
        ttk.Label(top,text='STREET WIRETAP  •  HARDWARE FIRST',font=('Segoe UI',17,'bold')).pack(anchor='w')
        bar=ttk.Frame(self,padding=10);bar.pack(fill='x')
        ttk.Label(bar,text='MIDI INPUT').pack(side='left')
        self.device=ttk.Combobox(bar,width=48,state='readonly');self.device.pack(side='left',padx=8)
        ttk.Button(bar,text='SCAN',command=self.scan).pack(side='left',padx=3)
        ttk.Button(bar,text='CONNECT',command=self.connect).pack(side='left',padx=3)
        ttk.Button(bar,text='DISCONNECT',command=self.disconnect).pack(side='left',padx=3)
        ttk.Button(bar,text='DEMO NOTE',command=self.demo).pack(side='left',padx=3)
        line=ttk.Frame(self,padding=10);line.pack(fill='x')
        self.status=tk.StringVar(value='Not connected. Scan MIDI ports or use DEMO NOTE.')
        ttk.Label(line,textvariable=self.status).pack(side='left')
        self.led=tk.Canvas(line,width=22,height=22,bg='#17191c',highlightthickness=0);self.led.pack(side='right')
        self.dot=self.led.create_oval(3,3,19,19,fill='#542727',outline='')
        commands=ttk.Frame(self,padding=10);commands.pack(fill='x')
        ttk.Label(commands,text='Assign last incoming control to').pack(side='left')
        self.action=ttk.Combobox(commands,values=['PLAY / STOP','RECORD','BACK BEAT','NEXT BEAT','BACK BAR','NEXT BAR','JOG -','JOG +','CHOP','UNDO','REDO','LOOP TOGGLE','PAD BANK +','PAD BANK -','ALL NOTES OFF','HW JOG','JOG','JOG CLICK','JOG BACK','PLAY/STOP','EDIT:MARQUEE','EDIT:LOOP MOVE','PAGE NEXT','PAGE PREV'],width=24,state='readonly')
        self.action.set('PLAY / STOP');self.action.pack(side='left',padx=8)
        ttk.Button(commands,text='LEARN NEXT',command=self.arm).pack(side='left',padx=3)
        self.mode=ttk.Combobox(commands,values=['button','relative_twos_complement','relative_binary_offset','relative_sign_magnitude','absolute'],width=23,state='readonly');self.mode.set('button');self.mode.pack(side='left',padx=3)
        ttk.Button(commands,text='SAVE PROFILE',command=self.save).pack(side='left',padx=3)
        ttk.Button(commands,text='LOAD PROFILE',command=self.load).pack(side='left',padx=3)
        ttk.Button(commands,text='CLEAR LOG',command=lambda:self.log.delete('1.0','end')).pack(side='left',padx=3)
        self.log=tk.Text(self,bg='#0b0d10',fg='#f4bd7c',insertbackground='white',font=('Consolas',11),wrap='none')
        self.log.pack(fill='both',expand=True,padx=12,pady=8)
        self.log.insert('end','STREET WIRETAP ready. Maschine Studio must expose a MIDI input port (e.g. via NI Controller Editor MIDI mode).\nThis diagnostic does not configure Maschine HID mode, LEDs or screens.\n\n')
        self.protocol('WM_DELETE_WINDOW',self.close)
        self.after(30,self.poll)
        self.scan()
    def scan(self):
        try:
            import mido
            names=mido.get_input_names()
        except Exception as e:
            names=[];self.write('MIDI backend unavailable: '+str(e)+'\nInstall: py -m pip install mido python-rtmidi')
        self.device['values']=names
        if names:self.device.current(0)
        self.status.set(f'{len(names)} MIDI input port(s) found. Select one and CONNECT.')
    def connect(self):
        name=self.device.get()
        if not name:return messagebox.showinfo('STREET WIRETAP','No MIDI port selected. Scan again or check device MIDI mode.')
        self.disconnect()
        try:
            import mido
            self.port=mido.open_input(name,callback=self.events.put)
            self.status.set('Connected: '+name)
            self.write('CONNECTED '+name)
        except Exception as e:
            self.status.set('Connection failed');messagebox.showerror('MIDI connection failed',str(e))
    def disconnect(self):
        if self.port:
            self.port.close();self.port=None
        self.status.set('Disconnected')
    def demo(self):
        class Message:
            type='note_on';channel=0;note=60;velocity=100
        self.events.put(Message())
    def arm(self):
        self.learn=True;self.status.set('LEARN ARMED — press a pad, button or turn an encoder')
    def write(self,s):
        self.log.insert('end',s+'\n');self.log.see('end')
    def poll(self):
        processed=0
        while processed<200:
            try:m=self.events.get_nowait()
            except queue.Empty:break
            self.handle(m);processed+=1
        if processed:self.led.itemconfigure(self.dot,fill='#e32636')
        else:self.led.itemconfigure(self.dot,fill='#542727')
        self.after(30,self.poll)
    def handle(self,m):
        typ=getattr(m,'type','unknown');ch=getattr(m,'channel',None)
        number=getattr(m,'control',None) if typ=='control_change' else getattr(m,'note',None)
        val=getattr(m,'value',None) if typ=='control_change' else getattr(m,'velocity',None)
        self.count+=1
        key=f"{'cc' if typ=='control_change' else 'note'}:{ch}:{number}"
        label=self.bindings.get(key,'')
        commands=self.router.translate(m)
        self.write(f'{datetime.now():%H:%M:%S.%f}'[:-3]+f'  #{self.count:05}  {typ:<16} CH={ch}  NUM={number}  VALUE={val}'+(f'  -> {label}' if label else '')+(f'  DISPATCH={commands}' if commands else ''))
        if self.learn and typ in ('note_on','control_change') and val is not None and val>0:
            self.bindings[key]=self.action.get();self.router.bind('cc' if typ=='control_change' else 'note',ch,number,self.action.get(),self.mode.get());self.learn=False
            self.status.set(f'LEARNED {key} -> {self.action.get()} (save profile to keep)')
    def save(self):
        path=filedialog.asksaveasfilename(defaultextension='.json',filetypes=[('JSON profile','*.json')],initialfile='street_wiretap_profile.json')
        if path:
            self.router.save(path)
            self.write('PROFILE SAVED '+path)
    def load(self):
        path=filedialog.askopenfilename(filetypes=[('JSON profile','*.json')])
        if not path:return
        try:
            data=json.loads(Path(path).read_text(encoding='utf-8'))
            if data.get('schema')!=1 or not isinstance(data.get('bindings'),dict):raise ValueError('Invalid profile')
            if all(isinstance(v,str) for v in data['bindings'].values()):
                # Convert legacy Wiretap profiles into the DAW-compatible router format.
                converted=MidiControlRouter()
                for key,command in data['bindings'].items():
                    kind,ch,num=key.split(':')
                    converted.bind('cc' if kind=='control_change' else 'note',int(ch),int(num),command)
                self.router=converted
            else:
                self.router.load(path)
            self.bindings={k:v['command'] for k,v in self.router.bindings.items()}
            self.write('DAW-COMPATIBLE PROFILE LOADED '+path)
        except Exception as e:messagebox.showerror('Profile error',str(e))
    def close(self):
        self.disconnect();self.destroy()

if __name__=='__main__':Wiretap().mainloop()
