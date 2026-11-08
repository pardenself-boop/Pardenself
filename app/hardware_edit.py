"""Hardware-first, transactional jog-click editor shared by Studio and Windows UI.
No physical USB driver is claimed. Every mutation uses Arranger methods.
"""
from dataclasses import dataclass

OPERATIONS = ('SELECT','MOVE','TRACK MOVE','TRIM LEFT','TRIM RIGHT','SLIP',
              'MARQUEE','LOOP START','LOOP END','LOOP MOVE')

@dataclass
class HardwareEdit:
    app: object
    focus: int = 0
    operation: str = 'SELECT'
    pending: float = 0.0
    anchor: float | None = None
    shift: bool = False
    marquee_track: int = 0

    def clips(self):
        return sorted(self.app.arr.clips,key=lambda c:(c['track'],c['start'],c['id']))

    def current(self):
        cs=self.clips()
        if not cs:return None
        self.focus%=len(cs)
        return cs[self.focus]

    def rotate(self,steps):
        if not steps:return self.describe()
        if self.operation=='SELECT':
            if self.clips():self.focus=(self.focus+steps)%len(self.clips())
        elif self.operation=='TRACK MOVE':
            self.pending+=int(steps)
        else:
            self.pending+=steps*(.0625 if self.shift else .25)
        return self.describe()

    def click(self):
        a=self.app.arr;c=self.current()
        if self.operation=='SELECT':
            if c:a.select([c['id']],add=self.shift)
            return self.describe()
        if self.operation=='MARQUEE':
            if self.anchor is None:
                self.anchor=self.app.playhead+self.pending
                self.marquee_track=a.focus_track
                self.pending=0
            else:
                a.marquee(self.anchor,self.app.playhead+self.pending,
                          self.marquee_track,a.focus_track,add=self.shift)
                self.cancel()
            return self.describe()
        if c and self.pending:
            # All edits checkpoint exactly once, at confirmation, not per jog tick.
            if self.operation=='MOVE':
                if c['id'] not in a.selected:a.select([c['id']])
                a.move(self.pending)
            elif self.operation=='TRACK MOVE':
                if c['id'] not in a.selected:a.select([c['id']])
                a.move(0,int(self.pending))
            elif self.operation=='TRIM LEFT':a.resize(c['id'],'left',self.pending)
            elif self.operation=='TRIM RIGHT':a.resize(c['id'],'right',self.pending)
            elif self.operation=='SLIP':a.slip(c['id'],self.pending)
        if self.pending and self.operation.startswith('LOOP'):
            edge={'LOOP START':'start','LOOP END':'end','LOOP MOVE':'body'}[self.operation]
            a.loop_edit(edge,self.pending)
        self.cancel()
        return self.describe()

    def set_operation(self,op):
        if op not in OPERATIONS:raise ValueError(op)
        self.operation=op;self.pending=0;self.anchor=None
        return self.describe()

    def cancel(self):
        self.pending=0;self.anchor=None;self.operation='SELECT'
        return self.describe()

    def describe(self):
        c=self.current();name=c['name'] if c else 'NO CLIP'
        return f'{self.operation} | {name} | delta {self.pending:+.4f}' + (' | SHIFT fine' if self.shift else '')
