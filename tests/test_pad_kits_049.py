import json,os,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from street_pad_kits import save_kit,load_kit
class KitTests(unittest.TestCase):
 def test_round_trip_relative_paths(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);wav=root/'drums'/'kick.wav';wav.parent.mkdir();wav.write_bytes(b'RIFF')
   slots=[None]*32;slots[0]=str(wav)
   dest=root/'kits'/'street.tbkit';save_kit(dest,slots)
   self.assertEqual(load_kit(dest)[0],str(wav.resolve()))
   self.assertEqual(load_kit(dest)[31],None)
   self.assertFalse(Path(dest).with_suffix('.tbkit.tmp').exists())
 def test_reject_wrong_slot_count(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):save_kit(Path(d)/'x.tbkit',[None]*16)
 def test_reject_invalid_format(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'x.tbkit';p.write_text(json.dumps({'format':'other','pads':[None]*32}))
   with self.assertRaises(ValueError):load_kit(p)
 def test_reject_non_wav_entry(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'x.tbkit';p.write_text(json.dumps({'format':'toolboxx.pad-kit.v1','pads':['malware.exe']+[None]*31}))
   with self.assertRaises(ValueError):load_kit(p)
