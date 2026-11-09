import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock,patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from metronome import Metronome
from toolboxx import Engine, COMMANDS
from track_city_bounce import bounce_track_city
from project_io import save_project, load_project
from test_pad_recording_065 import app_fixture


class ClickAudioTests(unittest.TestCase):
    def test_original_click_is_finite_accented_and_ends(self):
        normal=Metronome();accent=Metronome();normal.trigger();accent.trigger(True)
        a=normal.render(2048,48000);b=accent.render(2048,48000)
        self.assertTrue(all(math.isfinite(v) for v in a+b))
        self.assertGreater(max(map(abs,b)),max(map(abs,a))*1.2)
        self.assertEqual(a[0],0.);self.assertEqual(a[-1],0.)
        self.assertEqual(normal.voices,[])

    def test_click_keeps_its_shape_outside_master_fx(self):
        engine=Engine();engine.mix_rack.process=Mock(side_effect=lambda samples,sr:[0.]*len(samples))
        engine.click(True)
        self.assertGreater(max(map(abs,engine.render(512))),.01)
        engine.clear_clicks();engine.render(4096)
        self.assertEqual(engine.metronome.voices,[])

    def test_monitor_click_is_not_in_offline_wav(self):
        app=app_fixture();app.engine.click(True)
        with tempfile.TemporaryDirectory() as directory:
            result=bounce_track_city(app.engine,app.arr,app.patterns,120,Path(directory)/'silent.wav',bars=1)
        self.assertEqual(result['peak'],0.)
        self.assertEqual(len(app.engine.metronome.voices),1)


class CountInTests(unittest.TestCase):
    def app(self):
        app=app_fixture();app.playing=False;app.count_in_enabled=True;app.metronome_enabled=False
        app._count_in_remaining=0;app._count_in_active=False
        return app

    def test_four_beats_then_first_pattern_step(self):
        app=self.app();app.pattern[0][0]=.6
        app.engine.trigger=Mock();app.engine.click=Mock()
        app.toggle_play()
        for _ in range(15):app.tick()
        self.assertEqual(app.playhead,0.)
        self.assertEqual(app.engine.click.call_count,4)
        self.assertTrue(app.engine.click.call_args_list[0].kwargs['accent'])
        app.engine.trigger.assert_not_called()
        self.assertTrue(app._count_in_active)
        app.tick()
        self.assertFalse(app._count_in_active)
        app.engine.trigger.assert_called_once_with(0,.6)
        self.assertEqual(app.playhead,.25)

    def test_audition_during_final_count_interval_cannot_write_a_step(self):
        app=self.app();app.toggle_play()
        for _ in range(15):app.tick()
        self.assertEqual(app._count_in_remaining,0)
        self.assertTrue(app._count_in_active)
        app.trigger_absolute_pad(0,.4)
        self.assertFalse(any(app.pattern[0]))
        app.tick();app.trigger_absolute_pad(0,.5)
        self.assertTrue(any(app.pattern[0]))

    def test_count_in_does_not_start_when_record_is_disarmed(self):
        app=self.app();app.recording=False;app.toggle_play()
        self.assertFalse(app._count_in_active)
        self.assertEqual(app.playhead,.25)

    def test_stopping_count_in_resets_position_and_clears_monitor(self):
        app=self.app();app.toggle_play();app.toggle_play()
        self.assertEqual(app.playhead,0.)
        self.assertEqual(app._count_in_remaining,0)
        self.assertFalse(app._count_in_active)
        self.assertEqual(app.engine.metronome.voices,[])
        app.toggle_play();self.assertEqual(app._count_in_remaining,15)

    def test_disabling_count_in_resumes_without_another_lead_bar(self):
        app=self.app();app.toggle_play();app.command('COUNT IN TOGGLE')
        self.assertFalse(app._count_in_active)
        app.tick();self.assertEqual(app.playhead,.25)

    def test_metronome_follows_quarter_notes_and_has_learnable_commands(self):
        app=self.app();app.count_in_enabled=False;app.metronome_enabled=True;app.engine.click=Mock()
        app.toggle_play()
        for _ in range(16):app.tick()
        self.assertEqual(app.engine.click.call_count,5)
        self.assertTrue(app.engine.click.call_args.kwargs['accent'])
        self.assertIn('METRONOME TOGGLE',COMMANDS);self.assertIn('COUNT IN TOGGLE',COMMANDS)

    def test_count_in_is_cancelled_when_record_is_disarmed(self):
        app=self.app();app.toggle_play();app.toggle_rec()
        self.assertFalse(app.recording);self.assertFalse(app._count_in_active)
        app.tick();self.assertEqual(app.playhead,.25)


class CountInProjectTests(unittest.TestCase):
    def test_preferences_roundtrip_but_active_count_does_not(self):
        app=app_fixture();app.metronome_enabled=True;app.count_in_enabled=True;app._count_in_active=True
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'click.tbx.json';save_project(app,path)
            loaded=app_fixture();load_project(loaded,path)
            self.assertTrue(loaded.metronome_enabled);self.assertTrue(loaded.count_in_enabled)
            self.assertFalse(loaded._count_in_active)
            data=json.loads(path.read_text());data.pop('transport');path.write_text(json.dumps(data))
            load_project(loaded,path)
            self.assertFalse(loaded.metronome_enabled);self.assertFalse(loaded.count_in_enabled)

    def test_invalid_preference_does_not_replace_current_session(self):
        app=app_fixture()
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'click.tbx.json';save_project(app,path)
            data=json.loads(path.read_text());data['transport']={'count_in':'yes'};path.write_text(json.dumps(data))
            before=app.arr
            with self.assertRaises(ValueError):load_project(app,path)
            self.assertIs(app.arr,before)


class TransportDeadlineTests(unittest.TestCase):
    def test_ui_work_does_not_accumulate_into_tick_interval(self):
        app=app_fixture();app.bpm=120;app._next_tick_time=100.
        with patch('toolboxx.time.monotonic',return_value=100.03):app.schedule_tick()
        app.root.after.assert_called_with(95,app.tick)
        with patch('toolboxx.time.monotonic',return_value=100.15):app.schedule_tick()
        app.root.after.assert_called_with(100,app.tick)

    def test_large_stall_cannot_schedule_a_zero_delay_catchup_storm(self):
        app=app_fixture();app.bpm=120;app._next_tick_time=100.
        with patch('toolboxx.time.monotonic',return_value=105.):app.schedule_tick()
        app.root.after.assert_called_with(125,app.tick)
