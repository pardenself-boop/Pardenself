import os,sys,struct,tempfile,unittest,wave
from types import SimpleNamespace
from unittest.mock import Mock
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..','app'))
from toolboxx import Engine
from audio_smoke_test import AudioTest

class PadDeckTests(unittest.TestCase):
 def test_all_32_pads_trigger_pcm_audio(self):
  with tempfile.TemporaryDirectory() as d:
   path=os.path.join(d,'drum.wav')
   with wave.open(path,'wb') as w:
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(48000)
    w.writeframes(struct.pack('<h',12000)*1000)
   e=Engine()
   for i in range(32):
    e.load(i,path);e.trigger(i)
   self.assertEqual(len(e.voices),32)
   self.assertGreater(max(abs(x) for x in e.render(128)),0.01)
 def test_invalid_index_and_wav_rejected(self):
  e=Engine()
  with self.assertRaises(ValueError):e.trigger(32)
  with self.assertRaises(ValueError):e.load(-1,'missing.wav')
 def test_midi_pad_note_range_and_filter(self):
  a=AudioTest.__new__(AudioTest);a.trigger_pad=Mock()
  for note in range(36,68):
   self.assertTrue(a.handle_pad_midi(SimpleNamespace(type='note_on',note=note,velocity=90,channel=2),2))
  self.assertEqual(a.trigger_pad.call_count,32)
  self.assertFalse(a.handle_pad_midi(SimpleNamespace(type='note_on',note=68,velocity=90,channel=2),2))
  self.assertFalse(a.handle_pad_midi(SimpleNamespace(type='note_off',note=36,velocity=0,channel=2),2))
  self.assertFalse(a.handle_pad_midi(SimpleNamespace(type='note_on',note=36,velocity=90,channel=2),1))
 def test_keyboard_release_uses_original_instrument(self):
  a=AudioTest.__new__(AudioTest)
  a.keyboard_held={'a':(60,3),'w':(61,5)}
  a.engine=SimpleNamespace(labbs=SimpleNamespace(note_off=Mock()))
  a.release_keyboard()
  self.assertEqual(a.engine.labbs.note_off.call_count,2)
  self.assertEqual(a.keyboard_held,{})
