import sys
from pathlib import Path
sys.path.insert(0,str(Path('app').resolve()))
import tkinter as tk
root=tk.Tk();errors=[];root.report_callback_exception=lambda kind,value,tb:errors.append(value)
from toolboxx import App
app=App(root);root.withdraw();before=app.labbs.serialize();app.open_sound_browser();root.update()
assert app.labbs.serialize()==before,'UI startup changed audio parameters'
browser=app.sound_browser_window;browser.preset.set('Brownstone Keys');browser.factory();root.update()
assert app.labbs.selected==7 and app.labbs.parameters[7]['release']==.8
app.open_mix_rack()
for kind in ('eq','density','clipper'):app.mix_rack.add(kind)
app.mix_rack_window.refresh();root.update()
assert app.engine.mix_rack is app.mix_rack
app.open_dual_screen();root.update();surface=app.controller_map_window;surface.win.geometry('1480x960+0+0');surface.win.lift();root.update()
import subprocess
subprocess.run(['import','-display',':99','-window',str(surface.win.winfo_id()),'/workspace/work/controller-fx061.png'],check=True)
browser.win.lift();root.update()
subprocess.run(['import','-display',':99','-window',str(browser.win.winfo_id()),'/workspace/work/sound-browser061.png'],check=True)
assert not errors,errors
app.close();print('PASS: sound editor opens without patch mutation; original preset loads; FX shares audio engine; contextual display renders; no callback errors')
