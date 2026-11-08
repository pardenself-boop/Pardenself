import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from arranger_core import Arranger
from track_city_bounce import collect_hits,bounce_track_city

class TrackCityBounceTests(unittest.TestCase):
 def setUp(self):
  self.arr=Arranger();self.arr.clips=[dict(track=0,start=0.,length=4.,offset=0.,kind='pattern',pattern_id='main')]
  self.pattern=[[False]*16 for _ in range(32)];self.pattern[0][0]=True;self.pattern[1][4]=True
 def test_looped_clip(self):
  self.arr.clips[0]['length']=8
  self.assertEqual([(h['pad'],h['beat']) for h in collect_hits(self.arr,{'main':self.pattern},84,8)],[(1,0),(2,1),(1,4),(2,5)])
 def test_slip_and_trim(self):
  self.arr.clips[0].update(start=2.,length=2.,offset=1.)
  self.assertEqual([(h['pad'],h['beat']) for h in collect_hits(self.arr,{'main':self.pattern},84,8)],[(2,2.)])
 def test_mute_and_solo(self):
  self.arr.muted_tracks.add(0)
  self.assertEqual(collect_hits(self.arr,{'main':self.pattern},84,4),[])
 def test_invalid_bpm(self):
  with self.assertRaises(ValueError):collect_hits(self.arr,{'main':self.pattern},0,4)
 def test_missing_sample(self):
  class Fake: samples=[None]*32
  with self.assertRaisesRegex(ValueError,'pads: 1, 2'):bounce_track_city(Fake(),self.arr,{'main':self.pattern},84,'/tmp/never.wav')
if __name__=='__main__':unittest.main()
