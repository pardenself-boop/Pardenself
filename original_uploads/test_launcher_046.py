import sys
import types
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
import toolboxx_launcher

class LauncherTests(unittest.TestCase):
    def test_main_workstation_path(self):
        fake=types.ModuleType('launch_reference')
        fake.main=MagicMock()
        with patch.dict(sys.modules,{'launch_reference':fake}):
            self.assertEqual(toolboxx_launcher.run([]),'workstation')
            fake.main.assert_called_once_with()
    def test_sound_check_path(self):
        fake_tk=types.ModuleType('tkinter')
        root=MagicMock()
        fake_tk.Tk=MagicMock(return_value=root)
        fake_audio=types.ModuleType('audio_smoke_test')
        fake_audio.AudioTest=MagicMock()
        with patch.dict(sys.modules,{'tkinter':fake_tk,'audio_smoke_test':fake_audio}):
            self.assertEqual(toolboxx_launcher.run(['--sound-check']),'sound-check')
            fake_audio.AudioTest.assert_called_once_with(root)
            root.mainloop.assert_called_once_with()
    def test_unknown_args_do_not_hide_workstation(self):
        fake=types.ModuleType('launch_reference')
        fake.main=MagicMock()
        with patch.dict(sys.modules,{'launch_reference':fake}):
            self.assertEqual(toolboxx_launcher.run(['--unknown']),'workstation')
