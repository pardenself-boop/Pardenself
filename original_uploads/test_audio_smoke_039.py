import sys, unittest, math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from toolboxx import Engine

class AudioSmokeTests(unittest.TestCase):
 def test_silence_is_finite(self):
  e=Engine();audio=e.render(256)
  self.assertEqual(len(audio),256)
  self.assertTrue(all(math.isfinite(x) for x in audio))
 def test_instrument_reaches_master(self):
  e=Engine();e.labbs.note_on(note=48,velocity=.9,labb=3,duration=.5)
  audio=e.render(2048)
  self.assertGreater(max(map(abs,audio)),.001)
  self.assertLessEqual(max(map(abs,audio)),e.labbs.master.ceiling)
 def test_all_notes_off_releases(self):
  e=Engine();e.labbs.note_on(note=60,labb=7,duration=5)
  e.render(512);e.labbs.all_notes_off()
  for _ in range(35):e.render(512)
  self.assertEqual(len(e.labbs.voices),0)

if __name__=='__main__':unittest.main()
