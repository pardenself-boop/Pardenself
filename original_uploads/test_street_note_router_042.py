import sys, unittest
from pathlib import Path
from types import SimpleNamespace as M
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from street_note_router import StreetNoteRouter
class NoteRouterTests(unittest.TestCase):
 def setUp(self):
  self.events=[]
  self.r=StreetNoteRouter(lambda n,v,i:self.events.append(('on',n,i)),lambda n,i:self.events.append(('off',n,i)),lambda:self.events.append(('panic',)))
 def test_note_on_off(self):
  self.r.message(M(type='note_on',channel=0,note=60,velocity=100),7)
  self.r.message(M(type='note_off',channel=0,note=60),3)
  self.assertEqual(self.events,[('on',60,7),('off',60,7)])
 def test_sustain(self):
  self.r.message(M(type='note_on',channel=1,note=42,velocity=90),3)
  self.r.message(M(type='control_change',channel=1,control=64,value=127))
  self.r.message(M(type='note_off',channel=1,note=42))
  self.assertEqual(len(self.events),1)
  self.r.message(M(type='control_change',channel=1,control=64,value=0))
  self.assertEqual(self.events[-1],('off',42,3))
 def test_channel_filter(self):
  self.assertFalse(self.r.message(M(type='note_on',channel=2,note=60,velocity=127),3,0))
  self.assertFalse(self.events)
 def test_panic(self):
  self.r.message(M(type='note_on',channel=0,note=60,velocity=127))
  self.r.message(M(type='control_change',channel=0,control=123,value=0))
  self.assertEqual(self.events[-1],('panic',))
  self.assertFalse(self.r.held)
 def test_velocity_zero(self):
  self.r.message(M(type='note_on',channel=0,note=64,velocity=127))
  self.r.message(M(type='note_on',channel=0,note=64,velocity=0))
  self.assertEqual(self.events[-1],('off',64,3))
if __name__=='__main__':unittest.main()
