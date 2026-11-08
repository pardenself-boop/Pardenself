"""BOOM BAP TOOLBOXX audio smoke test: isolated from the full DAW UI."""
import math
import queue
import struct
import threading
import tkinter as tk
import wave
from pathlib import Path
from tkinter import ttk, filedialog, messagebox
from toolboxx import Engine
from street_note_router import StreetNoteRouter
from street_pad_kits import save_kit, load_kit

class AudioTest:
    def __init__(self, root):
        self.root = root
        self.engine = Engine()
        self.root.title('BOOM BAP TOOLBOXX | STREET SOUND CHECK')
        self.root.geometry('920x760')
        self.root.minsize(850,720)
        self.root.configure(bg='#1c1820')
        self.status = tk.StringVar(value='Ready — select an output and start audio')
        self.device = tk.StringVar(value='System default')
        self.devices = {'System default': None}
        self.midi_events=queue.Queue(maxsize=2048)
        self.midi_port=None
        self.midi_notes={}
        self.note_router=StreetNoteRouter(
            lambda note, velocity, inst:self.engine.labbs.note_on(note=note,velocity=velocity,labb=inst,duration=30.0),
            lambda note, inst:self.engine.labbs.note_off(note=note,labb=inst),
            self.panic)
        self.instrument=tk.StringVar(value='BASS LABB')
        self.midi_channel=tk.StringVar(value='ALL')
        self.instrument_ids={'BASS LABB':3,'KEY 88':7,'SYNTH LABB':5,'BREAK LABB':4}
        self.keyboard_held={}
        self.pad_midi_mode=tk.BooleanVar(value=False)
        self.pad_window=None
        self.pad_buttons=[]
        self.pad_paths=[None]*32
        self.keyboard_notes={'a':60,'w':61,'s':62,'e':63,'d':64,'f':65,'t':66,'g':67,'y':68,'h':69,'u':70,'j':71,'k':72}
        self.midi_device=tk.StringVar(value='')
        tk.Label(root, text='STREET SOUND CHECK  /  AUDIO TEST', font=('Segoe UI', 17, 'bold'), fg='#f4a36b', bg='#1c1820').pack(pady=16)
        tk.Label(root, text='Windows output device', fg='white', bg='#1c1820').pack()
        self.selector = ttk.Combobox(root, textvariable=self.device, state='readonly', width=65)
        self.selector.pack(pady=7)
        tk.Button(root, text='REFRESH DEVICES', command=self.refresh).pack(pady=3)
        controls = tk.Frame(root, bg='#1c1820'); controls.pack(pady=12)
        for label, action in [('START AUDIO', self.start), ('STOP AUDIO', self.stop), ('PANIC', self.panic)]:
            tk.Button(controls, text=label, command=action, width=17).pack(side='left', padx=5)
        keys = tk.Frame(root, bg='#1c1820'); keys.pack(pady=10)
        for name, idx, note in [('BASS LABB',3,36), ('KEY 88',7,60), ('SYNTH LABB',5,64), ('BREAK LABB',4,48)]:
            tk.Button(keys, text=name, width=17, command=lambda i=idx,n=note:self.play(i,n)).pack(side='left',padx=3)
        midi=tk.Frame(root,bg='#1c1820');midi.pack(pady=5)
        tk.Label(midi,text='STREET WIRETAP MIDI INPUT',bg='#1c1820',fg='#f4a36b').pack(side='left',padx=5)
        self.midi_selector=ttk.Combobox(midi,textvariable=self.midi_device,width=32,state='readonly');self.midi_selector.pack(side='left')
        tk.Button(midi,text='SCAN',command=self.scan_midi).pack(side='left',padx=3)
        tk.Button(midi,text='CONNECT',command=self.connect_midi).pack(side='left',padx=3)
        tk.Button(midi,text='DISCONNECT',command=self.disconnect_midi).pack(side='left',padx=3)
        selection=tk.Frame(root,bg='#1c1820');selection.pack(pady=4)
        tk.Label(selection,text='MIDI → INSTRUMENT',bg='#1c1820',fg='white').pack(side='left')
        ttk.Combobox(selection,textvariable=self.instrument,values=list(self.instrument_ids),width=17,state='readonly').pack(side='left',padx=8)
        tk.Label(selection,text='CHANNEL',bg='#1c1820',fg='white').pack(side='left')
        ttk.Combobox(selection,textvariable=self.midi_channel,values=['ALL']+[str(i) for i in range(1,17)],width=6,state='readonly').pack(side='left',padx=8)
        self.midi_led=tk.Label(root,text='● MIDI IN',bg='#1c1820',fg='#662c35');self.midi_led.pack()
        sample=tk.Frame(root,bg='#1c1820');sample.pack(pady=5)
        tk.Button(sample,text='LOAD WAV INTO SELECTED LABB',command=self.load_wav).pack(side='left',padx=6)
        tk.Label(sample,text='ROOT NOTE',fg='white',bg='#1c1820').pack(side='left')
        self.root_note=tk.IntVar(value=60)
        tk.Spinbox(sample,from_=0,to=127,width=4,textvariable=self.root_note).pack(side='left',padx=6)
        tk.Label(root,text='Computer keys: A W S E D F T G Y H U J K — play / release notes (when not typing)',fg='#e2d8c7',bg='#1c1820').pack()
        pads=tk.Frame(root,bg='#1c1820');pads.pack(pady=4)
        tk.Checkbutton(pads,text='MIDI PAD MODE (notes 36–67 → 32 pads)',variable=self.pad_midi_mode,fg='#f4a36b',bg='#1c1820',selectcolor='#28212d',command=self.on_pad_mode_change).pack(side='left',padx=8)
        tk.Button(pads,text='OPEN 32-PAD STREET DECK',command=self.open_pad_deck).pack(side='left')
        tk.Button(root, text='EXPORT OFFLINE TEST WAV (works without audio device)', command=self.export).pack(pady=6)
        self.meter = ttk.Progressbar(root, length=490, maximum=100)
        self.meter.pack(pady=10)
        tk.Label(root, textvariable=self.status, wraplength=630, fg='#8ce3c9', bg='#1c1820').pack(pady=8)
        tk.Label(root, text='Start Audio → press an instrument. If silent, export WAV and play it in Windows.', fg='#e2d8c7', bg='#1c1820').pack()
        self.refresh()
        self.scan_midi()
        self.root.after(20,self.poll_midi)
        self.root.after(100, self.update_meter)
        self.root.bind('<KeyPress>',self.key_down)
        self.root.bind('<KeyRelease>',self.key_up)
        self.root.protocol('WM_DELETE_WINDOW', self.close)
    def on_pad_mode_change(self):
        self.note_router.clear()
        self.release_keyboard()
        self.status.set('32-pad MIDI mode enabled' if self.pad_midi_mode.get() else 'Instrument MIDI mode enabled')
    def open_pad_deck(self):
        if self.pad_window and self.pad_window.winfo_exists():
            self.pad_window.lift();return
        self.pad_window=tk.Toplevel(self.root)
        self.pad_window.title('TOOLBOXX | STREET DECK | 32 PADS')
        self.pad_window.configure(bg='#1c1820')
        self.pad_buttons=[]
        for idx in range(32):
            frame=tk.Frame(self.pad_window,bg='#28212d',padx=4,pady=4)
            frame.grid(row=idx//8,column=idx%8,padx=3,pady=4)
            button=tk.Button(frame,text=f'PAD {idx+1:02}',width=9,bg='#7043ad',fg='white',command=lambda i=idx:self.trigger_pad(i))
            button.pack()
            tk.Button(frame,text='LOAD WAV',width=9,command=lambda i=idx:self.load_pad(i)).pack(pady=2)
            self.pad_buttons.append(button)
        actions=tk.Frame(self.pad_window,bg='#1c1820')
        actions.grid(row=4,column=0,columnspan=8,pady=8)
        tk.Button(actions,text='SAVE 32-PAD KIT',command=self.save_pad_kit).pack(side='left',padx=5)
        tk.Button(actions,text='LOAD 32-PAD KIT',command=self.load_pad_kit).pack(side='left',padx=5)
        tk.Label(self.pad_window,text='MIDI 36–67 → pads 1–32. Kit files reference WAVs; keep samples with your kit.',bg='#1c1820',fg='#f4a36b').grid(row=5,column=0,columnspan=8,pady=8)
    def load_pad(self,index):
        path=filedialog.askopenfilename(title=f'Load WAV into pad {index+1}',filetypes=[('WAV audio','*.wav')])
        if not path:return
        try:
            self.engine.load(index,path)
            self.pad_paths[index]=str(Path(path).resolve())
            if self.pad_window and self.pad_window.winfo_exists():
                self.pad_buttons[index].configure(text=Path(path).stem[:11],bg='#bd693b')
            self.status.set(f'Pad {index+1:02}: {Path(path).name}')
        except Exception as exc:self.status.set(f'Pad load failed: {exc}')
    def save_pad_kit(self):
        path=filedialog.asksaveasfilename(title='Save TOOLBOXX pad kit',defaultextension='.tbkit',filetypes=[('TOOLBOXX kit','*.tbkit')])
        if not path:return
        try:
            save_kit(path,self.pad_paths)
            self.status.set('Saved pad kit: '+Path(path).name)
        except Exception as exc:self.status.set('Kit save failed: '+str(exc))
    def load_pad_kit(self):
        path=filedialog.askopenfilename(title='Load TOOLBOXX pad kit',filetypes=[('TOOLBOXX kit','*.tbkit')])
        if not path:return
        try:
            paths=load_kit(path)
            # Validate every sample before changing any pad; invalid kits leave current deck intact.
            missing=[str(i+1) for i,p in enumerate(paths) if p and not Path(p).is_file()]
            if missing:raise FileNotFoundError('Missing WAV for pads: '+', '.join(missing))
            from toolboxx import Engine
            staging=Engine()
            for i,p in enumerate(paths):
                if p:staging.load(i,p)
            with self.engine.lock:
                self.engine.samples=list(staging.samples)
                self.engine.sample_paths=list(staging.sample_paths)
                self.engine.voices.clear()
            self.pad_paths=list(paths)
            if self.pad_window and self.pad_window.winfo_exists():
                for i,p in enumerate(paths):
                    self.pad_buttons[i].configure(text=Path(p).stem[:11] if p else f'PAD {i+1:02}',bg='#bd693b' if p else '#7043ad')
            self.status.set('Loaded 32-pad kit: '+Path(path).name)
        except Exception as exc:self.status.set('Kit load failed: '+str(exc))
    def trigger_pad(self,index):
        self.engine.trigger(index)
        self.status.set(f'PAD {index+1:02} triggered'+(' — START AUDIO to hear' if not self.engine.stream else ''))
    def release_keyboard(self):
        for note,inst in list(self.keyboard_held.values()):
            self.engine.labbs.note_off(note=note,labb=inst)
        self.keyboard_held.clear()
    def load_wav(self):
        path=filedialog.askopenfilename(title='Load sample',filetypes=[('WAV audio','*.wav')])
        if not path:return
        try:
            inst=self.instrument_ids[self.instrument.get()]
            self.engine.labbs.crate.load(inst,path,root_note=int(self.root_note.get()))
            self.status.set(f'Loaded WAV into {self.instrument.get()}: {Path(path).name}')
        except Exception as exc:self.status.set(f'Sample load failed: {exc}')
    def key_down(self,event):
        if isinstance(event.widget,(tk.Entry,ttk.Entry,ttk.Combobox,tk.Spinbox)):return
        key=event.keysym.lower()
        if key not in self.keyboard_notes or key in self.keyboard_held:return
        note=self.keyboard_notes[key]
        if self.pad_midi_mode.get():
            self.trigger_pad(note-60);return
        inst=self.instrument_ids[self.instrument.get()]
        self.keyboard_held[key]=(note,inst)
        self.engine.labbs.note_on(note=note,velocity=.8,labb=inst,duration=30)
    def key_up(self,event):
        key=event.keysym.lower()
        if key not in self.keyboard_held:return
        note,inst=self.keyboard_held.pop(key)
        self.engine.labbs.note_off(note=note,labb=inst)
    def scan_midi(self):
        try:
            import mido
            names=mido.get_input_names()
        except Exception as exc:
            names=[];self.status.set('MIDI unavailable: '+str(exc))
        self.midi_selector['values']=names
        if names and self.midi_device.get() not in names:self.midi_device.set(names[0])
        return names
    def connect_midi(self):
        self.disconnect_midi()
        name=self.midi_device.get()
        if not name:
            self.status.set('No MIDI port found. Set Maschine Studio to MIDI mode, then SCAN.')
            return
        try:
            import mido
            self.midi_port=mido.open_input(name,callback=self.enqueue_midi)
            self.status.set('MIDI connected: '+name)
        except Exception as exc:self.status.set('MIDI connection failed: '+str(exc))
    def enqueue_midi(self,msg):
        try:self.midi_events.put_nowait(msg)
        except queue.Full:
            # A dropped note-off can stick a voice; recover on the UI thread.
            try:self.midi_events.get_nowait()
            except queue.Empty:pass
            try:self.midi_events.put_nowait(('panic',))
            except queue.Full:pass
    def poll_midi(self):
        activity=False
        for _ in range(128):
            try:msg=self.midi_events.get_nowait()
            except queue.Empty:break
            activity=True
            if isinstance(msg,tuple) and msg==('panic',):self.note_router.clear();self.midi_notes.clear();continue
            channel=self.midi_channel.get()
            filt=None if channel=='ALL' else int(channel)-1
            inst=self.instrument_ids[self.instrument.get()]
            if self.pad_midi_mode.get() and self.handle_pad_midi(msg,filt):
                self.status.set(f'MIDI PAD {msg.note-35:02} triggered')
                continue
            if self.pad_midi_mode.get():continue
            if self.note_router.message(msg,inst,filt):
                self.status.set(f'MIDI {getattr(msg,"type","event")}  channel {getattr(msg,"channel",0)+1} → {self.instrument.get()}')
        self.midi_led.configure(fg='#ff3b43' if activity else '#662c35')
        if self.root.winfo_exists():self.root.after(20,self.poll_midi)
    def handle_pad_midi(self,msg,channel_filter=None):
        if getattr(msg,'type','')!='note_on' or getattr(msg,'velocity',0)<=0:return False
        if channel_filter is not None and getattr(msg,'channel',0)!=channel_filter:return False
        note=getattr(msg,'note',-1)
        if not 36<=note<=67:return False
        self.trigger_pad(note-36)
        return True
    def disconnect_midi(self):
        if self.midi_port:
            self.midi_port.close();self.midi_port=None
        self.midi_notes.clear()
        self.note_router.clear()
    def refresh(self):
        self.devices={'System default':None}
        try:
            import sounddevice as sd
            for i,d in enumerate(sd.query_devices()):
                if d['max_output_channels']>=2:
                    self.devices[f"{i}: {d['name']}"]=i
            self.status.set('Output devices found. Select one, then START AUDIO.')
        except Exception as exc:
            self.status.set(f'Audio backend unavailable: {exc}. Offline WAV export still works.')
        self.selector['values']=list(self.devices)
        if self.device.get() not in self.devices:self.device.set('System default')
    def start(self):
        try:
            self.engine.start(device=self.devices[self.device.get()])
            self.status.set('Audio running — press BASS, KEY 88, SYNTH or BREAK.')
        except Exception as exc:
            self.status.set(f'Cannot start audio: {exc}')
    def stop(self):
        try:self.engine.stop();self.status.set('Audio stopped')
        except Exception as exc:self.status.set(str(exc))
    def panic(self):
        self.engine.labbs.all_notes_off()
        with self.engine.lock:self.engine.voices.clear()
        self.status.set('All notes off')
    def play(self, idx, note):
        try:
            self.engine.labbs.note_on(note=note,velocity=.85,labb=idx,duration=.65)
            self.status.set(f'Triggered {idx+1}: {note}'+(' — audio running' if self.engine.stream else ' — start audio to hear live'))
        except Exception as exc:self.status.set(f'Trigger failed: {exc}')
    def export(self):
        target=filedialog.asksaveasfilename(title='Save sound check', defaultextension='.wav', initialfile='TOOLBOXX_SOUND_CHECK.wav', filetypes=[('WAV audio','*.wav')])
        if not target:return
        def worker():
            try:
                # Dedicated engine: offline rendering cannot disrupt the live engine.
                e=Engine();e.labbs.note_on(note=48,velocity=.85,labb=3,duration=.45)
                samples=[]
                for _ in range(94):samples.extend(e.render(512))
                e.labbs.note_on(note=60,velocity=.85,labb=7,duration=.55)
                for _ in range(94):samples.extend(e.render(512))
                data=b''.join(struct.pack('<hh',int(max(-1,min(1,s))*32767),int(max(-1,min(1,s))*32767)) for s in samples)
                with wave.open(target,'wb') as w:
                    w.setnchannels(2);w.setsampwidth(2);w.setframerate(e.sr);w.writeframes(data)
                self.root.after(0,lambda:self.status.set('Saved playable WAV: '+str(target)))
            except Exception as exc:
                self.root.after(0,lambda msg=str(exc):self.status.set('WAV export failed: '+msg))
        threading.Thread(target=worker,daemon=True).start()
    def update_meter(self):
        if not self.root.winfo_exists():return
        self.meter['value']=max(0,min(100,self.engine.labbs.master.peak*100))
        self.root.after(100,self.update_meter)
    def close(self):
        self.release_keyboard()
        self.disconnect_midi();self.stop();self.root.destroy()

def main():
    root=tk.Tk();AudioTest(root);root.mainloop()

if __name__=='__main__':main()
