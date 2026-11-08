import sys
from pathlib import Path
sys.path.insert(0,str(Path('app').resolve()))
import tkinter as tk
from toolboxx import App
root=tk.Tk();errors=[]
root.report_callback_exception=lambda kind,value,tb:errors.append(value)
app=App(root);app.open_cookup();root.withdraw()
window=app.cookup_window;window.win.geometry('1680x1050+0+0');root.update()
app.engine.load(0,'app/AUDIO_TEST.wav');window.refresh();root.update()
height=window.pad_deck.winfo_height()
window.pad_deck.event_generate('<Button-1>',x=15,y=height-10,time=1000);root.update()
assert app.selected_pad==0 and app.engine.voices
window.bank(1);root.update()
window.pad_deck.event_generate('<Button-1>',x=15,y=height-10,time=2000);root.update()
assert app.selected_pad==16
# Edit selected bank's first pad through the actual step matrix binding.
window.matrix.event_generate('<Button-1>',x=50,y=15);root.update()
assert app.patterns['main'][16][0]
app.trigger_absolute_pad(0);window.poll();root.update()
assert window._pad_view_state[0]==0
app.open_hardware_setup();root.update()
for child in root.winfo_children():
 if isinstance(child,tk.Toplevel) and child is not window.win:child.destroy()
window.win.lift();root.update()
assert not errors,errors
import subprocess
subprocess.run(['import','-display',':99','-window',str(window.win.winfo_id()),'/workspace/work/cookup-ui059.png'],check=True)
app.close()
print('PASS: Tk pad clicks, banks A/B, step edit, hardware-triggered selection, Maschine setup window; no callback errors')
