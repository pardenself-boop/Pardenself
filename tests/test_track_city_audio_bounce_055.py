import sys, unittest, tempfile, wave, math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from arranger_core import Arranger
from toolboxx import Engine
from track_city_bounce import bounce_track_city, collect_audio_clips

class AudioBounceTests(unittest.TestCase):
 def make_wav(self,path):
  import array
  samples=array.array('h',[int(12000*math.sin(2*math.pi*220*i/48000)) for i in range(4800)])
  with wave.open(str(path),'wb') as w:
   w.setnchannels(1);w.setsampwidth(2);w.setframerate(48000);w.writeframes(samples.tobytes())
 def test_audio_clip_renders_to_bounce(self):
  with tempfile.TemporaryDirectory() as d:
   source=Path(d)/'source.wav';out=Path(d)/'out.wav';self.make_wav(source)
   arr=Arranger();arr.clips=[dict(track=0,start=0.,length=1.,offset=0.,kind='audio',path=str(source),gain=1.)]
   bounce_track_city(Engine(),arr,{},120,str(out),bars=1)
   with wave.open(str(out),'rb') as w:
    self.assertEqual(w.getnchannels(),2)
    self.assertTrue(any(b for b in w.readframes(4800)))
 def test_muted_audio_is_ignored(self):
  arr=Arranger();arr.clips=[dict(track=0,start=0.,length=1.,kind='audio',path='missing.wav')]
  arr.muted_tracks.add(0)
  self.assertEqual(collect_audio_clips(arr,4),[])
 def test_missing_audio_fails_before_output(self):
  with tempfile.TemporaryDirectory() as d:
   arr=Arranger();arr.clips=[dict(track=0,start=0.,length=1.,kind='audio',path=str(Path(d)/'missing.wav'))]
   out=Path(d)/'out.wav'
   with self.assertRaises(FileNotFoundError):bounce_track_city(Engine(),arr,{},120,str(out),bars=1)
   self.assertFalse(out.exists())
if __name__=='__main__':unittest.main()
