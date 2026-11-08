"""STREET TAP / CRATE BLOCK window; isolated from the main MPC layout."""
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import webbrowser
from pathlib import Path
from street_capture import StreetTap, CrateIndex

class StreetCaptureWindow:
    def __init__(self, app):
        self.app = app
        self.tap = StreetTap()
        self.crate = CrateIndex()
        self.win = tk.Toplevel(app.root)
        self.win.title('BOOM BAP TOOLBOXX | STREET TAP + CRATE BLOCK')
        self.win.geometry('800x620')
        self.win.configure(bg='#17121d')
        self.win.protocol('WM_DELETE_WINDOW', self.close)
        self.devices = []
        self.device_var = tk.StringVar()
        self.name_var = tk.StringVar(value='New Street Sample')
        self.status = tk.StringVar(value='Ready — select a Windows output, then press RECORD')
        self._make_ui()
        self.refresh_devices()
        self.refresh_crate()
        self.poll()

    def _make_ui(self):
        bg='#17121d'; fg='#f3e5c9'; accent='#ed8237'
        def label(parent, text):return tk.Label(parent,text=text,bg=bg,fg=fg,font=('Segoe UI',10))
        label(self.win,'STREET TAP  /  WINDOWS SYSTEM AUDIO').pack(anchor='w',padx=18,pady=(16,6))
        label(self.win,'Record audio you have permission to use. Protected streams may not be available.').pack(anchor='w',padx=18)
        bar=tk.Frame(self.win,bg=bg);bar.pack(fill='x',padx=18,pady=8)
        self.device_menu=tk.OptionMenu(bar,self.device_var,'No device');self.device_menu.pack(side='left',fill='x',expand=True)
        tk.Button(bar,text='REFRESH OUTPUTS',command=self.refresh_devices).pack(side='left',padx=5)
        line=tk.Frame(self.win,bg=bg);line.pack(fill='x',padx=18,pady=6)
        label(line,'Sample name:').pack(side='left')
        tk.Entry(line,textvariable=self.name_var,width=34).pack(side='left',padx=8)
        tk.Button(line,text='● RECORD',command=self.start,bg=accent).pack(side='left',padx=5)
        tk.Button(line,text='■ STOP / SAVE',command=self.stop).pack(side='left')
        label(self.win,'No input monitoring (prevents audio feedback). Recording limit: 10 minutes.').pack(anchor='w',padx=18)
        tk.Label(self.win,textvariable=self.status,bg=bg,fg='#8ce3c9',wraplength=740).pack(anchor='w',padx=18,pady=8)
        tk.Button(self.win,text='OPEN CAPTURE FOLDER',command=self.open_recordings).pack(anchor='w',padx=18)
        label(self.win,'CRATE BLOCK  /  SAMPLE SITES + DOWNLOADS').pack(anchor='w',padx=18,pady=(18,6))
        tools=tk.Frame(self.win,bg=bg);tools.pack(fill='x',padx=18)
        for title,fn in [('ADD SITE',self.add_site),('ADD DOWNLOAD FOLDER',self.add_folder),('REFRESH',self.refresh_crate),('OPEN SELECTED',self.open_selected)]:
            tk.Button(tools,text=title,command=fn).pack(side='left',padx=4)
        self.listbox=tk.Listbox(self.win,bg='#211721',fg=fg,selectbackground='#81374f',height=12)
        self.listbox.pack(fill='both',expand=True,padx=18,pady=8)
        self.entries=[]
        self.listbox.bind('<Double-1>',lambda e:self.open_selected())

    def refresh_devices(self):
        try:
            self.devices=self.tap.devices()
            menu=self.device_menu['menu'];menu.delete(0,'end')
            for identifier,name in self.devices:
                menu.add_command(label=name,command=lambda n=name:self.device_var.set(n))
            self.device_var.set(self.devices[0][1] if self.devices else 'No Windows outputs')
        except Exception as exc:
            self.devices=[]
            self.device_var.set('Loopback unavailable')
            self.status.set(f'Install soundcard + numpy in the Windows build: {exc}')

    def start(self):
        item=next((i for i in self.devices if i[1]==self.device_var.get()),None)
        if not item:
            messagebox.showerror('STREET TAP','Select a valid Windows output device.',parent=self.win);return
        try:self.tap.start(item[0],self.name_var.get())
        except Exception as exc:messagebox.showerror('STREET TAP',str(exc),parent=self.win)

    def stop(self):
        self.tap.stop()
        self.status.set(f'{self.tap.status}: {self.tap.last_file or self.tap.error or ""}')
        self.refresh_crate()
        if self.tap.last_file:
            try:
                self.app.engine.load(self.app.selected_pad, str(self.tap.last_file))
                self.status.set(f'Loaded recording to PAD {self.app.selected_pad + 1}: {self.tap.last_file.name}')
                self.app._refresh()
            except Exception as exc:
                self.status.set(f'Saved WAV, but pad load failed: {exc}')

    def poll(self):
        if not self.win.winfo_exists():return
        self.status.set(f'{self.tap.status}  |  {self.tap.frames / 48000:.1f}s  |  {self.tap.last_file or self.tap.error or ""}')
        self.win.after(350,self.poll)

    def open_recordings(self):
        self.tap.output_dir.mkdir(parents=True,exist_ok=True)
        import os
        os.startfile(str(self.tap.output_dir)) if hasattr(os,'startfile') else messagebox.showinfo('Folder',str(self.tap.output_dir),parent=self.win)

    def add_site(self):
        url=simpledialog.askstring('Add sample site','Website URL (https://...):',parent=self.win)
        if not url:return
        name=simpledialog.askstring('Name','Name for this sample site:',parent=self.win) or ''
        try:self.crate.add_site(name,url);self.refresh_crate()
        except ValueError as exc:messagebox.showerror('Invalid site',str(exc),parent=self.win)

    def add_folder(self):
        folder=filedialog.askdirectory(parent=self.win,title='Choose downloads or sample folder')
        if folder:self.crate.add_folder(folder);self.refresh_crate()

    def refresh_crate(self):
        self.entries=[];self.listbox.delete(0,'end')
        for site in self.crate.sites:self.entries.append(('site',site['url']));self.listbox.insert('end','🌐  '+site['name'])
        for folder in self.crate.folders:self.entries.append(('folder',folder));self.listbox.insert('end','📁  '+folder)
        for sample in self.crate.samples():self.entries.append(('sample',str(sample)));self.listbox.insert('end','♫  '+sample.name)
        for wav in sorted(self.tap.output_dir.glob('*.wav')) if self.tap.output_dir.exists() else []:
            self.entries.append(('sample',str(wav)));self.listbox.insert('end','●  '+wav.name)

    def open_selected(self):
        chosen=self.listbox.curselection()
        if not chosen:return
        kind,value=self.entries[chosen[0]]
        if kind=='site':webbrowser.open(value)
        else:
            import os
            if hasattr(os,'startfile'):os.startfile(value)
            else:messagebox.showinfo('File location',value,parent=self.win)

    def close(self):
        self.tap.stop()
        self.win.destroy()
