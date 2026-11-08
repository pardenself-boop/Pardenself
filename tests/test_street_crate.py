import math
import os
import struct
import sys
import tempfile
import unittest
import wave
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app'))
from labb_engine import LabbEngine
from street_sample_engine import StreetCrate, load_wav

class CrateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.temp.name, 'break.wav')
        with wave.open(self.path, 'wb') as f:
            f.setnchannels(1);f.setsampwidth(2);f.setframerate(48000)
            f.writeframes(b''.join(struct.pack('<h', int(12000 * math.sin(i / 9))) for i in range(4800)))
    def tearDown(self): self.temp.cleanup()
    def test_load_and_pitch(self):
        e = StreetCrate()
        e.load(1, self.path, 60)
        self.assertTrue(e.note_on(1,72))
        e.render(100)
        self.assertAlmostEqual(e.voices[0]['pos'],200)
    def test_release(self):
        e = StreetCrate();e.load(1,self.path)
        e.note_on(1,60);e.note_off(60,1)
        e.render(2000)
        self.assertFalse(e.voices)
    def test_engine_sample_and_oscillator(self):
        e = LabbEngine()
        e.load_sample(1,self.path)
        e.note_on(60,labb=1)
        self.assertTrue(any(abs(v)>0.001 for v in e.render(256)))
        e.note_on(48,labb=3)
        self.assertTrue(any(abs(v)>0.001 for v in e.render(256)))
    def test_invalid_file_does_not_replace_slot(self):
        e = StreetCrate();e.load(1,self.path)
        with self.assertRaises(Exception): e.load(1,'missing.wav')
        self.assertTrue(e.note_on(1,60))
    def test_polyphony_limit(self):
        e=StreetCrate(max_voices=3);e.load(1,self.path)
        for n in range(10): e.note_on(1,60+n)
        self.assertEqual(len(e.voices),3)

if __name__ == '__main__':unittest.main()
