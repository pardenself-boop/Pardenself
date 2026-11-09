import json
import queue
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from pad_patterns import PadTakes, performance_beat, pattern_step, step_velocity
from arrangement_playback import velocity_hits_at, hits_at
from toolboxx import App, Engine
from arranger_core import Arranger
from street_song_bounce import ScheduledEngine, expand_patterns, validate_song
from track_city_bounce import collect_hits, bounce_track_city
from project_io import save_project, load_project
from note_lane import NoteLane
from suite_registry import SuiteRouter
from studio_midi_adapter import MidiControlRouter


def app_fixture():
    app=App.__new__(App);app.engine=Engine();app.labbs=app.engine.labbs
    app.arr=Arranger();app.arr.clips=app.arr.clips[:1]
    app.pattern=[[False]*16 for _ in range(32)];app.patterns={'main':app.pattern}
    app.pad_takes=PadTakes();app.root=Mock();app.status=Mock();app._refresh=Mock()
    app._tick_started=None;app.bpm=120;app.playhead=0.;app.recording=True;app.playing=True
    app.bank=0;app.selected_pad=0;app.tick_id=None;app.step=0
    app.notes=NoteLane();app.suites=SuiteRouter();app.mapping={};app.hardware_midi=MidiControlRouter()
    app.events=queue.Queue()
    return app


class RecordingTests(unittest.TestCase):
    def test_banked_pad_records_velocity_while_auditioning(self):
        app=app_fixture();app.bank=1;app.playhead=1.5
        app.engine.samples[31]=([.2]*1024,48000,'test')
        app.command('BANK PAD 16',velocity=.3)
        self.assertEqual(app.pattern[31][6],.3)
        self.assertEqual(app.engine.voices[0][2],.3)

    def test_no_recording_when_stopped_or_disarmed_or_zero_velocity(self):
        for recording,playing,velocity in ((False,True,.8),(True,False,.8),(True,True,0.)):
            app=app_fixture();app.recording=recording;app.playing=playing
            app.trigger_absolute_pad(0,velocity)
            self.assertFalse(any(app.pattern[0]))

    def test_selected_slipped_clip_records_source_phase(self):
        app=app_fixture();clip=app.arr.clips[0]
        clip.update(start=4.,offset=1.);app.arr.selected={clip['id']};app.playhead=4.5
        app.trigger_absolute_pad(0,.55)
        self.assertEqual(app.pattern[0][6],.55)
        app.playhead=9.;app.trigger_absolute_pad(1,.8)
        self.assertFalse(any(app.pattern[1]))

    def test_transport_clock_uses_audible_beat_not_next_scheduled_step(self):
        app=app_fixture();app._tick_beat=1.;app._tick_started=100.;app.playhead=1.25
        with patch('toolboxx.time.monotonic',return_value=100.01):app.trigger_absolute_pad(0,.4)
        self.assertEqual(app.pattern[0][4],.4)
        self.assertFalse(app.pattern[0][5])
        self.assertAlmostEqual(performance_beat(4,120,0,4,True,100.13,3.75,100),.01)

    def test_take_undo_redo_preserves_previous_hits(self):
        app=app_fixture();app.pattern[0][0]=.9
        app.trigger_absolute_pad(0,.2);app.trigger_absolute_pad(0,.4)
        app.playhead=.25;app.trigger_absolute_pad(1,.7)
        app.toggle_rec()
        self.assertTrue(app.pad_take_history())
        self.assertEqual(app.pattern[0][0],.9);self.assertFalse(app.pattern[1][1])
        self.assertTrue(app.pad_take_history(redo=True))
        self.assertEqual(app.pattern[0][0],.4);self.assertEqual(app.pattern[1][1],.7)

    def test_take_undo_does_not_overwrite_subsequent_step_edit(self):
        app=app_fixture();app.trigger_absolute_pad(0,.4);app.toggle_rec()
        app.pattern[0][0]=.8
        self.assertFalse(app.pad_take_history())
        self.assertEqual(app.pattern[0][0],.8)

    def test_stop_cancels_pending_transport_and_finishes_take(self):
        app=app_fixture();app.trigger_absolute_pad(0,.4);app.tick_id='pending'
        app.toggle_play()
        app.root.after_cancel.assert_called_once_with('pending')
        self.assertIsNone(app.tick_id);self.assertEqual(len(app.pad_takes.history),1)

    def test_undo_while_recording_cannot_change_live_take(self):
        app=app_fixture();app.trigger_absolute_pad(0,.4)
        self.assertFalse(app.pad_take_history())
        self.assertEqual(app.pattern[0][0],.4)

    def test_quantized_next_step_does_not_double_monitor_live_hit(self):
        app=app_fixture();app._tick_started=100.;app._tick_beat=1.;app.playhead=1.25
        app.engine.samples[0]=([.1]*1024,48000,'test')
        with patch('toolboxx.time.monotonic',return_value=100.08):app.trigger_absolute_pad(0,.4)
        self.assertEqual(app.pattern[0][5],.4)
        self.assertEqual(len(app.engine.voices),1)
        app.tick()
        self.assertEqual(len(app.engine.voices),1)
        app.playhead=1.25;app.tick()
        self.assertEqual(len(app.engine.voices),2)

    def test_monitor_suppression_preserves_other_pattern_on_same_pad(self):
        app=app_fixture();app.pattern[0][0]=.4
        other=[[False]*16 for _ in range(32)];other[0][0]=.7
        app.patterns['other']=other;app.arr.clips.append(dict(app.arr.clips[0],id='other',pattern_id='other'))
        self.assertEqual(velocity_hits_at(app.arr.clips,app.patterns,0,excluded_steps={('main',0,0)}),[(0,.7)])


class VelocityPlaybackTests(unittest.TestCase):
    def test_boolean_and_numeric_steps_share_playback_interface(self):
        app=app_fixture();app.pattern[0][0]=True;app.pattern[1][0]=.25
        self.assertEqual(velocity_hits_at(app.arr.clips,app.patterns,0),[(0,1.),(1,.25)])
        self.assertEqual(hits_at(app.arr.clips,app.patterns,0),[0,1])
        self.assertEqual(pattern_step(3.99),0)

    def test_overlapping_clips_match_live_and_offline_strength(self):
        app=app_fixture();app.pattern[0][0]=.2
        other=[[False]*16 for _ in range(32)];other[0][0]=.8
        app.patterns['other']=other
        app.arr.clips.append(dict(app.arr.clips[0],pattern_id='other',id='other'))
        self.assertEqual(velocity_hits_at(app.arr.clips,app.patterns,0),[(0,.8)])
        self.assertEqual(collect_hits(app.arr,app.patterns,120,4),[{'pad':1,'beat':0.,'velocity':.8}])

    def test_scheduled_renderer_delivers_strength_to_real_engine(self):
        engine=Engine();engine.samples[0]=([.1]*1024,48000,'test')
        render=ScheduledEngine(engine,[{'pad':1,'beat':0,'velocity':.25}],120)
        self.assertGreater(max(map(abs,render.render(32))),0)
        self.assertEqual(engine.voices[0][2],.25)

    def test_bounce_keeps_soft_and_loud_hits_distinct(self):
        app=app_fixture();app.engine.samples[0]=([.1]*512,48000,'test')
        with tempfile.TemporaryDirectory() as directory:
            app.pattern[0][0]=.2
            soft=bounce_track_city(app.engine,app.arr,app.patterns,120,Path(directory)/'soft.wav',bars=1)
            app.pattern[0][0]=1.
            loud=bounce_track_city(app.engine,app.arr,app.patterns,120,Path(directory)/'loud.wav',bars=1)
            self.assertLess(soft['peak'],loud['peak']*.4)

    def test_invalid_velocities_are_rejected(self):
        for value in (-.1,1.1,float('nan'),'loud'):
            with self.assertRaises(ValueError):step_velocity(value)
            with self.assertRaises(ValueError):validate_song({'hits':[{'pad':1,'beat':0,'velocity':value}]})


class VelocityProjectTests(unittest.TestCase):
    def test_project_roundtrip_preserves_velocities_and_reads_v2(self):
        app=app_fixture();app.pattern[0][0]=.31;app.pattern[1][2]=True
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'recorded.tbx.json';save_project(app,path)
            restored=app_fixture();load_project(restored,path)
            self.assertEqual(restored.pattern[0][0],.31)
            self.assertIs(restored.pattern[1][2],True)
            self.assertEqual(restored.pad_takes.history,[])
            data=json.loads(path.read_text());data['format']='toolboxx.project.v2';data['version']='2.0'
            data['patterns']['main'][0][0]=True;data['pattern'][0][0]=True
            path.write_text(json.dumps(data));load_project(restored,path)
            self.assertIs(restored.pattern[0][0],True)
