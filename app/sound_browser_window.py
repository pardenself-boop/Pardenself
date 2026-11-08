"""TOOLBOXX instrument/preset browser and real sound-parameter editor."""
import tkinter as tk
from tkinter import ttk,messagebox
from labb_engine import LABBS
from street_sounds import SOUNDS,apply_sound
from street_patch_vault import StreetPatchVault
from surface_context import SOUND_PARAMS

BG='#100f10';PANEL='#27211d';MINT='#82ceb5';ORANGE='#e38b42';CREAM='#e6d2b3'

class SoundBrowserWindow:
    def __init__(self,app):
        self.app=app;self.win=tk.Toplevel(app.root);self.win.title('TOOLBOXX | Street Banks / Sound Editor');self.win.geometry('1060x650');self.win.configure(bg=BG);self.loading=False;self._display_percent={}
        top=tk.Frame(self.win,bg=PANEL);top.pack(fill='x')
        tk.Label(top,text='STREET BANKS / SOUND WORKSHOP',font=('Segoe UI',17,'bold'),bg=PANEL,fg=CREAM).pack(side='left',padx=14,pady=13)
        for label,fn in [('START AUDIO',app.start_audio),('FX CHAIN',app.open_mix_rack),('AUDITION',lambda:app.labbs.note_on(48))]:tk.Button(top,text=label,command=fn,bg=PANEL,fg=CREAM).pack(side='right',padx=5)
        left=tk.Frame(self.win,bg=PANEL,width=280);left.pack(side='left',fill='y',padx=12,pady=12)
        tk.Label(left,text='OUR 22 LABBS',bg=PANEL,fg=MINT,font=('Segoe UI',11,'bold')).pack(pady=8)
        self.list=tk.Listbox(left,bg=BG,fg=CREAM,selectbackground='#713a33',width=28,height=23,exportselection=False);self.list.pack(fill='both',expand=True)
        for i,labb in enumerate(LABBS):self.list.insert('end',f'{i+1:02}  {labb.name}')
        self.list.bind('<<ListboxSelect>>',self.select)
        right=tk.Frame(self.win,bg=BG);right.pack(side='left',fill='both',expand=True,padx=14,pady=12)
        tk.Label(right,text='ORIGINAL NYC STARTING POINTS',bg=BG,fg=MINT).pack(anchor='w')
        self.preset=tk.StringVar(value=SOUNDS[0][0]);combo=ttk.Combobox(right,textvariable=self.preset,values=[p[0] for p in SOUNDS],state='readonly');combo.pack(fill='x',pady=7);combo.bind('<<ComboboxSelected>>',self.factory)
        self.title=tk.Label(right,bg=BG,fg=ORANGE,font=('Segoe UI',20,'bold'));self.title.pack(anchor='w',pady=9)
        grid=tk.Frame(right,bg=BG);grid.pack(fill='x');self.scales=[]
        for i,(label,_,lo,hi) in enumerate(SOUND_PARAMS):
            scale=tk.Scale(grid,from_=0,to=100,resolution=1,label=label,orient='horizontal',length=300,bg=PANEL,fg=CREAM,highlightthickness=0,command=lambda value,index=i:self.parameter(index,value))
            scale.grid(row=i//2,column=i%2,padx=5,pady=6,sticky='ew');self.scales.append(scale)
        grid.grid_columnconfigure(0,weight=1);grid.grid_columnconfigure(1,weight=1)
        self.vault=StreetPatchVault();tk.Label(right,text='USER PATCH MEMORY',bg=BG,fg=MINT).pack(anchor='w',pady=(14,3))
        row=tk.Frame(right,bg=BG);row.pack(fill='x');self.patch=tk.StringVar(value='My Street Patch')
        self.patches=ttk.Combobox(row,textvariable=self.patch,width=35);self.patches.pack(side='left',fill='x',expand=True)
        for label,fn in [('STORE',self.store),('RECALL',self.recall)]:tk.Button(row,text=label,command=fn,bg=PANEL,fg=CREAM).pack(side='left',padx=5)
        self.info=tk.Label(right,text='These are TOOLBOXX sounds and patches; no NI expansion files are loaded.',bg=BG,fg=CREAM,wraplength=630,justify='left');self.info.pack(anchor='w',pady=12)
        self.win.protocol('WM_DELETE_WINDOW',self.close);self._last=None;self.refresh();self.poll()
    def select(self,event=None):
        indices=self.list.curselection()
        if indices:self.app.labbs.selected=indices[0];self.app.notes.armed_labb=indices[0];self.refresh()
    def factory(self,event=None):
        index=[p[0] for p in SOUNDS].index(self.preset.get());apply_sound(self.app.labbs,index);self.app.notes.armed_labb=self.app.labbs.selected;self.app.surface_context.sound_index=index;self.refresh()
    def parameter(self,index,percent):
        if self.loading or self._display_percent.get(index)==float(percent):return
        self._display_percent[index]=float(percent)
        _,key,lo,hi=SOUND_PARAMS[index];value=lo+(hi-lo)*float(percent)/100;i=self.app.labbs.selected
        if key is None:self.app.labbs.volume[i]=value
        elif key=='master':self.app.labbs.master.drive=value
        else:self.app.labbs.set_parameter(i,key,value)
    def store(self):
        try:self.vault.save(self.app.labbs,self.app.labbs.selected,self.patch.get());self.refresh();self.info.config(text='Stored our patch: '+self.patch.get())
        except (OSError,ValueError) as exc:messagebox.showerror('Store patch',str(exc),parent=self.win)
    def recall(self):
        try:self.vault.load(self.app.labbs,self.app.labbs.selected,self.patch.get());self.refresh()
        except (OSError,ValueError) as exc:messagebox.showerror('Recall patch',str(exc),parent=self.win)
    def refresh(self):
        i=self.app.labbs.selected;self.title.config(text=LABBS[i].name.upper());self.list.selection_clear(0,'end');self.list.selection_set(i);self.list.see(i)
        self.loading=True
        for index,(_,key,lo,hi) in enumerate(SOUND_PARAMS):
            value=self.app.labbs.volume[i] if key is None else self.app.labbs.master.drive if key=='master' else self.app.labbs.parameters[i][key]
            percent=round((value-lo)*100/(hi-lo));self._display_percent[index]=percent;self.scales[index].set(percent)
        self.loading=False;self.patches['values']=self.vault.names(i);self._last=self.signature()
    def signature(self):
        i=self.app.labbs.selected;return (i,tuple(self.app.labbs.parameters[i].items()),self.app.labbs.volume[i],self.app.labbs.master.drive)
    def poll(self):
        if not self.win.winfo_exists():return
        if self.signature()!=self._last:self.refresh()
        self._poll_id=self.win.after(250,self.poll)
    def close(self):
        if hasattr(self,'_poll_id'):self.win.after_cancel(self._poll_id)
        self.win.destroy()
