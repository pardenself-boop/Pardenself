import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from arranger_core import Arranger
from arranger_ranges import RangeEditor

class RangeTests(unittest.TestCase):
    def setup_range(self,mode='ARR'):
        arr=Arranger();arr.clips=[]
        for track in range(3):arr.clips.append(dict(id=f'c{track}',track=track,start=0.,length=8.,offset=2.,kind='audio',path='source.wav',name=f'Track {track}'))
        arr.set_mode(mode);edit=RangeEditor(arr);edit.set_range(2,4,1,2)
        return arr,edit
    def test_mode_scopes(self):
        for mode,expected in [('MRQ',{'c1','c2'}),('TRK',{'c1'}),('ARR',{'c0','c1','c2'})]:
            arr,edit=self.setup_range(mode)
            self.assertEqual(set(edit.select()),expected)
            self.assertEqual(arr.focus_track,1)
    def test_copy_clips_media_offsets_without_mutating_source(self):
        arr,edit=self.setup_range();before=copy.deepcopy(arr.clips)
        self.assertEqual(edit.copy(),3)
        self.assertEqual(arr.clips,before)
        for clip in edit.clipboard['clips']:
            self.assertEqual((clip['start'],clip['length'],clip['offset']),(0,2,4))
    def test_clear_splits_spanning_clips_preserves_audio_and_undo(self):
        arr,edit=self.setup_range('TRK');before=copy.deepcopy(arr.clips)
        edit.delete();pieces=sorted([c for c in arr.clips if c['track']==1],key=lambda c:c['start'])
        self.assertEqual([(c['start'],c['length'],c['offset']) for c in pieces],[(0,2,2),(4,4,6)])
        self.assertEqual(len({c['id'] for c in arr.clips}),len(arr.clips))
        self.assertEqual(len(arr.history),1);self.assertTrue(arr.undo());self.assertEqual(arr.clips,before)
    def test_duplicate_insert_splits_and_shifts_only_scoped_track(self):
        arr,edit=self.setup_range('TRK');before=copy.deepcopy(arr.clips)
        added=edit.duplicate(insert=True)
        self.assertEqual(len(added),1)
        pieces=sorted([c for c in arr.clips if c['track']==1],key=lambda c:c['start'])
        self.assertEqual([(c['start'],c['length'],c['offset']) for c in pieces],[(0,4,2),(4,2,4),(6,4,6)])
        self.assertEqual([c for c in arr.clips if c['track']==0],[before[0]])
        self.assertEqual((arr.loop_start,arr.loop_end),(4,6))
        arr.undo();self.assertEqual(arr.clips,before);self.assertEqual((arr.loop_start,arr.loop_end),(2,4))
    def test_copy_and_paste_preserve_pattern_and_labb_metadata(self):
        arr,edit=self.setup_range()
        arr.clips[0].update(kind='pattern',pattern_id='drums')
        arr.clips[1].update(kind='labb',labb_index=3,note_pattern='bass')
        edit.copy();ids=edit.paste(12)
        pasted=[c for c in arr.clips if c['id'] in ids]
        self.assertEqual([c['start'] for c in pasted],[12,12,12])
        self.assertEqual(pasted[0]['pattern_id'],'drums');self.assertEqual(pasted[1]['note_pattern'],'bass')
    def test_invalid_range_and_paste_do_not_edit(self):
        arr,edit=self.setup_range();before=copy.deepcopy(arr.clips)
        with self.assertRaises(ValueError):edit.set_range(float('nan'),4)
        edit.copy()
        with self.assertRaises(ValueError):edit.paste(float('inf'))
        self.assertEqual(arr.clips,before)
    def test_empty_delete_is_not_an_undo_step(self):
        arr,edit=self.setup_range();edit.set_range(20,24);self.assertEqual(edit.delete(),0);self.assertFalse(arr.history)

    def test_audio_fades_remain_unchanged_outside_cleared_range(self):
        from audio_regions import region_sample
        arr,edit=self.setup_range('TRK');arr.clips[1].update(fade_in=6.,fade_out=4.)
        original=copy.deepcopy(arr.clips[1]);audio=[.5]*16000
        edit.delete();pieces=[c for c in arr.clips if c['track']==1]
        for beat in (.5,1.5,4.5,6.5,7.5):
            part=next(c for c in pieces if c['start']<=beat<c['start']+c['length'])
            before=region_sample(audio,1000,1000,original,beat*1000,60)
            after=region_sample(audio,1000,1000,part,(beat-part['start'])*1000,60)
            self.assertAlmostEqual(after,before)
