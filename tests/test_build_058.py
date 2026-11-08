import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'app'))
import verify_release
from cookup_ui import CookUpWindow


class Build058Tests(unittest.TestCase):
    def test_default_orb_exists_before_widgets_and_refresh(self):
        app = MagicMock()
        observed = []
        with patch('cookup_ui.tk.Toplevel'), \
             patch.object(CookUpWindow, '_build', lambda win: observed.append(win.selected_orb)), \
             patch.object(CookUpWindow, 'refresh', lambda win: observed.append(win.selected_orb)):
            CookUpWindow(app)
        self.assertEqual(observed, [1, 1])

    def test_release_rejects_missing_and_fake_executables(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            release = json.loads((ROOT / 'release.json').read_text())
            (root / 'release.json').write_text(json.dumps(release))
            with self.assertRaisesRegex(ValueError, 'Missing'):
                verify_release.verify(root)
            exe = root / 'build' / release['executable'] / (release['executable'] + '.exe')
            exe.parent.mkdir(parents=True)
            exe.write_bytes(b'bad' * 1024)
            with self.assertRaisesRegex(ValueError, 'signature'):
                verify_release.verify(root)

    def test_smoke_test_dispatch(self):
        import toolboxx_launcher
        with patch('startup_check.run', return_value=0) as smoke:
            self.assertEqual(toolboxx_launcher.run(['--smoke-test']), 0)
        smoke.assert_called_once_with()
