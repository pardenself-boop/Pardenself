import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app'))
from toolboxx import Engine
from arranger_core import Arranger
from note_lane import NoteLane
from suite_registry import SuiteRouter
from project_io import save_project, load_project, stage_project
from cookup_ui import CookUpWindow


def session():
    engine = Engine()
    pattern = [[False] * 16 for _ in range(32)]
    return SimpleNamespace(engine=engine, labbs=engine.labbs, arr=Arranger(),
                           notes=NoteLane(), suites=SuiteRouter(), bpm=93.5,
                           pattern=pattern, patterns={'main': pattern}, mapping={},
                           playing=True, recording=True, tick_id=None)


class ProjectTests(unittest.TestCase):
    def test_moved_folder_restores_pad_region_and_labb_media(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'song'; root.mkdir()
            wav = root / 'sample.wav'
            shutil.copyfile(Path(__file__).resolve().parents[1] / 'app' / 'AUDIO_TEST.wav', wav)
            app = session(); app.engine.load(31, str(wav))
            app.labbs.crate.load(3, wav, 48)
            app.arr.clips = [dict(id='audio', kind='audio', path=str(wav), track=0,
                                  start=0., length=1., offset=0., name='Region')]
            app.patterns['main'][31][0] = True
            project = root / 'song.tbx.json'; save_project(app, project)
            payload = json.loads(project.read_text())
            self.assertEqual(payload['sample_paths'][31], 'sample.wav')
            self.assertEqual(payload['arranger']['clips'][0]['path'], 'sample.wav')
            moved = Path(folder) / 'moved'; root.rename(moved)
            restored = session(); load_project(restored, moved / project.name)
            self.assertEqual(restored.engine.samples[31], app.engine.samples[31])
            self.assertEqual(restored.labbs.crate.slots[3][:3], app.labbs.crate.slots[3][:3])
            self.assertTrue(restored.patterns['main'][31][0])
            self.assertEqual(restored.notes.serialize(), app.notes.serialize())
            self.assertEqual(restored.bpm, 93.5)
            self.assertIn(str(moved / 'sample.wav'), restored.engine.regions.sources)
            restored.engine.trigger(31)
            self.assertGreater(max(abs(v) for v in restored.engine.render(1024)), 0)
            self.assertFalse(restored.playing)

    def test_missing_media_does_not_replace_current_session(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'project.json'; app = session(); save_project(app, path)
            data = json.loads(path.read_text()); data['sample_paths'][4] = 'gone.wav'
            path.write_text(json.dumps(data)); before = app.arr
            with self.assertRaisesRegex(ValueError, 'Pad 5 audio'):
                load_project(app, path)
            self.assertIs(app.arr, before)
            self.assertTrue(app.playing)
            self.assertTrue(app.recording)

    def test_invalid_tempo_and_pattern_leave_session_unchanged(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'project.json'; app = session(); save_project(app, path)
            valid = json.loads(path.read_text())
            for change in ({'bpm': 0}, {'bpm': 'fast'}, {'patterns': {'main': []}}, {'format': 'future'}):
                data = copy.deepcopy(valid); data.update(change); path.write_text(json.dumps(data))
                with self.assertRaises(ValueError): load_project(app, path)
                self.assertEqual(app.bpm, 93.5)
                self.assertTrue(app.playing)

    def test_atomic_save_failure_keeps_existing_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'project.json'; path.write_text('original')
            with patch('project_io.os.fsync', side_effect=OSError('disk full')):
                with self.assertRaises(OSError): save_project(session(), path)
            self.assertEqual(path.read_text(), 'original')
            self.assertEqual(list(Path(folder).glob('*.tmp')), [])

    def test_legacy_patterns_only_does_not_require_pattern_key(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'project.json'; save_project(session(), path)
            data = json.loads(path.read_text())
            for name in ('format', 'sample_paths', 'pattern'): data.pop(name)
            path.write_text(json.dumps(data))
            self.assertTrue(stage_project(path)['legacy_media'])


class PadUITests(unittest.TestCase):
    def window(self):
        win = CookUpWindow.__new__(CookUpWindow)
        win.app = SimpleNamespace(bank=0, selected_pad=0, engine=Engine(), _refresh=MagicMock())
        win.pad_deck = MagicMock()
        win.pad_deck.winfo_width.return_value = 160
        win.pad_deck.winfo_height.return_value = 160
        win.refresh = MagicMock()
        return win

    def test_both_banks_reach_every_pad(self):
        win = self.window()
        reached = []
        for bank in (0, 1):
            win.app.bank = bank
            for row in range(4):
                for col in range(4):
                    reached.append(win.pad_at(SimpleNamespace(x=col*40+20, y=row*40+20)))
        self.assertEqual(sorted(reached), list(range(32)))
        self.assertEqual(reached[:4], [12, 13, 14, 15])
        self.assertIsNone(win.pad_at(SimpleNamespace(x=-1, y=5)))

    def test_pad_click_triggers_selected_sample(self):
        win = self.window()
        with patch.object(win.app.engine, 'trigger') as trigger:
            win.pad_click(SimpleNamespace(x=20, y=140))
        trigger.assert_called_once_with(0)
        win.refresh.assert_called_once()

    def test_waveform_draws_loaded_pcm_and_empty_state(self):
        win = self.window();win.wave = MagicMock()
        win.wave.winfo_width.return_value = 300; win.wave.winfo_height.return_value = 130
        win.draw_wave()
        self.assertTrue(any('NO SAMPLE' in str(c) for c in win.wave.create_text.call_args_list))
        win.app.engine.samples[0] = ([0., .5, -.5, 0.] * 100, 48000, 'Kick')
        win.wave.reset_mock();win.draw_wave()
        self.assertGreater(win.wave.create_line.call_count, 100)
        self.assertTrue(any('Kick' in str(c) for c in win.wave.create_text.call_args_list))
