import sys, unittest, tempfile, wave
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from arranger_core import Arranger
from note_lane import NoteLane, Note
from toolboxx import Engine
from track_city_bounce import collect_midi_notes, bounce_track_city

class MidiBounceTests(unittest.TestCase):
 def setup_song(self):
  arr=Arranger(); arr.clips=[dict(track=0,start=0.,length=4.,offset=0.,kind='labb',labb_index=3,note_pattern='bass')]
  lane=NoteLane(); lane.patterns['bass']=[Note(0,48,.9,.5),Note(2,55,.8,.5)]
  return arr,lane
 def test_collect_notes(self):
  arr,lane=self.setup_song(); self.assertEqual([n['pitch'] for n in collect_midi_notes(arr,lane,4)],[48,55])
 def test_muted_track(self):
  arr,lane=self.setup_song();arr.muted_tracks.add(0);self.assertEqual(collect_midi_notes(arr,lane,4),[])
 def test_slip_and_clip_trim(self):
  arr,lane=self.setup_song();arr.clips[0].update(start=1.,length=1.5,offset=1.)
  self.assertEqual([n['pitch'] for n in collect_midi_notes(arr,lane,4)],[55])
 def test_bounce_produces_instrument_audio(self):
  arr,lane=self.setup_song()
  with tempfile.TemporaryDirectory() as d:
   output=Path(d)/'bass.wav';bounce_track_city(Engine(),arr,{},120,str(output),bars=1,note_lane=lane)
   with wave.open(str(output),'rb') as w:
    self.assertEqual(w.getnchannels(),2);self.assertEqual(w.getframerate(),48000)
    self.assertTrue(any(w.readframes(10000)))
 def test_bad_note_fails(self):
  arr,lane=self.setup_song();lane.patterns['bass']=[Note(0,129)]
  with self.assertRaises(ValueError):collect_midi_notes(arr,lane,4)
if __name__=='__main__':unittest.main()
