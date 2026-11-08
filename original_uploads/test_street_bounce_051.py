import sys
import tempfile
import unittest
import wave
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app'))
from street_bounce import bounce

class FakeEngine:
    sr = 8000
    def __init__(self, sample=.25): self.sample=sample
    def render(self, n): return [self.sample]*n

class BounceTests(unittest.TestCase):
    def test_stereo_header_and_samples(self):
        with tempfile.TemporaryDirectory() as d:
            result=bounce(FakeEngine(),Path(d)/'test.wav',.1,37)
            with wave.open(result['file'],'rb') as w:
                self.assertEqual((w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes()),(2,2,8000,800))
                self.assertEqual(len(w.readframes(800)),3200)
    def test_clipping_count(self):
        with tempfile.TemporaryDirectory() as d:
            result=bounce(FakeEngine(1.5),Path(d)/'test.wav',.01)
            self.assertEqual(result['clipped_frames'],80)
    def test_nonfinite_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(RuntimeError):bounce(FakeEngine(float('nan')),Path(d)/'test.wav',.01)
    def test_bad_duration(self):
        with self.assertRaises(ValueError):bounce(FakeEngine(),'test.wav',float('inf'))
