"""22-suite hardware-first browser, shared state with the DAW."""
import tkinter as tk
from suite_registry import SUITES

COLORS={'mint':'#8ce3c9','orange':'#d7773d','burgundy':'#81374f','cream':'#f3e5c9','purple':'#7043ad'}
class SuiteWindow:
    def __init__(self,app):
        self.app=app;self.win=tk.Toplevel(app.root);self.win.title('TOOLBOXX / 22 SUITES');self.win.geometry('870x650');self.win.configure(bg='#17151c')
        self.list=tk.Listbox(self.win,bg='#28212d',fg=COLORS['cream'],selectbackground=COLORS['purple'],font=('Segoe UI',12),width=34,activestyle='none',exportselection=False)
        self.list.pack(side='left',fill='both',expand=True,padx=12,pady=12)
        for i,s in enumerate(SUITES):self.list.insert('end',f'{i+1:02d}   {s.name}')
        self.list.bind('<<ListboxSelect>>',self.on_select)
        right=tk.Frame(self.win,bg='#17151c');right.pack(side='right',fill='both',expand=True,padx=12,pady=12)
        self.title=tk.Label(right,bg='#17151c',fg=COLORS['mint'],font=('Segoe UI',18,'bold'),wraplength=380);self.title.pack(anchor='w',pady=15)
        self.detail=tk.Label(right,bg='#17151c',fg=COLORS['cream'],font=('Segoe UI',12),justify='left',wraplength=360);self.detail.pack(anchor='w',pady=15)
        tk.Label(right,text='JOG = navigate  •  CLICK = open\nBACK = return to Track City',bg='#17151c',fg=COLORS['orange']).pack(anchor='w',pady=15)
        tk.Button(right,text='OPEN FOCUSED SUITE',command=self.open_suite,bg=COLORS['orange']).pack(fill='x',pady=6)
        tk.Button(right,text='TRACK CITY',command=lambda:self.app.command('SUITE OPEN 1'),bg=COLORS['purple'],fg='white').pack(fill='x')
        self.refresh()
    def on_select(self,_):
        if self.list.curselection():self.app.suites.select(self.list.curselection()[0]);self.refresh()
    def open_suite(self):self.app.command('SUITE OPEN')
    def refresh(self):
        if not self.win.winfo_exists():return
        i=self.app.suites.focus;s=SUITES[i];self.list.selection_clear(0,'end');self.list.selection_set(i);self.list.see(i)
        self.title.config(text=s.name)
        self.detail.config(text=f'FAMILY: {s.family}\nIMPLEMENTATION: {s.implementation.upper()}\n\n{s.purpose}\n\nAll suites share the TOOLBOXX project. Planned suites are navigation placeholders, not completed DSP.')
