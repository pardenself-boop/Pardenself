import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from street_capture import StreetTap, CrateIndex, safe_filename

class CaptureTests(unittest.TestCase):
 def test_filename_sanitized(self):
  self.assertEqual(safe_filename('../foo:bar'), 'foo_bar.wav')
 def test_crate_persists(self):
  with tempfile.TemporaryDirectory() as root:
   index=CrateIndex(Path(root)/'index.json')
   index.add_site('My Samples','https://example.com/samples')
   index.add_folder(root)
   fresh=CrateIndex(Path(root)/'index.json')
   self.assertEqual(fresh.sites[0]['name'],'My Samples')
   self.assertEqual(fresh.folders,[str(Path(root).resolve())])
 def test_invalid_site_rejected(self):
  with tempfile.TemporaryDirectory() as root:
   idx=CrateIndex(Path(root)/'idx.json')
   with self.assertRaises(ValueError):idx.add_site('x','javascript:alert(1)')
 def test_invalid_recording_settings(self):
  with self.assertRaises(ValueError):StreetTap().start(rate=2)
 def test_sample_directory_listing(self):
  with tempfile.TemporaryDirectory() as root:
   (Path(root)/'drum.wav').write_bytes(b'test')
   (Path(root)/'notes.txt').write_bytes(b'test')
   idx=CrateIndex(Path(root)/'idx.json');idx.add_folder(root)
   self.assertEqual([x.name for x in idx.samples()],['drum.wav'])
if __name__=='__main__':unittest.main()
