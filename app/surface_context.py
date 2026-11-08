"""Contextual soft keys/encoders shared by the workstation and controller map."""
from labb_engine import LABBS
from street_sounds import SOUNDS,apply_sound
from street_fx import NAMES

SOUND_PARAMS=(('LEVEL',None,0.,1.),('ATTACK','attack',.001,2.),('DECAY','decay',.005,3.),('SUSTAIN','sustain',0.,1.),
              ('RELEASE','release',.005,4.),('CUTOFF','cutoff',.015,.98),('DRIVE','drive',0.,1.),('MASTER DRIVE','master',.05,3.))

class SurfaceContext:
    PAGES=('ARRANGE','LOOP','SOUND','FX','BROWSE')
    def __init__(self,app):self.app=app;self.page='ARRANGE';self.fx_index=0;self.sound_index=0
    def set_page(self,page):
        if page not in self.PAGES:raise ValueError('Unknown surface page')
        self.page=page
    def keys(self):
        if self.page=='LOOP':return [('ARR','SURFACE ARRANGE'),('MRQ','MODE MRQ'),('TRK','MODE TRK'),('ALL','LOOP ALL'),('LOOP','LOOP TOGGLE'),('UNDO','UNDO'),('REDO','REDO'),('SOUND','SURFACE SOUND')]
        if self.page=='ARRANGE':return [('MRQ','MODE MRQ'),('TRK','MODE TRK'),('ARR','MODE ARR'),('LOOP','LOOP TOGGLE'),('COPY','RANGE COPY'),('CUT','RANGE CUT'),('DUP','RANGE DUPLICATE'),('INSERT','RANGE INSERT')]
        if self.page=='SOUND':return [('PREV','LABB PREV'),('NEXT','LABB NEXT'),('PLAY','LABB PLAY'),('ARM','LABB ARM'),('BROWSE','BROWSE SOUNDS'),('EDIT','EDIT SOUND'),('FX','EDIT FX'),('ARR','SURFACE ARRANGE')]
        if self.page=='FX':return [('EQ','FX ADD eq'),('COMP','FX ADD compressor'),('DRIVE','FX ADD density'),('CEILING','FX ADD clipper'),('PREV','FX PREV'),('NEXT','FX NEXT'),('BYPASS','FX BYPASS'),('EDIT','EDIT FX')]
        return [('PREV','SOUND PREV'),('NEXT','SOUND NEXT'),('PLAY','LABB PLAY'),('EDIT','EDIT SOUND'),('FX','EDIT FX'),('ARR','SURFACE ARRANGE'),('SOUND','SURFACE SOUND'),('BROWSE','BROWSE SOUNDS')]
    def key(self,index):
        if not 0<=index<8:raise ValueError('Soft key must be 1–8')
        self.app.command(self.keys()[index][1])
    def values(self):
        app=self.app;i=app.labbs.selected
        if self.page=='LOOP':return [('POSITION',app.arr.loop_start),('—',0.),('START',app.arr.loop_start),('LENGTH',app.arr.loop_end-app.arr.loop_start)]+[('—',0.)]*4
        if self.page in ('SOUND','BROWSE'):
            return [(label,app.labbs.volume[i] if key is None else app.labbs.master.drive if key=='master' else app.labbs.parameters[i][key]) for label,key,_,_ in SOUND_PARAMS]
        if self.page=='FX':
            if not app.mix_rack.modules:return [('EMPTY',0.)]*8
            self.fx_index%=len(app.mix_rack.modules);module=app.mix_rack.modules[self.fx_index]
            values=[(name.replace('_',' ').upper(),value) for name,value in module.params.items()]
            return (values+[('—',0.)]*8)[:8]
        editor=app.hardware_edit
        return [('POSITION',app.arr.loop_start),('START',app.arr.loop_start),('LENGTH',app.arr.loop_end-app.arr.loop_start),('PLAYHEAD',app.playhead),('TRACK',app.arr.focus_track+1),('MOVE',editor.pending if editor.operation=='MOVE' else 0.),('TRIM L',editor.pending if editor.operation=='TRIM LEFT' else 0.),('TRIM R',editor.pending if editor.operation=='TRIM RIGHT' else 0.)]
    def knob(self,index,direction):
        if not 0<=index<8 or direction not in (-1,1):raise ValueError('Invalid surface encoder')
        app=self.app
        if self.page=='LOOP':
            if index not in (0,2,3):return
            app.arr.loop_edit({0:'body',2:'start',3:'end'}[index],direction*.25)
        elif self.page in ('SOUND','BROWSE'):
            _,key,lo,hi=SOUND_PARAMS[index];current=self.values()[index][1];value=max(lo,min(hi,current+direction*(hi-lo)/100))
            if key is None:app.labbs.volume[app.labbs.selected]=value
            elif key=='master':app.labbs.master.drive=value
            else:app.labbs.set_parameter(app.labbs.selected,key,value)
        elif self.page=='FX':
            if not app.mix_rack.modules:return
            from mix_rack import MODULES
            self.fx_index%=len(app.mix_rack.modules);module=app.mix_rack.modules[self.fx_index];names=list(module.params)
            if index>=len(names):return
            key=names[index];lo,hi,_=MODULES[module.kind][key]
            app.mix_rack.set_parameter(self.fx_index,key,max(lo,min(hi,module.params[key]+direction*(hi-lo)/100)))
            if hasattr(app,'sync_fx_window'):app.sync_fx_window()
        elif index<3:
            app.arr.loop_edit(('body','start','end')[index],direction*.25)
        elif index==3:app.playhead=max(0,app.playhead+direction*.25)
        elif index==4:app.arr.focus_track=max(0,app.arr.focus_track+direction);app.range_editor.select()
        else:
            operation=('MOVE','TRIM LEFT','TRIM RIGHT')[index-5]
            if app.hardware_edit.operation!=operation:app.hardware_edit.set_operation(operation)
            app.hardware_edit.rotate(direction)
        app._refresh()
    def choose_sound(self,delta):
        self.sound_index=(self.sound_index+delta)%len(SOUNDS)
        name=apply_sound(self.app.labbs,self.sound_index);self.app.notes.armed_labb=self.app.labbs.selected
        self.app.status.config(text='STREET BANK: '+name);self.app._refresh()
