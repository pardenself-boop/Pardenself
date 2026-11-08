"""Visual Maschine Studio command simulator + editable hardware mapping, Windows Tk."""
import tkinter as tk
from tkinter import ttk, filedialog
from studio_bridge import StudioBridge,CONTROLS,PAGES,PALETTE

class StudioWindow:
    def __init__(self,app):
        self.app=app
        self.win=tk.Toplevel(app.root);self.win.title('TOOLBOXX | Studio Hardware Map / Simulator');self.win.geometry('1130x760');self.win.configure(bg=PALETTE['bg'])
        self.bridge=StudioBridge(self.dispatch)
        self.selected=tk.StringVar(value='PLAY');self.command=tk.StringVar(value='PLAY/STOP');self.shift=tk.BooleanVar(value=False)
        top=tk.Frame(self.win,bg=PALETTE['burgundy']);top.pack(fill='x')
        tk.Label(top,text='BOOM BAP TOOLBOXX  /  STUDIO HARDWARE COMMAND CENTER',fg=PALETTE['cream'],bg=PALETTE['burgundy'],font=('Segoe UI',15,'bold')).pack(side='left',padx=12,pady=10)
        tk.Button(top,text='SAVE PROFILE',command=self.save).pack(side='right',padx=5)
        tk.Button(top,text='LOAD PROFILE',command=self.load).pack(side='right',padx=5)
        nav=tk.Frame(self.win,bg=PALETTE['bg']);nav.pack(fill='x')
        for p in PAGES:tk.Button(nav,text=p,bg=PALETTE['purple'],fg='white',command=lambda p=p:self.dispatch('PAGE:'+p)).pack(side='left',padx=2,pady=5)
        self.shell=tk.Frame(self.win,bg='#302d33',padx=12,pady=12);self.shell.pack(fill='both',expand=True,padx=10,pady=6)
        self.screens=tk.Frame(self.shell,bg='#302d33');self.screens.pack(fill='x')
        self.left=tk.Canvas(self.screens,width=480,height=272,bg='#191821',highlightbackground=PALETTE['mint']);self.left.pack(side='left',padx=10)
        self.right=tk.Canvas(self.screens,width=480,height=272,bg='#191821',highlightbackground=PALETTE['orange']);self.right.pack(side='left',padx=10)
        panel=tk.Frame(self.shell,bg='#302d33');panel.pack(fill='both',expand=True,pady=10)
        controls=tk.Frame(panel,bg='#302d33');controls.pack(side='left',fill='both',expand=True)
        for idx,control in enumerate(CONTROLS):
            bg=PALETTE['burgundy'] if control.startswith('PAD') else PALETTE['purple'] if 'JOG' in control else '#514451'
            b=tk.Button(controls,text=control,width=12,bg=bg,fg=PALETTE['cream'],command=lambda c=control:self.press(c))
            b.grid(row=idx//7,column=idx%7,padx=3,pady=3,ipady=4)
            b.bind('<Button-3>',lambda e,c=control:self.select(c))
        edit=tk.Frame(panel,bg=PALETTE['bg'],padx=10,pady=10);edit.pack(side='right',fill='y')
        tk.Label(edit,text='VISUAL MAP INSPECTOR',fg=PALETTE['mint'],bg=PALETTE['bg'],font=('Segoe UI',12,'bold')).pack()
        ttk.Combobox(edit,textvariable=self.selected,values=CONTROLS,state='readonly',width=23).pack(pady=8)
        ttk.Combobox(edit,textvariable=self.command,values=list(app_command_options()),width=23).pack(pady=8)
        tk.Checkbutton(edit,text='SHIFT LAYER',variable=self.shift,bg=PALETTE['bg'],fg=PALETTE['cream'],selectcolor=PALETTE['burgundy']).pack(pady=5)
        tk.Button(edit,text='ASSIGN MAPPING',command=self.assign,bg=PALETTE['orange']).pack(fill='x',pady=4)
        tk.Label(edit,text='Right-click any hardware button\nto select it for mapping.',fg=PALETTE['cream'],bg=PALETTE['bg'],justify='left').pack(pady=10)
        self.help=tk.Label(self.win,text='JOG ROTATE = navigate / adjust  •  JOG CLICK = select / commit  •  BACK = cancel  •  SHIFT = fine steps',fg=PALETTE['cream'],bg=PALETTE['bg']);self.help.pack()
        self.status=tk.Label(self.win,text='SIMULATOR READY — physical USB not connected',fg=PALETTE['mint'],bg=PALETTE['bg']);self.status.pack()
        self.refresh()
    def select(self,control):self.selected.set(control);self.command.set(self.bridge.mappings.get(control,''))
    def assign(self):
        self.bridge.map_control(self.selected.get(),self.command.get(),self.shift.get())
        self.status.config(text='MAPPED '+self.selected.get()+' → '+self.command.get())
    def press(self,control):
        result=self.bridge.event(control)
        self.status.config(text=f'{control} → {result or "UNMAPPED"}');self.refresh()
    def dispatch(self,command):
        if command.startswith('PAGE:'):
            page=command[5:]
            if page in self.app_pages():self.app.set_page(self.app_pages().index(page))
            else:self.status.config(text=page+' / reserved page')
        elif command.startswith('BANK:'):self.app.set_bank(int(command[5:]))
        elif command=='JOG SHIFT':self.app.command(command)
        elif command=='DUPLICATE':self.app.duplicate()
        else:self.app.command(command)
        self.refresh()
    def app_pages(self):return list(self.app_pages_source())
    def app_pages_source(self):
        from toolboxx import PAGES as BASE_PAGES
        return BASE_PAGES
    def save(self):
        p=filedialog.asksaveasfilename(defaultextension='.json',filetypes=[('JSON','*.json')]);
        if p:self.bridge.save(p)
    def load(self):
        p=filedialog.askopenfilename(filetypes=[('JSON','*.json')]);
        if p:self.bridge.load(p);self.refresh()
    def refresh(self):
        if not self.win.winfo_exists():return
        a=self.app;cream=PALETTE['cream'];mint=PALETTE['mint'];orange=PALETTE['orange']
        for c in (self.left,self.right):c.delete('all')
        self.left.create_text(18,18,anchor='nw',text=('CHOP LABB / WAVEFORM' if a.page==1 else 'STUDIO / '+self.app_pages()[a.page]),fill=mint,font=('Segoe UI',16,'bold'))
        self.left.create_text(18,53,anchor='nw',text=f'BANK {chr(65+a.bank)}    PAD {a.selected_pad+1:02d}    BPM {a.bpm}',fill=cream,font=('Consolas',13))
        import math
        coords=[]
        for x in range(16,465,3):
            amp=15+43*abs(math.sin(x*.052)*math.sin(x*.013));coords.extend([x,168+math.sin(x*.38)*amp])
        self.left.create_line(*coords,fill=orange,width=2)
        for x in range(55,480,80):self.left.create_line(x,100,x,235,fill=mint,dash=(3,6))
        self.left.create_text(18,250,anchor='nw',text='VIRTUAL WAVEFORM • load sample in DAW',fill=cream)
        self.right.create_text(18,18,anchor='nw',text=f'TRACK CITY / {a.arr.mode}',fill=orange,font=('Segoe UI',16,'bold'))
        self.right.create_text(18,48,anchor='nw',text=f'LOOP {a.arr.loop_start:.2f} → {a.arr.loop_end:.2f} BEATS   JOG {a.jog_modes[a.jog_mode]}',fill=cream)
        scale=20
        self.right.create_line(80,85,460,85,fill=mint,width=3)
        for i in range(4):
            y=100+i*35;self.right.create_rectangle(15,y,465,y+30,fill='#2b2732',outline='')
            self.right.create_text(18,y+7,anchor='nw',text=['DRUM','CHOP','BASS','KEYS'][i],fill=cream)
        for clip in a.arr.clips:
            if clip['track']>3:continue
            x=85+clip['start']*scale;y=100+clip['track']*35
            self.right.create_rectangle(x,y+3,min(460,x+clip['length']*scale),y+27,fill=orange if clip['track']==0 else PALETTE['purple'],outline=mint if clip['id'] in a.arr.selected else '')
        focused=a.hardware_edit.current()
        if focused and focused['track']<=3:
            fx=85+focused['start']*scale;fy=100+focused['track']*35
            self.right.create_rectangle(fx-2,fy+1,min(462,fx+focused['length']*scale+2),fy+29,outline=mint,width=2,dash=(3,2))
        self.right.create_line(85+a.playhead*scale,82,85+a.playhead*scale,240,fill=cream,dash=(3,3))
        self.right.create_text(18,250,anchor='nw',text=(f'LABB {a.labbs.selected+1}/22 {__import__("labb_engine").LABBS[a.labbs.selected].name} | '+a.hardware_edit.describe())[:66],fill=mint,font=('Consolas',10))

def app_command_options():
    from toolboxx import COMMANDS
    return COMMANDS+['DUPLICATE']
