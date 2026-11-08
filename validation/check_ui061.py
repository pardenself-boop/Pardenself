import sys
from pathlib import Path
sys.path.insert(0,str(Path('app').resolve()))
import tkinter as tk
from types import SimpleNamespace
from toolboxx import App
root=tk.Tk();errors=[];root.report_callback_exception=lambda kind,value,tb:errors.append(value)
app=App(root);app.engine.load(0,'app/AUDIO_TEST.wav');app.open_cookup();root.withdraw();root.update()
window=app.cookup_window
# Loop edge drag is quantized and forms one undo action.
scale=window._loop_scale();initial=(app.arr.loop_start,app.arr.loop_end)
window.loop_press(SimpleNamespace(x=90+app.arr.loop_end*scale))
window.loop_move(SimpleNamespace(x=90+(app.arr.loop_end+1)*scale));window.loop_release(None)
assert len(app.arr.history)==1 and app.arr.loop_end==initial[1]+1
app.arr.undo();assert (app.arr.loop_start,app.arr.loop_end)==initial
app.command('MODE TRK');app.range_editor.set_range(0,2,0,0);app.command('RANGE COPY');app.playhead=12;app.command('RANGE PASTE')
assert any(c['start']==12 for c in app.arr.clips)
app.open_dual_screen();root.update();surface=app.controller_map_window
surface.win.geometry('1420x900+0+0');root.update()
from controller_surface import BY_KEY
w,h=surface.dimensions();rect=BY_KEY['PAD 1'].rect
surface.press(SimpleNamespace(x=(rect[0]+rect[2])*w/2,y=(rect[1]+rect[3])*h/2));assert surface.selected=='PAD 1'
surface.learn();app._enqueue_midi(SimpleNamespace(type='note_on',channel=0,note=60,velocity=100));app._poll();surface.poll();root.update()
assert app.hardware_midi.bindings['note:0:60']['control']=='PAD 1'
app.set_bank(1);app._enqueue_midi(SimpleNamespace(type='note_on',channel=0,note=60,velocity=100));app._poll();assert app.selected_pad==16
app.trigger_absolute_pad(0);surface.poll();root.update()
import subprocess
subprocess.run(['import','-display',':99','-window',str(surface.win.winfo_id()),'/workspace/work/controller-map061.png'],check=True)
surface.close();window.win.lift();root.update()
subprocess.run(['import','-display',':99','-window',str(window.win.winfo_id()),'/workspace/work/arranger061.png'],check=True)
assert not errors,errors
app.close()
print('PASS: real Tk loop undo, track range copy/paste, physical map hit-test, control learn and bank-aware dispatch; no callback errors')
