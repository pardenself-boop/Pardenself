"""Editable physical control map and live software mirrors of shared DAW state."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from controller_surface import CONTROLS, BY_KEY, hit_test, move_rect

BG='#100f10'; PANEL='#27211d'; MINT='#82ceb5'; ORANGE='#e38b42'; CREAM='#e6d2b3'; PURPLE='#8e6a93'

class ControllerMapWindow:
    def __init__(self,app):
        self.app=app;self.win=tk.Toplevel(app.root)
        self.win.title('TOOLBOXX | Studio Control Surface');self.win.geometry(f'{min(1480,self.win.winfo_screenwidth()-60)}x{min(960,self.win.winfo_screenheight()-80)}');self.win.minsize(1040,650);self.win.configure(bg=BG)
        self.selected='PAD 1';self.drag=None;self.background=None;self._photo=None;self._image_size=None;self.edit_layout=tk.BooleanVar(value=False)
        top=tk.Frame(self.win,bg=PANEL);top.pack(fill='x')
        tk.Label(top,text='TOOLBOXX  /  STREET CONTROL DECK',font=('Segoe UI',17,'bold'),bg=PANEL,fg=CREAM).pack(side='left',padx=14,pady=12)
        for text,fn in [('SAVE MAP',self.save),('LOAD MAP',self.load),('MIDI CONNECTION',app.open_hardware_setup),('TEACH 16 PADS',app.arm_pad_learn)]:self.button(top,text,fn).pack(side='right',padx=4)
        body=tk.Frame(self.win,bg=BG);body.pack(fill='both',expand=True,padx=12,pady=10)
        self.canvas=tk.Canvas(body,bg=BG,highlightthickness=0);self.canvas.pack(side='left',fill='both',expand=True)
        self.canvas.bind('<Configure>',lambda event:self.draw());self.canvas.bind('<ButtonPress-1>',self.press);self.canvas.bind('<B1-Motion>',self.motion);self.canvas.bind('<ButtonRelease-1>',self.release)
        self.canvas.bind('<Button-3>',self.press)
        holder=tk.Frame(body,bg=PANEL,width=295);holder.pack(side='right',fill='y',padx=(12,0));holder.pack_propagate(False)
        scroll=tk.Canvas(holder,bg=PANEL,highlightthickness=0,width=278);scroll.pack(side='left',fill='both',expand=True)
        scrollbar=ttk.Scrollbar(holder,orient='vertical',command=scroll.yview);scrollbar.pack(side='right',fill='y');scroll.config(yscrollcommand=scrollbar.set)
        side=tk.Frame(scroll,bg=PANEL,padx=14,pady=14);scroll.create_window(0,0,window=side,anchor='nw',width=278)
        side.bind('<Configure>',lambda event:scroll.configure(scrollregion=scroll.bbox('all')))
        self.label(side,'CONTROL ASSIGNMENT',MINT,12).pack(anchor='w')
        self.control_label=self.label(side,'',ORANGE,17);self.control_label.pack(anchor='w',pady=(12,5))
        self.address_label=self.label(side,'Unmapped',CREAM,9);self.address_label.pack(anchor='w',pady=5)
        self.command=tk.StringVar();self.kind=tk.StringVar(value='note');self.channel=tk.IntVar(value=0);self.number=tk.IntVar(value=36);self.mode=tk.StringVar(value='button')
        from toolboxx import COMMANDS
        from studio_midi_adapter import VALID_MODES
        for label,var,values in [('COMMAND',self.command,list(dict.fromkeys(['HW JOG','JOG','SHIFT']+COMMANDS))),('MODE',self.mode,['button']+list(VALID_MODES)),('TYPE',self.kind,['note','cc']),('CHANNEL (0–15)',self.channel,list(range(16))),('NOTE / CC',self.number,list(range(128)))]:
            self.label(side,label,CREAM,9).pack(anchor='w',pady=(9,2))
            combo=ttk.Combobox(side,textvariable=var,values=values,state='readonly');combo.pack(fill='x')
            if label=='COMMAND':combo.bind('<<ComboboxSelected>>',self.command_changed)
        for text,fn in [('LEARN PHYSICAL CONTROL',self.learn),('CANCEL LEARN',self.cancel_learn),('ASSIGN ADDRESS',self.assign),('TEST COMMAND',self.test),('REMOVE ASSIGNMENT',self.unmap)]:self.button(side,text,fn).pack(fill='x',pady=(8,0))
        tk.Checkbutton(side,text='EDIT HOTSPOT POSITIONS',variable=self.edit_layout,bg=PANEL,fg=MINT,selectcolor=BG,command=self.draw).pack(anchor='w',pady=(18,5))
        self.label(side,'Drag controls to reposition their hotspots.\nMap files keep positions and MIDI bindings.',CREAM,8).pack(anchor='w')
        self.button(side,'PHOTO BACKGROUND…',self.load_background).pack(fill='x',pady=6)
        self.button(side,'RESET HOTSPOT POSITIONS',self.reset_layout).pack(fill='x',pady=3)
        self.status=self.label(self.win,'',MINT,9);self.status.config(wraplength=1300);self.status.pack(fill='x',padx=12,pady=(0,5))
        footer=self.label(self.win,'Primary controller: Native Instruments Maschine Studio  •  Software display mirrors; physical screen output is not connected',CREAM,9);footer.config(wraplength=1300);footer.pack(pady=(0,9))
        self.select(self.selected);self.win.protocol('WM_DELETE_WINDOW',self.close);self.poll()

    def label(self,parent,text,color=CREAM,size=10):return tk.Label(parent,text=text,bg=parent.cget('bg'),fg=color,font=('Segoe UI',size,'bold' if size>=12 else 'normal'),justify='left',wraplength=270)
    def button(self,parent,text,fn):return tk.Button(parent,text=text,command=fn,bg=PANEL,fg=CREAM,activebackground=ORANGE,activeforeground=BG,relief='flat',padx=9,pady=7,font=('Segoe UI',9,'bold'))
    def binding(self,key):
        return next(((address,info) for address,info in self.app.hardware_midi.bindings.items() if info.get('control')==key),(None,None))
    def select(self,key):
        self.selected=key;control=BY_KEY[key];address,info=self.binding(key)
        self.control_label.config(text=key);self.command.set(info['command'] if info else control.command)
        self.mode.set(info['mode'] if info else 'relative_twos_complement' if control.encoder and control.command in ('HW JOG','JOG','LOOP MOVE +','LOOP START +','LOOP END +') else 'button')
        if address:
            kind,channel,number=address.split(':');self.kind.set(kind);self.channel.set(int(channel));self.number.set(int(number))
        self.address_label.config(text=address or 'Unmapped — learn or enter an address')
        self.draw()
    def command_changed(self,event=None):
        command=self.command.get()
        self.mode.set('relative_twos_complement' if command in ('HW JOG','JOG') or command.endswith((' +',' -')) else 'button')
    def learn(self):
        self.app.arm_hardware_learn(self.command.get(),self.mode.get(),self.selected)
    def cancel_learn(self):
        self.app.hardware_learn=None;self.app.hardware_status='Learning cancelled — existing controller map preserved'
    def assign(self):
        try:
            kind=self.kind.get();channel=int(self.channel.get());number=int(self.number.get())
            self.app.hardware_midi.bind(kind,channel,number,self.command.get(),self.mode.get(),self.selected)
            self.app.mapping.pop(f'{"note_on" if kind=="note" else "control_change"}:{channel}:{number}',None)
            self.app.hardware_status='Mapped '+self.selected;self.select(self.selected)
        except (ValueError,TypeError) as exc:messagebox.showerror('Control assignment',str(exc),parent=self.win)
    def test(self):
        command=self.command.get()
        if command in ('HW JOG','JOG'):command+=' +'
        if command=='SHIFT':command='JOG SHIFT'
        self.app.command(command);self.app.hardware_status='Virtual test: '+self.selected+' → '+command
    def unmap(self):
        self.app.hardware_midi.bindings={key:value for key,value in self.app.hardware_midi.bindings.items() if value.get('control')!=self.selected};self.select(self.selected)
    def save(self):
        path=filedialog.asksaveasfilename(parent=self.win,defaultextension='.json',initialfile='TOOLBOXX_Studio_Map.json',filetypes=[('Controller map','*.json')])
        if path:
            try:self.app.hardware_midi.save(path);self.app.hardware_status='Saved editable controller map: '+Path(path).name
            except (OSError,ValueError) as exc:messagebox.showerror('Save map',str(exc),parent=self.win)
    def load(self):
        path=filedialog.askopenfilename(parent=self.win,filetypes=[('Controller map','*.json')])
        if path:
            try:self.app.hardware_midi.load(path);self.select(self.selected);self.app.hardware_status='Loaded controller map: '+Path(path).name
            except (OSError,ValueError) as exc:messagebox.showerror('Load map',str(exc),parent=self.win)
    def load_background(self):
        path=filedialog.askopenfilename(parent=self.win,filetypes=[('Controller photo','*.png *.jpg *.jpeg *.webp')])
        if path:
            try:
                from PIL import Image
                with Image.open(path) as picture:self.background=picture.convert('RGB')
                self._image_size=None;self.draw();self.app.hardware_status='Photo loaded for this window; saved maps retain the editable hotspots'
            except Exception as exc:messagebox.showerror('Controller photo',str(exc),parent=self.win)
    def reset_layout(self):self.app.hardware_midi.surface_layout={};self.draw()
    def dimensions(self):return max(1,self.canvas.winfo_width()),max(1,self.canvas.winfo_height())
    def press(self,event):
        w,h=self.dimensions();key=hit_test(event.x/w,event.y/h,self.app.hardware_midi.surface_layout)
        if key is None:return
        self.select(key)
        if self.edit_layout.get():self.drag=(event.x/w,event.y/h,self.app.hardware_midi.surface_layout.get(key,BY_KEY[key].rect))
    def motion(self,event):
        if self.drag is None or not self.edit_layout.get():return
        w,h=self.dimensions();x,y,rect=self.drag
        self.app.hardware_midi.surface_layout[self.selected]=move_rect(rect,event.x/w-x,event.y/h-y);self.draw()
    def release(self,event):self.drag=None
    def draw(self):
        c=self.canvas;c.delete('all');w,h=self.dimensions()
        c.create_rectangle(.018*w,.018*h,.985*w,.99*h,fill='#252322',outline='#8d6545',width=2)
        from street_visuals import scuffed_metal,skyline
        for y in range(18,int(h*.98),5):c.create_line(.025*w,y,.978*w,y,fill='#292524')
        scuffed_metal(c,.018*w,.018*h,.985*w,.99*h,seed=24,density=330)
        skyline(c,.55*w,.025*h,.97*w,.075*h)
        if self.background:
            from PIL import ImageTk
            if self._image_size!=(w,h):self._photo=ImageTk.PhotoImage(self.background.resize((w,h)));self._image_size=(w,h)
            c.create_image(0,0,image=self._photo,anchor='nw')
        else:c.create_text(.045*w,.045*h,anchor='w',text='TOOLBOXX  /  BOOM BAP',fill=CREAM,font=('Segoe UI',12,'bold'))
        self.draw_screens(w,h)
        for control in CONTROLS:
            rect=self.app.hardware_midi.surface_layout.get(control.key,control.rect);x0,y0,x1,y1=(rect[0]*w,rect[1]*h,rect[2]*w,rect[3]*h)
            selected=control.key==self.selected;address,info=self.binding(control.key)
            edge=MINT if selected else ORANGE if info else '#777078'
            fill='#19171c'
            if control.key.startswith('PAD '):
                index=self.app.bank*16+int(control.key[4:])-1
                fill='#24453e' if index==self.app.selected_pad else ['#3c263e','#25403c','#513d23','#34304d'][int(control.key[4:])%4]
            if control.key=='PLAY':fill='#245445'
            if control.key=='REC':fill='#6b2634'
            shape=c.create_oval if control.encoder or control.key=='JOG PRESS' else c.create_rectangle
            shape(x0,y0,x1,y1,fill=fill,outline=edge,width=3 if selected else 1)
            if not control.encoder:
                c.create_line(x0+3,y0+3,x1-3,y0+3,fill='#69533e')
                c.create_line(x1-12,y1-3,x1-3,y1-3,fill='#47372e')
            if control.key=='JOG ROTATE':
                for inset in (5,10,15):c.create_oval(x0+inset,y0+inset,x1-inset,y1-inset,outline='#514a53')
            c.create_text((x0+x1)/2,(y0+y1)/2,text=control.label,fill=CREAM,font=('Segoe UI',max(6,min(9,int(w/110))),'bold'))
            if self.edit_layout.get() and selected:c.create_rectangle(x0-3,y0-3,x1+3,y1+3,outline=ORANGE,dash=(3,2))
        c.create_text(.045*w,.965*h,anchor='w',text='SELECT TO MAP  •  MINT: SELECTED  •  ORANGE: ASSIGNED',fill=MINT,font=('Segoe UI',8,'bold'))
    def draw_screens(self,w,h):
        c=self.canvas;app=self.app
        for x0,x1 in ((.235,.506),(.516,.796)):c.create_rectangle(x0*w,.135*h,x1*w,.323*h,fill='#0d1116',outline='#655765',width=2)
        left=.245*w;right=.525*w;top=.15*h;width=.25*w;height=.16*h
        c.create_text(left,top,anchor='nw',text=f'SOUND  {app.selected_pad+1:02}  /  BANK {"AB"[app.bank]}',fill=MINT,font=('Segoe UI',9,'bold'))
        sample=app.engine.samples[app.selected_pad]
        if sample:
            data,rate,name=sample;c.create_text(left,top+22,anchor='nw',text=name[:25],fill=CREAM,font=('Segoe UI',8))
            columns=max(1,int(width));mid=top+height*.65
            if getattr(self,'_wave_data',None) is not data or getattr(self,'_wave_columns',None)!=columns:
                self._wave_data=data;self._wave_columns=columns;self._wave_peaks=[]
                for i in range(columns):
                    start=int(i*len(data)/columns);end=max(start+1,int((i+1)*len(data)/columns));chunk=data[start:end]
                    self._wave_peaks.append((min(chunk),max(chunk)) if chunk else (0.,0.))
            for i,(lo,hi) in enumerate(self._wave_peaks):c.create_line(left+i,mid-hi*height*.3,left+i,mid-lo*height*.3,fill=ORANGE)
        else:c.create_text(left,top+height*.55,anchor='w',text='No pad sample loaded',fill=CREAM,font=('Segoe UI',9))
        c.create_text(right,top,anchor='nw',text=f'TRACK CITY / {app.arr.mode}',fill=ORANGE,font=('Segoe UI',9,'bold'))
        c.create_text(right,top+22,anchor='nw',text=f'{app.arr.loop_start/4+1:g} → {app.arr.loop_end/4+1:g} bars  |  {app.bpm:g} BPM',fill=CREAM,font=('Segoe UI',8))
        start=app.arr.loop_start;span=max(16,app.arr.loop_end-start)
        scale=width/span;row=max(5,(height-38)/6)
        for clip in app.arr.clips:
            if clip['track']>5:continue
            a=max(0,clip['start']-start);b=min(span,clip['start']+clip['length']-start)
            if b<=a:continue
            y=top+39+clip['track']*row
            c.create_rectangle(right+a*scale,y,right+b*scale,y+row-2,fill=ORANGE if clip['track']==0 else PURPLE,outline=MINT if clip['id'] in app.arr.selected else '')
        for i,(label,cmd) in enumerate([('MRQ','MODE MRQ'),('TRK','MODE TRK'),('ARR','MODE ARR'),('LOOP','LOOP TOGGLE'),('COPY','RANGE COPY'),('CUT','RANGE CUT'),('DUP','RANGE DUPLICATE'),('INSERT','RANGE INSERT')]):
            c.create_text((.271+i*.069)*w,.118*h,text=label,fill=MINT,font=('Segoe UI',7,'bold'))
    def poll(self):
        if not self.win.winfo_exists():return
        pending=getattr(self.app,'hardware_learn',None)
        if pending and pending.get('batch') and self.selected!=pending['control']:self.select(pending['control'])
        learned=getattr(self.app,'last_hardware_learn',None)
        if learned is not None and learned is not getattr(self,'_last_learned',None):
            self._last_learned=learned
            if learned.get('control') in BY_KEY:self.select(learned['control'])
        self.status.config(text=self.app.hardware_status);self.draw();self._poll_id=self.win.after(250,self.poll)
    def close(self):
        pending=getattr(self.app,'hardware_learn',None)
        if pending and pending.get('control'):self.app.hardware_learn=None
        if hasattr(self,'_poll_id'):self.win.after_cancel(self._poll_id)
        self.win.destroy()
