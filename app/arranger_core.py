"""TOOLBOXX Track City editing model: beat-based, hardware/UI agnostic."""
import copy
import uuid

class Arranger:
    def __init__(self):
        self.clips=[{'id':self._id(),'track':0,'start':0.,'length':4.,'offset':0.,'name':'DRUM A','kind':'pattern','pattern_id':'main'}, {'id':self._id(),'track':1,'start':4.,'length':4.,'offset':0.,'name':'CHOP B','kind':'pattern','pattern_id':'main'}, {'id':self._id(),'track':2,'start':0.,'length':8.,'offset':0.,'name':'BASS A','kind':'pattern','pattern_id':'main'}]
        self.mode='ARR';self.selected=set();self.focus_track=0;self.loop_start=0.;self.loop_end=16.;self.loop_enabled=True
        self.snap=0.25;self.history=[];self.future=[];self.clipboard=[];self.muted_tracks=set();self.solo_tracks=set()
    @staticmethod
    def _id():return uuid.uuid4().hex[:10]
    def snapshot(self):return copy.deepcopy((self.clips,self.selected,self.focus_track,self.loop_start,self.loop_end,self.loop_enabled))
    def restore(self,s):self.clips,self.selected,self.focus_track,self.loop_start,self.loop_end,self.loop_enabled=copy.deepcopy(s)
    def checkpoint(self):self.history.append(self.snapshot());self.history=self.history[-100:];self.future.clear()
    def undo(self):
        if not self.history:return False
        self.future.append(self.snapshot());self.restore(self.history.pop());return True
    def redo(self):
        if not self.future:return False
        self.history.append(self.snapshot());self.restore(self.future.pop());return True
    def quant(self,v):return round(v/self.snap)*self.snap if self.snap else v
    def set_mode(self,m):
        if m not in ('MRQ','TRK','ARR'):raise ValueError(m)
        self.mode=m
    def select(self,ids,add=False):
        ids=set(ids)
        if not add:self.selected=ids
        else:self.selected^=ids
        if self.selected:
            c=next((c for c in self.clips if c['id'] in self.selected),None)
            if c:self.focus_track=c['track']
    def marquee(self,t0,t1,track0,track1,add=False):
        lo,hi=sorted((t0,t1));a,b=sorted((track0,track1))
        ids={c['id'] for c in self.clips if a<=c['track']<=b and c['start']<hi and c['start']+c['length']>lo}
        self.select(ids,add);return ids
    def create(self,track,start,length=4.,name='NEW CLIP',kind='pattern'):
        self.checkpoint();c={'id':self._id(),'track':max(0,int(track)),'start':max(0.,self.quant(start)),'length':max(.25,self.quant(length)),'offset':0.,'name':name,'kind':kind,'pattern_id':'main'};self.clips.append(c);self.select([c['id']]);return c
    def move(self,delta,track_delta=0):
        targets=[c for c in self.clips if c['id'] in self.selected]
        if not targets:return
        self.checkpoint();delta=self.quant(delta)
        delta=max(delta,-min(c['start'] for c in targets))
        track_delta=max(track_delta,-min(c['track'] for c in targets))
        for c in targets:c['start']+=delta;c['track']+=track_delta
    def resize(self,clip_id,edge,delta):
        c=next((c for c in self.clips if c['id']==clip_id),None)
        if not c:return
        d=self.quant(delta)
        if edge=='left':d=max(-c['start'],min(d,c['length']-.25))
        elif edge=='right':d=max(.25-c['length'],d)
        else:raise ValueError(edge)
        if not d:return
        self.checkpoint()
        if edge=='left':c['start']+=d;c['length']-=d;c['offset']+=d
        else:c['length']+=d
    def slip(self,clip_id,delta):
        c=next((c for c in self.clips if c['id']==clip_id),None)
        if c:self.checkpoint();c['offset']+=self.quant(delta)
    def split(self,at):
        targets=[c for c in self.clips if c['id'] in self.selected and c['start']<at<c['start']+c['length']]
        if not targets:return []
        self.checkpoint();new=[]
        for c in targets:
            n=copy.deepcopy(c);n['id']=self._id();n['start']=at;n['length']=c['start']+c['length']-at;n['offset']=c['offset']+(at-c['start']);c['length']=at-c['start'];self.clips.append(n);new.append(n['id'])
        self.select(new);return new
    def delete(self):
        if not self.selected:return
        self.checkpoint();self.clips=[c for c in self.clips if c['id'] not in self.selected];self.selected.clear()
    def copy(self):self.clipboard=copy.deepcopy([c for c in self.clips if c['id'] in self.selected])
    def paste(self,at,merge=False):
        if not self.clipboard:return []
        self.checkpoint();base=min(c['start'] for c in self.clipboard);new=[]
        for old in self.clipboard:
            c=copy.deepcopy(old);c['id']=self._id();c['start']=max(0.,self.quant(at+old['start']-base))
            if merge:
                overlap=next((x for x in self.clips if x['track']==c['track'] and x['start']==c['start'] and x['kind']==c['kind']),None)
                if overlap:
                    # Non-destructive container union, not a MIDI-note merge.
                    overlap['length']=max(overlap['length'],c['length']);continue
            self.clips.append(c);new.append(c['id'])
        self.select(new);return new
    def duplicate(self):
        self.copy()
        if self.clipboard:return self.paste(max(c['start']+c['length'] for c in self.clipboard))
        return []
    def loop_edit(self,edge,delta):
        d=self.quant(delta)
        if not d:return
        self.checkpoint()
        if edge=='start':self.loop_start=max(0.,min(self.loop_start+d,self.loop_end-.25))
        elif edge=='end':self.loop_end=max(self.loop_start+.25,self.loop_end+d)
        elif edge=='body':
            d=max(-self.loop_start,d);self.loop_start+=d;self.loop_end+=d
        else:raise ValueError(edge)
    def track_audible(self,track):
        return track not in self.muted_tracks and (not self.solo_tracks or track in self.solo_tracks)
    def toggle_track_mute(self,track):
        track=int(track);self.muted_tracks.symmetric_difference_update({track});return track in self.muted_tracks
    def toggle_track_solo(self,track):
        track=int(track);self.solo_tracks.symmetric_difference_update({track});return track in self.solo_tracks
    def serialize(self):return {'muted_tracks':sorted(self.muted_tracks),'solo_tracks':sorted(self.solo_tracks),'clips':self.clips,'loop_start':self.loop_start,'loop_end':self.loop_end,'loop_enabled':self.loop_enabled,'mode':self.mode,'snap':self.snap}
    def deserialize(self,d):
        self.clips=copy.deepcopy(d.get('clips',[]));self.muted_tracks=set(map(int,d.get('muted_tracks',[])));self.solo_tracks=set(map(int,d.get('solo_tracks',[])))
        for c in self.clips:c.setdefault('id',self._id());c.setdefault('offset',0.);c.setdefault('kind','pattern');c.setdefault('pattern_id','main')
        self.loop_start=float(d.get('loop_start',0));self.loop_end=max(self.loop_start+.25,float(d.get('loop_end',16)));self.loop_enabled=bool(d.get('loop_enabled',True));self.mode=d.get('mode','ARR');self.snap=float(d.get('snap',.25));self.selected=set();self.history.clear();self.future.clear()
