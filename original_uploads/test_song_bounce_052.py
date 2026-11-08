import sys, unittest, tempfile, wave
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app'))
from street_song_bounce import ScheduledEngine, validate_song, bounce_song

class FakeEngine:
    sr=1000
    def __init__(self): self.triggered=[];self.loaded=[]
    def trigger(self, pad): self.triggered.append(pad)
    def render(self,n): return [.1]*n
    def load(self,pad,path): self.loaded.append((pad,path))

class SongTests(unittest.TestCase):
    def test_events_across_block_boundaries(self):
        e=FakeEngine(); s=ScheduledEngine(e,[{'pad':1,'beat':0},{'pad':2,'beat':.5}],60)
        self.assertEqual(len(s.render(300)),300)
        self.assertEqual(e.triggered,[0]);s.render(201)
        self.assertEqual(e.triggered,[0,1])
    def test_reject_out_of_range_hit(self):
        with self.assertRaises(ValueError):validate_song({'bars':1,'hits':[{'pad':33,'beat':0}]})
    def test_reject_nan(self):
        with self.assertRaises(ValueError):validate_song({'bpm':float('nan')})
    def test_song_wav(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'test.wav').write_bytes(b'dummy')
            e=FakeEngine(); result=bounce_song({'bpm':120,'bars':1,'samples':{'1':'test.wav'},'hits':[{'pad':1,'beat':0},{'pad':1,'beat':2}]},p/'song.wav',p,e)
            with wave.open(result['file'],'rb') as w:self.assertEqual(w.getnframes(),2000)
            self.assertEqual(e.triggered,[0,0])
    def test_missing_sample_no_partial_bounce(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'song.wav'
            with self.assertRaises(FileNotFoundError):bounce_song({'samples':{'1':'missing.wav'}},p,engine=FakeEngine())
            self.assertFalse(p.exists())
