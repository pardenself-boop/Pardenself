"""Independent mix-rack control surface. Configuration only, not audio DSP."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from mix_rack import MODULES, MixRack

BG='#17151c'; PANEL='#28212d'; FG='#f3e5c9'; ACCENT='#8ce3c9'; ORANGE='#d7773d'
class MixRackWindow:
    def __init__(self, app):
        self.app=app
        self.win=tk.Toplevel(app.root)
        self.win.title('TOOLBOXX | MODULAR MIX RACK | CONFIGURATION')
        self.win.geometry('780x650');self.win.configure(bg=BG)
        head=tk.Frame(self.win,bg=BG);head.pack(fill='x',padx=12,pady=10)
        tk.Label(head,text='MODULAR MIX RACK',fg=ACCENT,bg=BG,font=('Segoe UI',17,'bold')).pack(side='left')
        self.kind=tk.StringVar(value='eq')
        ttk.Combobox(head,textvariable=self.kind,values=list(MODULES),state='readonly',width=15).pack(side='left',padx=12)
        tk.Button(head,text='+ ADD',command=self.add,bg=ORANGE).pack(side='left')
        tk.Button(head,text='SAVE PRESET',command=self.save,bg=PANEL,fg=FG).pack(side='right')
        tk.Button(head,text='LOAD PRESET',command=self.load,bg=PANEL,fg=FG).pack(side='right',padx=5)
        tk.Label(self.win,text='Hide = panel only  •  Bypass = processing state  •  MIDI target: mix.INDEX.parameter',bg=BG,fg=FG).pack(anchor='w',padx=14)
        tk.Label(self.win,text='CONFIGURATION ONLY — DSP NOT CONNECTED',bg=BG,fg=ORANGE).pack(anchor='w',padx=14,pady=5)
        outer=tk.Frame(self.win,bg=BG);outer.pack(fill='both',expand=True)
        self.canvas=tk.Canvas(outer,bg=BG,highlightthickness=0)
        scrollbar=tk.Scrollbar(outer,command=self.canvas.yview);scrollbar.pack(side='right',fill='y')
        self.canvas.pack(side='left',fill='both',expand=True);self.canvas.configure(yscrollcommand=scrollbar.set)
        self.frame=tk.Frame(self.canvas,bg=BG);self.canvas.create_window((0,0),window=self.frame,anchor='nw')
        self.frame.bind('<Configure>',lambda e:self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.refresh()
    def add(self):self.app.mix_rack.add(self.kind.get());self.refresh()
    def save(self):
        path=filedialog.asksaveasfilename(parent=self.win,defaultextension='.json',filetypes=[('TOOLBOXX rack preset','*.json')])
        if path:
            with open(path,'w',encoding='utf8') as f:f.write(self.app.mix_rack.to_json())
    def load(self):
        path=filedialog.askopenfilename(parent=self.win,filetypes=[('TOOLBOXX rack preset','*.json')])
        if path:
            try:
                with open(path,encoding='utf8') as f:rack=MixRack.from_json(f.read())
                self.app.mix_rack=rack;self.refresh()
            except (OSError,ValueError,TypeError,KeyError) as e:messagebox.showerror('Invalid rack preset',str(e),parent=self.win)
    def toggle(self,i,attr,var):
        setattr(self.app.mix_rack.modules[i],attr,bool(var.get()))
        self.refresh()
    def move(self,i,d):
        j=i+d
        if 0<=j<len(self.app.mix_rack.modules):self.app.mix_rack.move(i,j);self.refresh()
    def param(self,i,name,value):
        self.app.mix_rack.set_parameter(i,name,float(value))
    def refresh(self):
        for w in self.frame.winfo_children():w.destroy()
        for i,m in enumerate(self.app.mix_rack.modules):
            box=tk.Frame(self.frame,bg=PANEL,bd=1,relief='ridge');box.pack(fill='x',padx=12,pady=6)
            header=tk.Frame(box,bg=PANEL);header.pack(fill='x')
            tk.Label(header,text=f'{i+1:02d}  {m.kind.upper()}',fg=ACCENT,bg=PANEL,font=('Segoe UI',12,'bold')).pack(side='left',padx=10)
            for label,attr in [('ACTIVE','enabled'),('SHOW','visible')]:
                v=tk.BooleanVar(value=getattr(m,attr))
                tk.Checkbutton(header,text=label,variable=v,command=lambda i=i,a=attr,v=v:self.toggle(i,a,v),bg=PANEL,fg=FG,selectcolor=BG,activebackground=PANEL).pack(side='left',padx=6)
            for label,d in [('↑',-1),('↓',1)]:tk.Button(header,text=label,command=lambda i=i,d=d:self.move(i,d),bg=BG,fg=FG).pack(side='right')
            if m.visible:
                for name,(lo,hi,_) in MODULES[m.kind].items():
                    row=tk.Frame(box,bg=PANEL);row.pack(fill='x',padx=12)
                    tk.Label(row,text=name.replace('_',' ').upper(),width=18,anchor='w',bg=PANEL,fg=FG).pack(side='left')
                    scale=tk.Scale(row,from_=lo,to=hi,resolution=.01,orient='horizontal',length=360,bg=PANEL,fg=FG,highlightthickness=0,command=lambda v,i=i,n=name:self.param(i,n,v))
                    scale.set(m.params[name]);scale.pack(side='left')
                    tk.Label(row,text=f'mix.{i}.{name}',fg=ACCENT,bg=PANEL).pack(side='left',padx=8)
