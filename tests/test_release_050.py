import sys,unittest,queue
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from toolboxx import App
class Release050(unittest.TestCase):
 def test_nonblocking_midi_flood(self):
  app=App.__new__(App);app.events=queue.Queue(maxsize=2);app.midi_dropped=0
  for i in range(5):app._enqueue_midi(i)
  self.assertEqual(app.midi_dropped,3)
  self.assertEqual(app._drain_midi(1),[0])
  self.assertEqual(app._drain_midi(),[1])
 def test_installer_names_agree(self):
  import json
  root=Path(__file__).resolve().parents[1]
  release=json.loads((root/'release.json').read_text())
  self.assertEqual(release['installer'],f"BOOM_BAP_TOOLBOXX_Setup_{release['build']}.exe")
  self.assertIn('$release.installer',(root/'BUILD_SETUP_WINDOWS.ps1').read_text())
  self.assertIn('OutputBaseFilename={#InstallerBase}',(root/'installer/toolboxx.iss').read_text())
if __name__=='__main__':unittest.main()
