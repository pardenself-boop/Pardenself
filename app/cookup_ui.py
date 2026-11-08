"""TOOLBOXX COOK UP v1.5: real Tkinter custom interface, shared App state.
Visual meters, wave and FX slots are identified where illustrative; no fabricated DSP.
"""
import math, tkinter as tk
from pathlib import Path
from labb_engine import LABBS
from feature_registry import FEATURES, AVAILABLE, read_visibility, write_visibility
BG='#100f10'; PANEL='#24201e'; PANEL2='#161516'; MINT='#82ceb5'; ORANGE='#e38b42'; BURG='#713a33'; CREAM='#e6d2b3'; PURPLE='#775c8c'; DIM='#ad9a84'
COLORS=[ORANGE,MINT,PURPLE,BURG,MINT,ORANGE]
ORB_NAMES=['HISTORY','SOUL','JAZZ','DEEP','DUST','SPACE','TAPE','VINYL']

class CookUpWindow:
 def __init__(self,app):
  self.app=app;self.win=tk.Toplevel(app.root);self.win.title('BOOM BAP TOOLBOXX | COOK UP MATRIX | BUILD 061');self.win.geometry('1500x900');self.win.minsize(1050,680);self.win.configure(bg=BG);self.win.after_idle(self._maximize)
  self.selected_orb=1;self.arr_view_start=0.0;self.arr_zoom=1.0;self.mouse_pan_anchor=None;self.loop_drag=None;self.range_drag=None;self.macro=app.labbs.orbs;self.matrix_page=0;self.current_suite=app.labbs.selected;self._build();self.refresh()
  self.win.bind('<Escape>',lambda e:self.win.destroy());self.win.bind('<Control-z>',lambda e:self.act('UNDO'));
  for key,cmd in [('<Control-c>','RANGE COPY'),('<Control-x>','RANGE CUT'),('<Control-v>','RANGE PASTE'),('<Control-d>','RANGE DUPLICATE'),('<Delete>','RANGE DELETE')]:self.win.bind(key,lambda e,c=cmd:self.act(c))
  self.win.after(200,self.poll)
 def _maximize(self):
  try:self.win.state('zoomed')
  except tk.TclError:
   try:self.win.attributes('-zoomed',True)
   except tk.TclError:pass
 def txt(self,p,s,size=10,color=CREAM,bold=False):return tk.Label(p,text=s,bg=p.cget('bg'),fg=color,font=('Segoe UI',size,'bold' if bold else 'normal'))
 def button(self,p,s,fn,color=PANEL):return tk.Button(p,text=s,command=fn,bg=color,fg=CREAM,activebackground=ORANGE,activeforeground=BG,relief='ridge',font=('Segoe UI',9,'bold'),padx=9,pady=5,cursor='hand2',bd=1,highlightthickness=0)
 def section(self,p,label,color=MINT):
  f=tk.Frame(p,bg=PANEL);f.pack(fill='x',pady=(7,3));self.txt(f,'◆ '+label,10,color,True).pack(anchor='w',padx=10,pady=5);return f
 def grid_section(self,p,row,label,color=MINT):
  f=tk.Frame(p,bg=PANEL);f.grid(row=row,column=0,sticky='ew',pady=(3,1));self.txt(f,'◆ '+label,10,color,True).pack(anchor='w',padx=10,pady=3)
 def _build(self):
  h=tk.Frame(self.win,bg='#261720',height=65);h.pack(fill='x');h.pack_propagate(False)
  self.txt(h,'◈  BOOM BAP TOOLBOXX',19,CREAM,True).pack(side='left',padx=14,pady=9)
  self.txt(h,'SOUND LABB DIVISION  /  COOK UP MATRIX',9,MINT,True).pack(side='left',padx=9)
  # Persistent transport remains visible when browsing instruments.
  for label,cmd in [('▶ PLAY/PAUSE','PLAY/STOP'),('● REC','RECORD')]:
   self.button(h,label,lambda c=cmd:self.act(c),ORANGE if label.startswith('▶') else PANEL2).pack(side='left',padx=3)
  self.tempo_label=self.txt(h,'',10,CREAM,True);self.tempo_label.pack(side='left',padx=7)
  for t,f in [('SAVE',self.app.save),('LOAD',self.app.load),('STUDIO',self.app.open_studio),('STUDIO MAP',self.app.open_dual_screen),('MIX RACK',self.app.open_mix_rack),('MENU',self.open_feature_menu),('DAW',self.app.root.lift)]:self.button(h,t,f).pack(side='right',padx=3)
  self.art=tk.Canvas(self.win,height=76,bg=BG,highlightthickness=0);self.art.pack(fill='x',padx=10,pady=(5,2));self.art.bind('<Configure>',self.draw_banner)
  mid=tk.Frame(self.win,bg=BG);mid.pack(fill='both',expand=True,padx=8,pady=3)
  self.main_columns=mid
  side=tk.Frame(mid,bg=PANEL,width=230);side.pack(side='left',fill='y',padx=(0,7));side.pack_propagate(False)
  self.txt(side,'22 INSTRUMENT LABBS',12,MINT,True).pack(anchor='w',padx=9,pady=11)
  self.labb_list=tk.Listbox(side,bg=PANEL2,fg=CREAM,selectbackground=ORANGE,selectforeground=BG,highlightthickness=0,relief='flat',font=('Segoe UI',10),exportselection=False,activestyle='none',bd=0)
  self.labb_list.pack(fill='both',expand=True,padx=8,pady=4)
  for i,l in enumerate(LABBS):self.labb_list.insert('end',f' {i+1:02}  {l.name.upper()}')
  self.labb_list.bind('<<ListboxSelect>>',self.select_suite)
  self.labb_status=self.txt(side,'',9,MINT);self.labb_status.pack(anchor='w',padx=9,pady=6)
  self.instrument_sidebar=side
  center=tk.Frame(mid,bg=BG);center.pack(side='left',fill='both',expand=True);center.grid_columnconfigure(0,weight=1);center.grid_rowconfigure(5,weight=3);center.grid_rowconfigure(7,weight=5);center.grid_rowconfigure(10,weight=2)
  inst=tk.Frame(center,bg=PANEL);inst.grid(row=0,column=0,sticky='ew')
  self.labb_title=self.txt(inst,'KEY 88 LABB',19,CREAM,True);self.labb_title.pack(side='left',padx=12,pady=9)
  self.txt(inst,'ENGINE  •  WAVE  •  MIDI  •  FX  •  MOD',9,ORANGE,True).pack(side='right',padx=10)
  self.instrument_header=inst
  self.orbs=tk.Canvas(center,height=86,bg=PANEL,highlightthickness=0);self.orbs.grid(row=1,column=0,sticky='ew',pady=(3,2));self.orbs.bind('<Configure>',lambda e:self.draw_orbs());self.orbs.bind('<Button-1>',self.orb_click);self.orbs.bind('<MouseWheel>',self.orb_scroll)
  wavebox=tk.Frame(center,bg=PANEL);wavebox.grid(row=2,column=0,sticky='ew',pady=2)
  self.pad_deck=tk.Canvas(wavebox,width=184,height=110,bg=PANEL2,highlightthickness=0,cursor='hand2');self.pad_deck.pack(side='left',fill='y',padx=5,pady=5);self.pad_deck.bind('<Configure>',lambda e:self.draw_pad_deck());self.pad_deck.bind('<Button-1>',self.pad_click);self.pad_deck.bind('<Double-Button-1>',self.pad_load)
  self.wave=tk.Canvas(wavebox,height=110,bg=PANEL2,highlightthickness=0);self.wave.pack(side='left',fill='both',expand=True,padx=5,pady=5);self.wave.bind('<Configure>',lambda e:self.draw_wave())
  self.wave_panel=wavebox
  params=tk.Frame(wavebox,bg=PANEL,width=205);params.pack(side='right',fill='y');params.pack_propagate(False)
  self.txt(params,'LABB PERFORMANCE',10,ORANGE,True).pack(pady=(7,4))
  for text,command in [('NOTE ◀','LABB NOTE -'),('AUDITION','LABB NOTE PLAY'),('NOTE ▶','LABB NOTE +')]:self.button(params,text,lambda c=command:self.act(c),BURG if text=='AUDITION' else PANEL2).pack(fill='x',padx=10,pady=2)
  ctl=tk.Frame(center,bg=PANEL);ctl.grid(row=3,column=0,sticky='ew',pady=2)
  for t,f in [('LOAD WAV',self.load_wav),('MASCHINE SETUP',self.app.open_hardware_setup),('BANK A',lambda:self.bank(0)),('BANK B',lambda:self.bank(1)),('JOG ◀',lambda:self.act('HW JOG -')),('JOG CLICK',lambda:self.act('JOG CLICK')),('JOG ▶',lambda:self.act('HW JOG +'))]:self.button(ctl,t,f,BURG if t=='JOG CLICK' else PANEL).pack(side='left',padx=3,pady=4)
  self.pad_header_holder=center
  self.grid_section(center,4,'STEP MATRIX  /  SELECT A PAD TO EDIT ITS GROUP')
  self.matrix=tk.Canvas(center,height=104,bg=PANEL,highlightthickness=0);self.matrix.grid(row=5,column=0,sticky='nsew');self.matrix.bind('<Configure>',lambda e:self.draw_matrix());self.matrix.bind('<Button-1>',self.matrix_click)
  self.grid_section(center,6,'TRACK CITY  /  MRQ · TRK · ARR',ORANGE)
  self.track_city_stack=tk.Frame(center,bg=PANEL2);self.track_city_stack.grid(row=7,column=0,sticky='nsew');self.track_city_stack.grid_columnconfigure(0,weight=1);self.track_city_stack.grid_rowconfigure(1,weight=1)
  self.loop_bar=tk.Canvas(self.track_city_stack,height=34,bg='#251824',highlightthickness=0,cursor='hand2');self.loop_bar.grid(row=0,column=0,sticky='ew');self.loop_bar.bind('<Configure>',lambda e:self.draw_loop_bar());self.loop_bar.bind('<ButtonPress-1>',self.loop_press);self.loop_bar.bind('<B1-Motion>',self.loop_move);self.loop_bar.bind('<ButtonRelease-1>',self.loop_release);self.loop_bar.bind('<Motion>',self.loop_hover);self.loop_bar.bind('<Double-Button-1>',self.loop_tools);self.loop_bar.bind('<Button-3>',self.loop_tools)
  self.arrange=tk.Canvas(self.track_city_stack,height=190,bg=PANEL2,highlightthickness=0);self.arrange.grid(row=1,column=0,sticky='nsew');self.arrange.bind('<Configure>',lambda e:self.draw_arrange());self.arrange.bind('<ButtonPress-1>',self.arr_press);self.arrange.bind('<B1-Motion>',self.arr_move);self.arrange.bind('<ButtonRelease-1>',self.arr_release);self.arrange.bind('<ButtonPress-2>',self.mouse_pan_start);self.arrange.bind('<B2-Motion>',self.mouse_pan_move);self.arrange.bind('<ButtonRelease-2>',self.mouse_pan_end);self.arrange.bind('<MouseWheel>',self.mouse_wheel);self.arrange.bind('<Button-4>',lambda e:self.mouse_wheel_steps(e,1));self.arrange.bind('<Button-5>',lambda e:self.mouse_wheel_steps(e,-1))
  transport=tk.Frame(center,bg=PANEL);transport.grid(row=8,column=0,sticky='ew',pady=2)
  self.mode_buttons={}
  for t,c in [('▶ PLAY/STOP','PLAY/STOP'),('MRQ','MODE MRQ'),('TRK','MODE TRK'),('ARR','MODE ARR'),('SPLIT','SPLIT'),('COPY','COPY'),('MERGE','PASTE MERGE'),('UNDO','UNDO'),('REDO','REDO')]:
   button=self.button(transport,t,lambda c=c:self.act(c),ORANGE if 'PLAY' in t else PANEL);button.pack(side='left',padx=2,pady=4)
   if t in ('MRQ','TRK','ARR'):self.mode_buttons[t]=button
  self.button(transport,'RANGE ▾',lambda:self.loop_tools(),BURG).pack(side='left',padx=2,pady=4)
  self.grid_section(center,9,'DEVICE CHAIN  /  ROUTING PREVIEW',MINT)
  self.devices=tk.Canvas(center,height=75,bg=PANEL2,highlightthickness=0);self.devices.grid(row=10,column=0,sticky='nsew');self.devices.bind('<Configure>',lambda e:self.draw_devices())
  self.center_panel=center
  right=tk.Frame(mid,bg=PANEL,width=215);right.pack(side='right',fill='y',padx=(7,0));right.pack_propagate(False)
  self.right_sidebar=right
  self.txt(right,'ORB CONTROL',14,MINT,True).pack(pady=(12,5))
  self.orb_label=self.txt(right,'SOUL',16,ORANGE,True);self.orb_label.pack(pady=6)
  self.knob=tk.Scale(right,from_=0,to=100,orient='horizontal',bg=PANEL,fg=CREAM,highlightthickness=0,troughcolor=BURG,length=185,command=self.knob_changed,label='Macro value')
  self.knob.pack(pady=5)
  self.txt(right,'SOUL changes filter character.\nOther orbs save macro values.',9,DIM).pack(pady=5)
  self.txt(right,'FX RACK  /  PREVIEW',12,ORANGE,True).pack(pady=(18,7))
  for i,n in enumerate(['EQ','COMP','SAT','TAPE','LO-FI','REVERB','DELAY']):self.button(right,n,lambda n=n:self.fx_info(n),BURG if i%2 else '#38243d').pack(fill='x',padx=10,pady=2)
  self.fx_status=self.txt(right,'FX slots are not DSP yet',9,DIM);self.fx_status.pack(pady=10)
  self.txt(right,'MASTER OUTPUT',12,MINT,True).pack(pady=(17,4))
  self.master=tk.Canvas(right,height=110,bg=PANEL2,highlightthickness=0);self.master.pack(fill='x',padx=10)
  self.feature_visibility={}
  self.saved_pack_layout={}
  self.visibility_path=Path.home()/'.toolboxx'/'workspace_visibility.json'
  self._restore_visibility()
  self.info=self.txt(self.win,'SHARED ENGINE • 22 LABBS • TRACK CITY • STUDIO SIMULATOR • PHYSICAL USB NOT YET CONNECTED',9,MINT);self.info.pack(fill='x',pady=2)
 def _panel_registry(self):
  return {
   'Instrument browser':(self.instrument_sidebar,'pack'),
   'Instrument header':(self.instrument_header,'grid'),
   'Performance macros':(self.orbs,'grid'),
   'Waveform / sample view':(self.wave_panel,'grid'),
   '32-pad step matrix':(self.matrix,'grid'),
   'Track City arranger':(self.arrange,'grid'),
   'Device chain':(self.devices,'grid'),
   'Right-side FX and meters':(self.right_sidebar,'pack'),
   'Brand header / Rage banner':(self.art,'pack')}
 def _restore_visibility(self):
  for label,visible in read_visibility(self.visibility_path).items():
   self.feature_visibility[label]=tk.BooleanVar(master=self.win,value=visible)
   if not visible:
    widget,manager=self._panel_registry()[label]
    self.set_panel_visible(widget,manager,False)
 def _save_visibility(self):
  write_visibility(self.visibility_path,{k:v.get() for k,v in self.feature_visibility.items()})
 def toggle_panel(self,label):
  widget,manager=self._panel_registry()[label]
  self.set_panel_visible(widget,manager,self.feature_visibility[label].get())
  self._save_visibility()
 def open_feature_menu(self):
  """Single grouped menu. Only verified UI features have active commands.
  Planned features remain visible in the catalog but cannot be falsely enabled.
  """
  menu=tk.Menu(self.win,tearoff=False,bg=PANEL,fg=CREAM,activebackground=BURG,activeforeground=CREAM)
  for group,labels in FEATURES.items():
   sub=tk.Menu(menu,tearoff=False,bg=PANEL,fg=CREAM,activebackground=BURG,activeforeground=CREAM)
   for label in labels:
    if label in self.feature_visibility:
     sub.add_checkbutton(label=label,variable=self.feature_visibility[label],command=lambda l=label:self.toggle_panel(l))
    elif label=='Advanced instrument editor':
     sub.add_command(label='Open '+label,command=self.app.open_labbs)
    else:
     sub.add_command(label=label+'   [PLANNED]',state='disabled')
   menu.add_cascade(label=group,menu=sub)
  # Build 022: actionable instrument engine commands live in the master menu.
  # These commands reuse the existing shared engine and editor; no second state.
  instruments=tk.Menu(menu,tearoff=False,bg=PANEL,fg=CREAM,activebackground=BURG,activeforeground=CREAM)
  instruments.add_command(label='Open 22 LABBs / Advanced Instrument Editor',command=self.app.open_labbs)
  instruments.add_command(label='Advanced MIDI Note Editor',command=self.app.open_advanced_midi)
  instruments.add_separator()
  instruments.add_command(label='ALL NOTES OFF / Panic',command=self.app.labbs.all_notes_off)
  instruments.add_command(label='Patch STORE / RECALL (open editor)',command=self.app.open_labbs)
  instruments.add_command(label='ADSR / Filter / Drive / Width (open editor)',command=self.app.open_labbs)
  instruments.add_command(label='MIDI Channel / Level / Mute / Solo (open editor)',command=self.app.open_labbs)
  menu.add_cascade(label='LABB ENGINE / PATCH MEMORY',menu=instruments)
  crate=tk.Menu(menu,tearoff=False,bg=PANEL,fg=CREAM)
  crate.add_command(label='STREET TAP / Record Windows Audio',command=self.open_street_capture)
  crate.add_command(label='CRATE BLOCK / Sample Sites + Downloads',command=self.open_street_capture)
  menu.add_cascade(label='STREET TAP / CRATE BLOCK',menu=crate)
  mouse=tk.Menu(menu,tearoff=False,bg=PANEL,fg=CREAM)
  mouse.add_command(label='Logitech / Trackball: mouse profile',command=self.show_mouse_profile)
  mouse.add_command(label='Reset arranger pan + zoom',command=self.reset_arr_view)
  menu.add_cascade(label='HARDWARE / LOGITECH MOUSE',menu=mouse)
  mpc=tk.Menu(menu,tearoff=False,bg=PANEL,fg=CREAM)
  for label,command in [('MRQ / Marquee','MODE MRQ'),('TRK / Track','MODE TRK'),('ARR / Arrange','MODE ARR'),('Scissor Split','SPLIT'),('Paste Merge','PASTE MERGE'),('Undo','UNDO'),('Redo','REDO')]:
   mpc.add_command(label=label,command=lambda c=command:self.act(c))
  mpc.add_separator();mpc.add_command(label='Loop brace: drag body to move / ends to resize',state='disabled')
  menu.add_cascade(label='TRACK CITY / MPC WORKFLOW',menu=mpc)
  fender=tk.Menu(menu,tearoff=False,bg=PANEL,fg=CREAM)
  fender.add_command(label='Advanced MIDI Note Editor',command=self.app.open_advanced_midi)
  fender.add_command(label='Advanced Instrument Controls',command=self.app.open_labbs)
  fender.add_command(label='Mix Rack / Iron Chain FX',command=self.app.open_mix_rack)
  fender.add_separator()
  for label in ['STREET LINK / Controller Focus [PLANNED]','MOTION TRACKS / Automation Lanes [PLANNED]','CREW LINK / Controller Groups [PLANNED]']:
   fender.add_command(label=label,state='disabled')
  menu.add_cascade(label='ADVANCED / STUDIO WORKFLOW',menu=fender)
  menu.add_separator()
  menu.add_command(label='Show all workspace panels',command=self.show_all_panels)
  menu.add_command(label='Reset workspace visibility',command=self.show_all_panels)
  try:menu.tk_popup(self.win.winfo_pointerx(),self.win.winfo_pointery())
  finally:menu.grab_release()
 def open_street_capture(self):
  from street_capture_window import StreetCaptureWindow
  StreetCaptureWindow(self.app)
 def set_panel_visible(self,widget,manager,visible):
  if visible:
   if manager=='grid':widget.grid()
   else:
    opts=self.saved_pack_layout.get(widget)
    if opts:widget.pack(**opts)
    else:widget.pack()
  else:
   if manager=='grid':widget.grid_remove()
   else:
    if widget.winfo_manager()=='pack':self.saved_pack_layout[widget]=widget.pack_info()
    widget.pack_forget()
 def show_all_panels(self):
  for label,var in self.feature_visibility.items():
   if not var.get():var.set(True)
  mapping=[(self.instrument_sidebar,'pack'),(self.instrument_header,'grid'),(self.orbs,'grid'),(self.wave_panel,'grid'),(self.matrix,'grid'),(self.arrange,'grid'),(self.devices,'grid'),(self.right_sidebar,'pack'),(self.art,'pack')]
  for widget,manager in mapping:self.set_panel_visible(widget,manager,True)
  self._save_visibility()
 def draw_banner(self,e=None):
  from street_visuals import scuffed_metal,skyline
  c=self.art;c.delete('all');w=max(1,c.winfo_width());h=max(1,c.winfo_height())
  c.create_rectangle(0,0,w,h,fill='#211d1a',outline='#94603b',width=2)
  scuffed_metal(c,0,0,w,h,seed=14,density=90);skyline(c,max(500,w-410),0,w,h)
  c.create_text(19,24,anchor='w',text='TOOLBOXX  /  COOK UP MATRIX',fill=CREAM,font=('Arial Black',20,'bold'))
  c.create_text(21,57,anchor='w',text='NEW YORK  •  BOOM BAP  /  SAMPLE · ARRANGE · PERFORM',fill=MINT,font=('Segoe UI',9,'bold'))
  c.create_rectangle(w-205,11,w-12,35,fill='#171615',outline='#73573c')
  c.create_text(w-22,23,anchor='e',text=f'{sum(sample is not None for sample in self.app.engine.samples):02} / 32 PADS LOADED',fill=ORANGE,font=('Segoe UI',9,'bold'))
 def select_suite(self,event=None):
  s=self.labb_list.curselection()
  if s:self.app.labbs.selected=s[0];self.refresh()
 def orb_click(self,e):self.selected_orb=max(0,min(7,int(e.x*8/max(1,self.orbs.winfo_width()))));self.refresh()
 def orb_scroll(self,e):
  n=ORB_NAMES[self.selected_orb];self.macro[n]=max(0,min(1,self.macro[n]+(.025 if e.delta>0 else -.025)));self.refresh()
 def knob_changed(self,val):self.macro[ORB_NAMES[self.selected_orb]]=float(val)/100;self.draw_orbs()
 def draw_orbs(self):
  c=self.orbs;c.delete('all');w=max(1,c.winfo_width());step=w/8
  for i,n in enumerate(ORB_NAMES):
   x=(i+.5)*step;y=max(25,c.winfo_height()*.4);r=min(29,step*.34,c.winfo_height()*.29);col=[ORANGE,MINT,PURPLE,BURG,CREAM,ORANGE,MINT,PURPLE][i]
   for k in range(3,0,-1):c.create_oval(x-r-k*2,y-r-k*2,x+r+k*2,y+r+k*2,outline=col if i==self.selected_orb else '#38283b')
   c.create_oval(x-r,y-r,x+r,y+r,fill='#31233b',outline=col,width=2)
   c.create_arc(x-r+5,y-r+5,x+r-5,y+r-5,start=90,extent=-359*self.macro[n],style='arc',outline=col,width=4)
   c.create_text(x,y,text=n[:2],fill=CREAM,font=('Segoe UI',12,'bold'));c.create_text(x,c.winfo_height()-12,text=n,fill=CREAM,font=('Segoe UI',8,'bold'))
 def draw_pad_deck(self):
  c=self.pad_deck;c.delete('all');w=max(1,c.winfo_width());h=max(1,c.winfo_height());cw=w/4;rh=h/4
  for row in range(4):
   for col in range(4):
    # Hardware-style order: pads 1–4 at the bottom, 13–16 at the top.
    index=self.app.bank*16+(3-row)*4+col;selected=index==self.app.selected_pad;loaded=self.app.engine.samples[index] is not None
    x=col*cw;y=row*rh;color=MINT if selected else ORANGE if loaded else PURPLE
    c.create_rectangle(x+2,y+2,x+cw-2,y+rh-2,fill='#30251d' if loaded else '#201724',outline=color,width=2 if selected else 1)
    c.create_line(x+5,y+5,x+cw-6,y+5,fill='#65513b')
    c.create_line(x+cw-13,y+rh-5,x+cw-5,y+rh-5,fill='#4b3933')
    c.create_text(x+7,y+rh/2,anchor='w',text=f'{index+1:02}',fill=CREAM,font=('Segoe UI',9,'bold'))
    c.create_oval(x+cw-12,y+rh/2-2,x+cw-8,y+rh/2+2,fill=ORANGE if loaded else '#514258',outline='')
 def pad_at(self,e):
  w=max(1,self.pad_deck.winfo_width());h=max(1,self.pad_deck.winfo_height())
  if not 0<=e.x<w or not 0<=e.y<h:return None
  return self.app.bank*16+(3-int(e.y*4/h))*4+int(e.x*4/w)
 def pad_click(self,e):
  index=self.pad_at(e)
  if index is None:return
  self.app.selected_pad=index;self.app.engine.trigger(index);self.app._refresh();self.refresh()
 def pad_load(self,e):
  index=self.pad_at(e)
  if index is None:return
  self.app.selected_pad=index;self.load_wav()
 def draw_wave(self):
  c=self.wave;c.delete('all');w=max(1,c.winfo_width());h=max(1,c.winfo_height());sample=self.app.engine.samples[self.app.selected_pad]
  c.create_text(12,9,anchor='nw',text=f'PAD {self.app.selected_pad+1:02}  /  '+(sample[2] if sample else 'NO SAMPLE'),fill=CREAM,font=('Segoe UI',9,'bold'))
  middle=h*.58;c.create_line(10,middle,w-10,middle,fill='#584035')
  if not sample:
   c.create_text(w/2,middle,text='LOAD WAV  •  Double-click a pad to assign audio',fill=DIM,font=('Segoe UI',9));return
  data,rate,name=sample;columns=max(1,int(w)-24);amplitude=max(1,(h-42)/2)
  for column in range(columns):
   start=int(column*len(data)/columns);end=max(start+1,int((column+1)*len(data)/columns));chunk=data[start:end]
   if not chunk:continue
   lo=min(chunk);hi=max(chunk);x=12+column
   c.create_line(x,middle-hi*amplitude,x,middle-lo*amplitude,fill=ORANGE)
  c.create_text(w-10,h-7,anchor='se',text=f'{len(data)/rate:.2f}s  •  {rate/1000:g} kHz',fill=MINT,font=('Segoe UI',8))
 def draw_matrix(self):
  c=self.matrix;c.delete('all');w=max(1,c.winfo_width());left=42;cw=max(6,(w-left-8)/16);pat=self.app.active_pattern()
  rh=max(18,(c.winfo_height()-6)/4)
  for r in range(4):
   pad=(self.app.selected_pad//4)*4+r;c.create_text(19,5+r*rh+rh/2,text=f'{pad+1:02}',fill=CREAM,font=('Segoe UI',9,'bold'))
   for j in range(16):
    x=left+j*cw;y=5+r*rh;on=pat[pad][j];col=[MINT,PURPLE,ORANGE,BURG][r] if on else '#33243b';c.create_rectangle(x+2,y,x+cw-2,y+rh-5,fill=col,outline='#65465e' if j%4==0 else '#35283d');
    if j%4==0:c.create_text(x+5,y+3,anchor='nw',text=str(j+1),fill=BG if on else DIM,font=('Segoe UI',7))
 def matrix_click(self,e):
  w=max(1,self.matrix.winfo_width());cw=(w-50)/16;r=int((e.y-5)//max(18,(self.matrix.winfo_height()-6)/4));j=int((e.x-42)//cw)
  if 0<=r<4 and 0<=j<16:self.app.selected_pad=(self.app.selected_pad//4)*4+r;self.app.toggle_step(j);self.refresh()
 def _loop_scale(self):
  return max(1,(max(1,self.loop_bar.winfo_width())-102)/48)*self.arr_zoom
 def draw_loop_bar(self):
  if not hasattr(self,'loop_bar'):return
  c=self.loop_bar;c.delete('all');w=max(1,c.winfo_width());scale=self._loop_scale();left=90;arr=self.app.arr
  c.create_text(9,17,text=arr.mode,anchor='w',fill=MINT,font=('Segoe UI',9,'bold'))
  start=left+(arr.loop_start-self.arr_view_start)*scale;end=left+(arr.loop_end-self.arr_view_start)*scale
  x0,x1=max(left,start),min(w-2,end)
  if x1>x0:
   c.create_rectangle(x0,5,x1,29,fill=BURG if arr.loop_enabled else '#322b36',outline=MINT,width=2)
   for x in [start,end]:
    if left<=x<=w:c.create_line(x,4,x,30,fill=ORANGE,width=5)
   if x1-x0>105:c.create_text((x0+x1)/2,17,text=f'{arr.loop_start/4+1:g} → {arr.loop_end/4+1:g}  •  '+('LOOP' if arr.loop_enabled else 'LOOP OFF'),fill=CREAM,font=('Segoe UI',8,'bold'))
  for mode,button in self.mode_buttons.items():button.config(bg=ORANGE if mode==arr.mode else PANEL,fg=BG if mode==arr.mode else CREAM)
 def _loop_hit(self,x):
  scale=self._loop_scale();start=90+(self.app.arr.loop_start-self.arr_view_start)*scale;end=90+(self.app.arr.loop_end-self.arr_view_start)*scale
  if x<90:return None
  if abs(x-start)<10:return 'start'
  if abs(x-end)<10:return 'end'
  if start<x<end:return 'body'
  return None
 def loop_hover(self,e):
  edge=self._loop_hit(e.x);self.loop_bar.config(cursor='sb_h_double_arrow' if edge in ('start','end') else 'fleur' if edge else 'arrow')
 def loop_tools(self,e=None):
  if e is None:
   from types import SimpleNamespace
   e=SimpleNamespace(x_root=self.loop_bar.winfo_rootx()+100,y_root=self.loop_bar.winfo_rooty()+34)
  self.loop_drag=None
  menu=tk.Menu(self.win,tearoff=False,bg=PANEL,fg=CREAM,activebackground=ORANGE)
  for label,cmd in [('Copy range','RANGE COPY'),('Cut range','RANGE CUT'),('Paste at playhead','RANGE PASTE'),('Duplicate after range','RANGE DUPLICATE'),('Duplicate + insert time','RANGE INSERT'),('Clear range','RANGE DELETE'),('Loop on / off','LOOP TOGGLE'),('Loop whole song','LOOP ALL'),('Focus loop for jog control','LOOP FOCUS')]:menu.add_command(label=label,command=lambda c=cmd:self.act(c))
  try:menu.tk_popup(e.x_root,e.y_root)
  finally:menu.grab_release()
 def loop_press(self,e):
  edge=self._loop_hit(e.x)
  if edge:self.loop_drag={'x':e.x,'start':self.app.arr.loop_start,'end':self.app.arr.loop_end,'edge':edge,'checkpoint':False}
 def loop_move(self,e):
  if self.loop_drag is None:return
  d=self.loop_drag;delta=self.app.arr.quant((e.x-d['x'])/self._loop_scale());start,end=d['start'],d['end']
  if d['edge']=='start':start=max(0,min(end-.25,start+delta))
  elif d['edge']=='end':end=max(start+.25,end+delta)
  else:delta=max(-start,delta);start+=delta;end+=delta
  if (start,end)==(self.app.arr.loop_start,self.app.arr.loop_end):return
  if not d['checkpoint']:self.app.arr.checkpoint();d['checkpoint']=True
  self.app.arr.loop_start=start;self.app.arr.loop_end=end;self.app.range_editor.select();self.draw_arrange()
 def loop_release(self,e):
  self.loop_drag=None;self.app._refresh()
 def _arr_position(self,e):
  scale=max(1,(max(1,self.arrange.winfo_width())-102)/48)*self.arr_zoom;rowh=max(14,(self.arrange.winfo_height()-48)/6)
  return max(0.,self.arr_view_start+(e.x-90)/scale),max(0,min(5,int((e.y-44)//rowh)))
 def arr_press(self,e):
  beat,track=self._arr_position(e)
  if e.y<44:self.arr_click(e);return
  self.app.arr.focus_track=track
  if e.x<90:
   self.app.range_editor.track_range=(track,track);self.app.range_editor.select();self.refresh();return
  self.range_drag={'beat':beat,'track':track,'x':e.x,'y':e.y}
  self.arr_click(e)
 def arr_move(self,e):
  if not self.range_drag:return
  d=self.range_drag
  if abs(e.x-d['x'])+abs(e.y-d['y'])<4:return
  beat,track=self._arr_position(e)
  end_track=track if self.app.arr.mode=='MRQ' else d['track']
  self.app.range_editor.set_range(d['beat'],beat,d['track'],end_track);self.draw_arrange()
 def arr_release(self,e):
  self.range_drag=None;self.app._refresh();self.refresh()
 def draw_arrange(self):
  c=self.arrange;c.delete('all');w=max(1,c.winfo_width());h=max(1,c.winfo_height());left=90;scale=max(1,(w-left-12)/48)*self.arr_zoom
  self.draw_loop_bar()
  first=int(self.arr_view_start//4)*4;last=int(self.arr_view_start+48/self.arr_zoom)+8
  for beat in range(first,last,4):
   x=left+(beat-self.arr_view_start)*scale;c.create_line(x,24,x,h,fill='#392a3d');c.create_text(x+2,26,text=str(beat//4+1),anchor='nw',fill=DIM,font=('Segoe UI',8))
  rowh=max(14,(h-48)/6)
  for t in range(6):
   y=44+t*rowh;c.create_text(6,y+8,text=['DRUMS','BASS','KEYS','CHOP','VOX','FX'][t],fill=CREAM,anchor='w',font=('Segoe UI',8,'bold'));c.create_line(left,y+rowh-3,w,y+rowh-3,fill='#38293c')
  tracks=self.app.range_editor.scope_tracks();lo=self.app.arr.loop_start;hi=self.app.arr.loop_end
  for track in range(6):
   if tracks is None or track in tracks:
    x0=max(left,left+(lo-self.arr_view_start)*scale);x1=min(w,left+(hi-self.arr_view_start)*scale)
    if x1>x0:c.create_rectangle(x0,44+track*rowh,x1,44+(track+1)*rowh-3,fill='#392735',outline='')
  for clip in self.app.arr.clips:
   t=clip['track'];
   if t>5:continue
   x=left+(clip['start']-self.arr_view_start)*scale;x2=x+clip['length']*scale;y=44+t*rowh;selected=clip['id'] in self.app.arr.selected
   if x2<left or x>w:continue
   x=max(left,x);x2=min(w,x2)
   c.create_rectangle(x,y,x2,y+rowh-6,fill=COLORS[t],outline=CREAM if selected else BG,width=2 if selected else 1,tags=('clip',clip['id']))
   c.create_text(x+4,y+(rowh-6)/2,text=clip['name'][:18],anchor='w',fill=BG,font=('Segoe UI',8,'bold'),tags=('clip',clip['id']))
  x=left+(self.app.playhead-self.arr_view_start)*scale;c.create_line(x,23,x,h,fill=CREAM,width=2)
 def arr_click(self,e):
  w=max(1,self.arrange.winfo_width());left=90;scale=max(1,(w-left-12)/48)*self.arr_zoom
  if e.y<44:self.app.playhead=max(0,self.arr_view_start+(e.x-left)/scale);self.refresh();return
  for item in reversed(self.arrange.find_overlapping(e.x,e.y,e.x,e.y)):
   tags=self.arrange.gettags(item)
   if 'clip' in tags:self.app.arr.select([tags[-1]]);self.app._refresh();self.refresh();return
  self.app.arr.select([]);self.refresh()
 def mouse_pan_start(self,e):
  # Middle button never seeks, selects, or mutates clips.
  self.mouse_pan_anchor=(e.x,self.arr_view_start)
 def mouse_pan_move(self,e):
  if self.mouse_pan_anchor is None:return
  width=max(1,self.arrange.winfo_width());scale=max(1,(width-102)/48)*self.arr_zoom
  x,start=self.mouse_pan_anchor;self.arr_view_start=max(0.0,start+(x-e.x)/scale);self.draw_arrange()
 def mouse_pan_end(self,e):self.mouse_pan_anchor=None
 def mouse_wheel(self,e):
  steps=(1 if e.delta>0 else -1) if e.delta else 0
  self.mouse_wheel_steps(e,steps)
 def mouse_wheel_steps(self,e,steps):
  if not steps:return
  width=max(1,self.arrange.winfo_width());scale=max(1,(width-102)/48)*self.arr_zoom
  if e.state & 0x0008: # Alt + wheel: zoom around pointer, not playhead.
   beat=self.arr_view_start+max(0,e.x-90)/scale
   self.arr_zoom=max(.25,min(16.0,self.arr_zoom*(1.15 if steps>0 else 1/1.15)))
   new_scale=max(1,(width-102)/48)*self.arr_zoom
   self.arr_view_start=max(0,beat-max(0,e.x-90)/new_scale)
  else:self.arr_view_start=max(0,self.arr_view_start-steps*4/self.arr_zoom)
  self.draw_arrange()
 def reset_arr_view(self):
  self.arr_view_start=0.0;self.arr_zoom=1.0;self.draw_arrange()
 def show_mouse_profile(self):
  from tkinter import messagebox
  messagebox.showinfo('TOOLBOXX / LOGITECH MOUSE',
   'Universal Logitech / trackball profile\n\nLeft click: select clip / ruler seek\nMiddle drag: pan ONLY\nWheel: horizontal timeline scroll\nAlt + wheel: pointer-centered zoom\nCtrl + Z: undo\n\nMouse side buttons and model-specific remapping require device identification and driver/OS integration. No Logitech driver is included.',parent=self.win)
 def draw_devices(self):
  c=self.devices;c.delete('all');w=max(1,c.winfo_width());h=max(75,c.winfo_height());names=['16-BAND EQ','RED HOOK TAPE','DUSTY TUBE','BROOKLYN IRON','CHORUS','REVERB','COMP'];cw=w/len(names)
  for i,n in enumerate(names):
   x=i*cw;c.create_rectangle(x+3,4,x+cw-3,h-5,fill='#2a1c2d',outline=[MINT,ORANGE,PURPLE][i%3],width=1)
   c.create_text(x+cw/2,15,text=n,fill=CREAM,font=('Segoe UI',8,'bold'))
   for j in range(3):c.create_oval(x+cw*(.23+j*.25)-5,36,x+cw*(.23+j*.25)+5,46,outline=[MINT,ORANGE,PURPLE][(i+j)%3],width=2)
   c.create_text(x+cw/2,h-18,text='DSP PLANNED',fill=DIM,font=('Segoe UI',7))
 def draw_master(self):
  c=self.master;c.delete('all');w=max(1,c.winfo_width());peak=min(1,max(0,self.app.labbs.master.peak))
  c.create_text(8,12,anchor='w',text='SHARED MASTER BUS',fill=CREAM,font=('Segoe UI',9,'bold'))
  for i in range(18):
   x=8+i*(w-16)/18;active=(i/18)<peak;c.create_rectangle(x,36,x+(w-22)/23,75,fill=(MINT if i<12 else ORANGE) if active else '#34283a',outline='')
  c.create_text(8,92,anchor='w',text=f'PEAK {peak:.2f}  /  SOFT CLIP + CEILING',fill=DIM,font=('Segoe UI',8))
 def load_wav(self):self.app.load_sample();self.refresh()
 def bank(self,i):self.app.set_bank(i);self.app.selected_pad=self.app.bank*16+self.app.selected_pad%16;self.refresh()
 def act(self,command):self.app.command(command);self.refresh()
 def fx_info(self,n):self.fx_status.config(text=n+' • visual slot only')
 def refresh(self):
  self.current_suite=self.app.labbs.selected;self.labb_list.selection_clear(0,'end');self.labb_list.selection_set(self.current_suite);self.labb_list.see(self.current_suite)
  l=LABBS[self.current_suite];self.labb_title.config(text=l.name.upper()+'  /  '+l.wave.upper());self.labb_status.config(text='ENGINE  '+l.wave.upper()+'  •  SHARED BUS')
  self.orb_label.config(text=ORB_NAMES[self.selected_orb]);self.knob.set(round(self.macro[ORB_NAMES[self.selected_orb]]*100))
  self.tempo_label.config(text=f'{self.app.bpm:g} BPM  •  4/4')
  self.draw_banner();self.draw_orbs();self.draw_pad_deck();self.draw_wave();self.draw_matrix();self.draw_arrange();self.draw_devices();self.draw_master()
 def poll(self):
  if not self.win.winfo_exists():return
  controller=getattr(self.app,'midi_connected_name',None)
  self.info.config(text='MASCHINE STUDIO  /  '+('MIDI CONNECTED: '+controller if controller else 'MIDI NOT CONNECTED')+'  •  SHARED AUDIO ENGINE  •  22 LABBS')
  sample=self.app.engine.samples[self.app.selected_pad];state=(self.app.selected_pad,self.app.bank,id(sample),sum(s is not None for s in self.app.engine.samples))
  if state!=getattr(self,'_pad_view_state',None):
   self._pad_view_state=state;self.draw_pad_deck();self.draw_wave();self.draw_banner()
  if self.current_suite!=self.app.labbs.selected:self.refresh()
  self.tempo_label.config(text=f'{self.app.bpm:g} BPM  •  '+('PLAYING' if self.app.playing else 'STOPPED'))
  self.draw_arrange();self.draw_matrix();self.draw_master();self.win.after(250,self.poll)
